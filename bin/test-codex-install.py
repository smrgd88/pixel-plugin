#!/usr/bin/env python3
"""Exercise a local Codex plugin cache without changing user configuration.

Requires Codex CLI 0.160.0 and real Aseprite. --model-workflow additionally
runs a natural-language turn; the default checks installation and real MCP calls.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
REQUEST_ID = 'io.github.smrgd88.pixel-mcp/request_id'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def user_state():
    home = Path.home()
    paths = [home/'.codex/config.toml', home/'.agents/plugins/marketplace.json',
             home/'.config/pixel-mcp/config.json']
    return {str(p): digest(p) if p.is_file() else None for p in paths}


def toml(value):
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k)+'='+toml(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ','.join(toml(v) for v in value) + ']'
    if isinstance(value, bool):
        return str(value).lower()
    return json.dumps(value)


class Server:
    def __init__(self, codex, cwd, overrides, env, output):
        command = [codex]
        for key, value in overrides.items():
            command += ['-c', key+'='+toml(value)]
        command += ['app-server']
        self.log = (output/'stderr.log').open('w')
        self.process = subprocess.Popen(command, cwd=cwd, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log, text=True)
        self.queue = queue.Queue()
        self.events = []
        self.counter = 0
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for line in self.process.stdout:
                self.queue.put(json.loads(line))
        except Exception as error:
            self.queue.put(error)
        finally:
            self.queue.put(EOFError('app-server stdout closed'))

    def receive(self, timeout):
        message = self.queue.get(timeout=timeout)
        if isinstance(message, Exception):
            raise message
        self.events.append(message)
        # Persist progress so interrupted/failed test turns remain auditable.
        with (Path(self.log.name).parent/'events.jsonl').open('a') as log:
            log.write(json.dumps(message)+'\n')
        # No approval/elicitation is silently accepted by the test driver.
        if 'method' in message and 'id' in message:
            self.process.stdin.write(json.dumps({'id': message['id'], 'error': {
                'code': -32601, 'message': 'Interactive requests are not allowed in this test'}})+'\n')
            self.process.stdin.flush()
        return message

    def request(self, method, params):
        self.counter += 1
        self.process.stdin.write(json.dumps({'id': self.counter, 'method': method,
                                            'params': params})+'\n')
        self.process.stdin.flush()
        deadline = time.monotonic()+60
        while time.monotonic() < deadline:
            response = self.receive(max(0.1, deadline-time.monotonic()))
            if response.get('id') == self.counter and 'method' not in response:
                if 'error' in response:
                    raise RuntimeError(response['error'])
                return response['result']
        raise TimeoutError(method)

    def close(self, output):
        self.process.stdin.close()
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdout.close()
        self.log.close()
        (output/'events.json').write_text(json.dumps(self.events, indent=2)+'\n')


def inspect(aseprite, path):
    result = subprocess.check_output([str(aseprite), '--batch', str(path),
                    '--script', str(ROOT/'bin/inspect-sprite.lua')], text=True)
    return json.loads(result)


def verify_sprite(aseprite, path, size, colors):
    result = inspect(aseprite, path)
    assert (result['width'], result['height']) == (size, size), path
    assert result['frames'] == [150, 100], result['frames']
    for frame, color in enumerate(colors, 1):
        pixels = [c['pixels'].get('2,3') for layer in result['layers'] for c in layer['cels']
                  if c['frame'] == frame]
        assert color in pixels, (path, frame, pixels)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path, required=True)
    parser.add_argument('--codex', default='codex')
    parser.add_argument('--output', type=Path, default=ROOT/'test-outputs/codex-install')
    parser.add_argument('--model-workflow', action='store_true')
    args = parser.parse_args()
    aseprite = args.aseprite.resolve(strict=True)
    output = args.output.resolve() / ('run-'+uuid.uuid4().hex[:10])
    output.mkdir(parents=True)
    fixture = output/'fixture with spaces'
    package = fixture/'package'
    package.mkdir(parents=True)
    # Copy only Git-tracked distribution files, never the working .git or test outputs.
    for name in subprocess.check_output(['git','ls-files'], cwd=ROOT, text=True).splitlines():
        if name == 'AGENTS.md':
            continue  # Routing must come from the installed skills, not repo instructions.
        source = ROOT/name
        if source.is_file():
            target = package/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    subprocess.run(['git','init','-q',str(fixture)], check=True)
    market = 'pixel-install-spike-'+output.name
    plugin_id = 'pixel-plugin@'+market
    catalog = fixture/'.agents/plugins/marketplace.json'
    catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps({'name': market, 'plugins': [{'name': 'pixel-plugin',
        'source': {'source':'local','path':'./package'},
        'policy': {'installation':'AVAILABLE','authentication':'ON_USE'},
        'category': 'Productivity'}]}, indent=2)+'\n')
    config = output/'aseprite.json'
    config.write_text(json.dumps({'aseprite_path': str(aseprite), 'temp_dir': str(output/'sprites'),
        'snapshot_dir': str(output/'snapshots'), 'enable_history': False, 'log_level':'error'}))
    env = dict(os.environ)
    env['PIXEL_MCP_CONFIG'] = str(config)
    env.pop('PIXEL_MCP_BINARY', None)
    overrides = {'marketplaces': {market:{'source':str(fixture),'source_type':'local'}},
        'plugins': {plugin_id:{'enabled':True,'mcp_servers':{'aseprite':{'default_tools_approval_mode':'approve'}}}}, 'mcp_servers': {},
        'projects': {str(fixture):{'trust_level':'trusted'}},
        'features': {'remote_plugin':False,'apps':False}}
    import tomllib  # Only the host model-workflow runner needs Python 3.11+.
    user_config = Path.home()/'.codex/config.toml'
    if user_config.is_file():
        existing = tomllib.loads(user_config.read_text())
        for key in existing.get('plugins', {}):
            overrides['plugins'][key] = {'enabled':False}
        for key in existing.get('mcp_servers', {}):
            overrides['mcp_servers'][key] = {'enabled':False}
    # Disable implicit personal/bundled plugins and standalone user skills as well.
    before = user_state()
    calls = []
    expected = json.loads((ROOT/'config/mcp-contract.json').read_text())['tools']
    cache_roots = []
    report = {'base_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT,
             text=True).strip(), 'codex': subprocess.check_output([args.codex,'--version'],
             text=True).strip(), 'aseprite': subprocess.check_output([str(aseprite),'--version'],
             text=True).strip(), 'marketplace':market, 'model_workflow':args.model_workflow, 'result':'FAIL'}
    try:
        bootstrap = output/'bootstrap'
        bootstrap.mkdir()
        server = Server(args.codex, fixture, overrides, env, bootstrap)
        try:
            server.request('initialize', {'clientInfo':{'name':'pixel-install-test','version':'1'},
                            'capabilities':{'experimentalApi':True}})
            inventory = server.request('plugin/list', {'cwds':[str(fixture)],
                        'marketplaceKinds':['local'],'forceRefetch':False})
            for entry in inventory.get('marketplaces', []):
                for plugin in entry.get('plugins', []):
                    if plugin['id'] != plugin_id:
                        overrides['plugins'][plugin['id']] = {'enabled':False}
            skills = server.request('skills/list', {'cwds':[str(fixture)],'forceReload':True})
            overrides['skills'] = {'config':[{'path':str(Path(x['path']).parent),'enabled':False}
                for d in skills['data'] for x in d['skills']
                if not x.get('pluginId') and x.get('scope') == 'user']}
        finally:
            server.close(bootstrap)
        for phase in ['installed', 'restart', 'source-update']:
            if phase == 'source-update':
                # Claude compatibility identity and Codex metadata must share a version.
                for relative in ['.codex-plugin/plugin.json','.claude-plugin/plugin.json']:
                    manifest = package/relative
                    value = json.loads(manifest.read_text())
                    value['version'] = '0.5.1'
                    manifest.write_text(json.dumps(value, indent=2)+'\n')
            phase_output = output/phase
            phase_output.mkdir()
            server = Server(args.codex, fixture, overrides, env, phase_output)
            try:
                server.request('initialize', {'clientInfo':{'name':'pixel-install-test','version':'1'},
                                'capabilities':{'experimentalApi':True}})
                inventory = server.request('plugin/list', {'cwds':[str(fixture)],'marketplaceKinds':['local'],'forceRefetch':False})
                (phase_output/'plugins.json').write_text(json.dumps(inventory,indent=2))
                skills = server.request('skills/list', {'cwds':[str(fixture)],'forceReload':True})
                (phase_output/'skills.json').write_text(json.dumps(skills,indent=2))
                pixel = [x for d in skills['data'] for x in d['skills']
                         if x['enabled'] and x['name'].startswith('pixel-plugin:')]
                assert len(pixel)==4 and all(x['pluginId']==plugin_id for x in pixel), pixel
                cache = Path(pixel[0]['path']).parents[2]
                assert cache != package and all(Path(x['path']).is_relative_to(cache) for x in pixel)
                cache_roots.append(str(cache))
                expected_version = json.loads((ROOT/'.codex-plugin/plugin.json').read_text())['version'] if phase=='source-update' else json.loads((package/'.codex-plugin/plugin.json').read_text())['version']
                assert json.loads((cache/'.codex-plugin/plugin.json').read_text())['version']==expected_version
                for rel in ['bin/pixel-mcp','config/codex-mcp.json','config/mcp-source.json'] + [str(p.relative_to(ROOT)) for p in (ROOT/'bin').glob('pixel-mcp-*') if p.is_file()]:
                    assert digest(cache/rel)==digest(ROOT/rel), rel
                source_pin = json.loads((ROOT/'config/mcp-source.json').read_text())['commit']
                selected_version = subprocess.check_output([str(cache/'bin/pixel-mcp'),'--version'],env=env,text=True)
                assert source_pin in selected_version,selected_version
                subprocess.run([str(cache/'bin/pixel-mcp'),'--health'], env=env,
                               stdout=subprocess.PIPE, check=True)
                thread = server.request('thread/start', {'cwd':str(fixture),'ephemeral':True,
                    'approvalPolicy':'never','sandbox':'workspace-write','experimentalRawEvents':False})
                tid = thread['thread']['id']
                status = server.request('mcpServerStatus/list', {'threadId':tid,'limit':100})
                connected = [x for x in status['data'] if x['runtimeStatus']=='connected']
                assert len(connected)==1 and connected[0]['name']=='aseprite', status
                tools = connected[0]['tools']
                assert set(tools)=={x['name'] for x in expected}
                for tool in expected:
                    for key in ['inputSchema','outputSchema']:
                        assert tools[tool['name']].get(key)==tool.get(key), (tool['name'],key)
                (phase_output/'skills.json').write_text(json.dumps(skills,indent=2))
                (phase_output/'mcp-status.json').write_text(json.dumps(status,indent=2))
                if phase != 'installed':
                    result = server.request('mcpServer/tool/call', {'threadId':tid,'server':'aseprite',
                        'tool':'get_sprite_info','arguments':{'sprite_path':str(output/'artifacts/protocol.aseprite')}})
                    assert not result.get('isError')
                    print('PASS:',phase,'cache/health/56 schemas/reconnected sprite',flush=True)
                    continue
                def call(name, **arguments):
                    value = server.request('mcpServer/tool/call', {'threadId':tid,'server':'aseprite',
                                           'tool':name,'arguments':arguments})
                    calls.append({'name':name,'arguments':arguments,'result':value})
                    return value
                def ok(name, **arguments):
                    value = call(name, **arguments)
                    assert not value.get('isError'), value
                    assert value['_meta'][REQUEST_ID]
                    return value['structuredContent']
                sprite = ok('create_canvas',width=16,height=16,color_mode='rgb')['file_path']
                layer = ok('get_sprite_info',sprite_path=sprite)['layers'][0]
                ok('draw_pixels',sprite_path=sprite,layer_name=layer,frame_number=1,
                   pixels=[{'x':2,'y':3,'color':'#FF0000'}])
                ok('add_frame',sprite_path=sprite,duration_ms=100)
                ok('set_frame_duration',sprite_path=sprite,frame_number=1,duration_ms=150)
                ok('draw_pixels',sprite_path=sprite,layer_name=layer,frame_number=2,
                   pixels=[{'x':2,'y':3,'color':'#00FF00'}])
                art = output/'artifacts'
                art.mkdir()
                saved = ok('save_as',sprite_path=sprite,output_path=str(art/'protocol.aseprite'))['file_path']
                for fmt, frame in [('png',1),('gif',0)]:
                    ok('export_sprite',sprite_path=saved,output_path=str(art/('protocol.'+fmt)),
                       format=fmt,frame_number=frame)
                ok('export_spritesheet',sprite_path=saved,output_path=str(art/'protocol-sheet.png'),
                   layout='horizontal',padding=0,include_json=True)
                failure = call('get_sprite_info',sprite_path=str(art/'missing.aseprite'))
                assert failure['isError'] and 'structuredContent' not in failure
                error = json.loads(failure['content'][0]['text'])
                assert error['error']['code']=='not_found'
                assert error['request_id']==failure['_meta'][REQUEST_ID]
                before_sprite = digest(Path(saved))
                assert ok('flatten_layers',sprite_path=saved,dry_run=True)['warnings']
                assert digest(Path(saved))==before_sprite
                verify_sprite(aseprite,Path(saved),16,['#FF0000FF','#00FF00FF'])
                verify_sprite(aseprite,art/'protocol.gif',16,['#FF0000FF','#00FF00FF'])
                metadata = json.loads((art/'protocol-sheet.json').read_text())
                frames = metadata['frames']
                frames = list(frames.values()) if isinstance(frames,dict) else frames
                assert [f['duration'] for f in frames]==[150,100]
                print('PASS: installed cache, 4 skills, 56 schemas, 12 MCP calls, native/GIF/JSON pixels and timing',flush=True)
                if args.model_workflow:
                    prompt = ('Use the installed Pixel Plugin to create a 32x32 RGB sprite with a red pixel at (2,3). '
                      'Add a second frame of 100 ms with a blue pixel at (2,3). Set the first frame to 150 ms. '
                      f'Save {art}/model.aseprite and export {art}/model.gif and {art}/model-sheet.png with JSON. '
                      'Read the installed creator, animator and exporter guides and verify outputs. '
                      'Use only aseprite MCP tools for artwork; do not edit settings or use shell to draw/export.')
                    server.request('turn/start', {'threadId':tid,
                        'input':[{'type':'text','text':prompt}],'approvalPolicy':'never'})
                    deadline = time.monotonic()+300
                    while time.monotonic() < deadline:
                        try:
                            event = server.receive(min(20,deadline-time.monotonic()))
                        except queue.Empty:
                            continue
                        if event.get('method')=='turn/completed':
                            assert event['params']['turn']['status']=='completed',event
                            break
                    else:
                        raise TimeoutError('natural-language workflow')
                    verify_sprite(aseprite,art/'model.aseprite',32,['#FF0000FF','#0000FFFF'])
                    verify_sprite(aseprite,art/'model.gif',32,['#FF0000FF','#0000FFFF'])
                    model_frames = json.loads((art/'model-sheet.json').read_text())['frames']
                    model_frames = list(model_frames.values()) if isinstance(model_frames,dict) else model_frames
                    assert [x['duration'] for x in model_frames]==[150,100]
                    print('PASS: natural-language Codex workflow, independently verified native/GIF/JSON',flush=True)
            finally:
                server.close(phase_output)
        assert cache_roots[0]==cache_roots[1]==cache_roots[2]
        report.update({'result':'PASS','cache_roots':cache_roots,'protocol_calls':len(calls), 'source_changes_do_not_refresh_cache':True,
                       'explicit_reinstall_verified':False,
                       'user_settings_unchanged':user_state()==before})
        assert report['user_settings_unchanged']
    finally:
        (output/'calls.json').write_text(json.dumps(calls,indent=2)+'\n')
        (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
        assert user_state()==before,'User settings changed; no automatic restoration attempted'
    print('Evidence:',output)


if __name__ == '__main__':
    main()
