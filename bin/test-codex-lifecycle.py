#!/usr/bin/env python3
"""Run in an isolated OS user/container: explicit Codex plugin mutations are tested.

This writes the selected user's Codex configuration. Never run against a personal
Codex home. The supplied empty home guard is mandatory; no authentication is needed.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

spec = importlib.util.spec_from_file_location('install_test',Path(__file__).with_name('test-codex-install.py'))
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--aseprite',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--isolated-home',type=Path,required=True)
    parser.add_argument('--codex',default='codex')
    args=parser.parse_args()
    assert Path('/.dockerenv').exists(),'This mutation test must run inside a disposable Docker container'
    home=Path.home().resolve()
    assert home==args.isolated_home.resolve(),'Home does not match the explicitly isolated OS user'
    assert not (home/'.codex').exists(),'Refusing to mutate an existing Codex home'
    assert not (home/'.agents/plugins/marketplace.json').exists(),'Refusing an existing marketplace'
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    fixture=Path('/work/lifecycle fixture');fixture.mkdir(parents=True,exist_ok=False)
    package=fixture/'package';shutil.copytree(args.package,package)
    market='pixel-lifecycle-'+uuid.uuid4().hex[:8];plugin_id='pixel-plugin@'+market
    catalog=fixture/'.agents/plugins/marketplace.json';catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps({'name':market,'plugins':[{'name':'pixel-plugin','source':{'source':'local','path':'./package'},'policy':{'installation':'AVAILABLE','authentication':'ON_USE'},'category':'Productivity'}]}))
    config=Path('/work/aseprite.json');config.write_text(json.dumps({'aseprite_path':str(args.aseprite),'temp_dir':'/work/sprites','snapshot_dir':'/work/snapshots','enable_history':False,'log_level':'error'}))
    env=dict(os.environ);env['PIXEL_MCP_CONFIG']=str(config);env.pop('PIXEL_MCP_BINARY',None)
    records=[]
    def cli(label,*argv):
        r=subprocess.run([args.codex,*argv],cwd=fixture,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
        (output/(label+'.stdout')).write_text(r.stdout);(output/(label+'.stderr')).write_text(r.stderr)
        assert r.returncode==0,(label,r.stderr)
        value=json.loads(r.stdout);records.append({'phase':label,'result':value});print('PASS:',label,flush=True);return value
    def runtime(label,expect_plugin=True,manual=False):
        phase=output/label;phase.mkdir()
        server=install.Server(args.codex,fixture,{'features':{'remote_plugin':False,'apps':False}},env,phase)
        try:
            server.request('initialize',{'clientInfo':{'name':'pixel-lifecycle','version':'1'},'capabilities':{'experimentalApi':True}})
            skills=server.request('skills/list',{'cwds':[str(fixture)],'forceReload':True})
            pixel=[s for d in skills['data'] for s in d['skills'] if s['enabled'] and s.get('pluginId')==plugin_id]
            assert len(pixel)==(4 if expect_plugin else 0),pixel
            t=server.request('thread/start',{'cwd':str(fixture),'ephemeral':True,'approvalPolicy':'never','sandbox':'workspace-write','experimentalRawEvents':False})['thread']['id']
            status=server.request('mcpServerStatus/list',{'threadId':t,'limit':100})
            connected=[s for s in status['data'] if s['runtimeStatus']=='connected']
            assert len(connected)==(1 if expect_plugin or manual else 0),status
            if connected:
                s=connected[0];assert s['name']=='aseprite' and len(s['tools'])==56,s
                assert s['pluginId']==(None if manual else plugin_id),s['pluginId']
                w=server.request('mcpServer/tool/call',{'threadId':t,'server':'aseprite','tool':'create_canvas','arguments':{'width':8,'height':8,'color_mode':'rgb'}})
                assert not w.get('isError'),w
                sprite=w['structuredContent']['file_path'];assert Path(sprite).is_file()
                records.append({'phase':label,'pluginId':s['pluginId'],'skills':len(pixel),'tools':len(s['tools']),'sprite':sprite})
            (phase/'skills.json').write_text(json.dumps(skills,indent=2));(phase/'mcp-status.json').write_text(json.dumps(status,indent=2))
            print('PASS:',label,'runtime',flush=True)
        finally:server.close(phase)
    cli('marketplace-add','plugin','marketplace','add',str(fixture),'--json')
    first=cli('install','plugin','add',plugin_id,'--json');oldcache=Path(first['installedPath']);assert oldcache.is_dir()
    runtime('installed')
    cli('remove','plugin','remove',plugin_id,'--json');assert not oldcache.exists()
    runtime('removed',False)
    reinstall=cli('reinstall','plugin','add',plugin_id,'--json');assert reinstall['pluginId']==plugin_id
    runtime('reinstalled')
    for rel in ['.claude-plugin/plugin.json','.codex-plugin/plugin.json']:
        p=package/rel;v=json.loads(p.read_text());v['version']='0.5.1';p.write_text(json.dumps(v,indent=2))
    upgraded=cli('upgrade','plugin','add',plugin_id,'--json');newcache=Path(upgraded['installedPath'])
    assert upgraded['pluginId']==plugin_id and newcache!=oldcache,(first,upgraded)
    assert json.loads((newcache/'.codex-plugin/plugin.json').read_text())['version']=='0.5.1'
    assert install.digest(newcache/'bin/pixel-mcp-linux-amd64')==install.digest(package/'bin/pixel-mcp-linux-amd64')
    runtime('upgraded')
    # Add a real manual server with the same name, then inspect which one the host selected.
    userfile=home/'.codex/config.toml';saved=userfile.read_text()
    manual_config='\n[mcp_servers.aseprite]\ncommand = '+json.dumps(str(package/'bin/pixel-mcp'))+'\nenv_vars = ["PIXEL_MCP_CONFIG"]\n'
    userfile.write_text(saved+manual_config)
    runtime('manual-conflict',manual=True)
    # This is an isolated user's test-owned configuration, with no concurrent actors.
    userfile.write_text(saved)
    runtime('manual-cleared')
    cli('final-remove','plugin','remove',plugin_id,'--json');runtime('final-removed',False)
    cli('marketplace-remove','plugin','marketplace','remove',market,'--json')
    remaining = home/'.codex/plugins/cache'/market
    assert not any(p.is_file() or p.is_symlink() for p in remaining.rglob('*')),remaining
    assert not newcache.exists()
    # Codex may retain empty marketplace parents after deleting all plugin payloads.
    summary={'result':'PASS','pluginId':plugin_id,'codex':subprocess.check_output([args.codex,'--version'],text=True).strip(),'aseprite':subprocess.check_output([str(args.aseprite),'--version'],text=True).strip(),'installedPath':str(oldcache),'upgradedPath':str(newcache),'phases':records}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS: complete lifecycle, same-ID upgrade, manual precedence and plugin recovery, cache cleanup',flush=True)


if __name__=='__main__':main()
