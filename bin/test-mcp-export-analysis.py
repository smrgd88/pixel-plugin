#!/usr/bin/env python3
"""Legacy/sequence result compatibility and optional real export/reference tests."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('client', ROOT / 'bin/mcp-client.py')
client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client_module)
TOOLS = {t['name']: t for t in json.loads((ROOT / 'config/mcp-contract.json').read_text())['tools']}


class ExportContract(unittest.TestCase):
    def test_optional_files_and_decoder(self):
        old = {'exported_path': '/tmp/a.png', 'file_size': 123}
        sequence = dict(old, exported_path='/tmp/a_0001.png', files=[
            {'path': '/tmp/a_0001.png', 'file_size': 123, 'frame_number': 1},
            {'path': '/tmp/a_0002.png', 'file_size': 234, 'frame_number': 2}])
        validator = Draft202012Validator(TOOLS['export_sprite']['outputSchema'])
        c = client_module.Client.__new__(client_module.Client)
        for payload in [old, dict(old, files=None), sequence]:
            validator.validate(payload)
            for structured in [False, True]:
                wire = {'content': [{'type': 'text', 'text': json.dumps(payload)}]}
                if structured:
                    wire['structuredContent'] = payload
                with self.subTest(payload=payload, structured=structured):
                    with patch.object(c, 'request', return_value=wire):
                        self.assertEqual(c.call('export_sprite', {}), payload)
        bad = copy.deepcopy(sequence)
        del bad['files'][1]['frame_number']
        with self.assertRaises(ValidationError):
            validator.validate(bad)
        with patch.object(c, 'request', return_value={'isError': True, 'structuredContent': sequence}):
            with self.assertRaises(RuntimeError):
                c.call('export_sprite', {})


def live(aseprite, output):
    aseprite = str(aseprite.resolve(strict=True))
    with tempfile.TemporaryDirectory(prefix='pixel-export-analysis-') as tmp:
        out = output.resolve() if output else Path(tmp) / 'artifacts'
        out.mkdir(parents=True, exist_ok=True)
        config = Path(tmp) / 'config.json'
        temp_root = out / 'server-temp'
        config.write_text(json.dumps({'aseprite_path': aseprite, 'temp_dir': str(temp_root), 'log_level': 'error'}))
        env = dict(os.environ, PIXEL_MCP_CONFIG=str(config)); env.pop('PIXEL_MCP_BINARY', None)
        c = client_module.Client([str(ROOT / 'bin/pixel-mcp')], env)
        calls = []
        def call(name, **args):
            Draft202012Validator(TOOLS[name]['inputSchema']).validate(args)
            wire = c.request('tools/call', {'name': name, 'arguments': args})
            calls.append({'name': name, 'arguments': args, 'wire': wire})
            assert not wire.get('isError'), wire
            result = wire['structuredContent']
            assert json.loads('\n'.join(x['text'] for x in wire['content'] if x['type'] == 'text')) == result
            Draft202012Validator(TOOLS[name]['outputSchema']).validate(result)
            return result
        def reject(name, **args):
            wire = c.request('tools/call', {'name': name, 'arguments': args})
            calls.append({'name': name, 'arguments': args, 'wire': wire})
            assert wire.get('isError'), wire
            return wire
        def inspect(path):
            # Aseprite otherwise auto-loads neighboring numbered images (including stale files).
            single = ['--oneframe'] if Path(path).suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp'] else []
            result = subprocess.check_output([aseprite, '--batch', *single, str(path), '--script', str(ROOT / 'bin/inspect-sprite.lua')], text=True, timeout=30)
            return json.loads(result)
        def pixels(path):
            info = inspect(path)
            return {xy: color for layer in info['layers'] for cel in layer['cels']
                    for xy, color in (cel['pixels'].items() if isinstance(cel['pixels'], dict) else [])}
        def lua(path, code):
            script = Path(tmp) / 'fixture.lua'; script.write_text(code)
            subprocess.run([aseprite, '--batch', str(path), '--script', str(script)], capture_output=True, check=True, timeout=30)
        def unchanged(path, before, mode):
            assert path.read_bytes() == before
            assert stat.S_IMODE(path.stat().st_mode) == mode
        try:
            assert c.tools() == sorted(TOOLS.values(), key=lambda t: t['name'])
            source = Path(call('create_canvas', width=8, height=8, color_mode='rgb')['file_path'])
            # Fixture-only Lua establishes grouped, hidden and offset layers with known pixels.
            lua(source, '''local s=app.activeSprite
local base=s.layers[1];base.name="Base"
local im=Image(8,8,ColorMode.RGB);im:clear(app.pixelColor.rgba(255,0,0,255));s:newCel(base,1,im)
s:newFrame(1);local blue=Image(8,8,ColorMode.RGB);blue:clear(app.pixelColor.rgba(0,0,255,255));base:cel(2).image=blue
local group=s:newGroup();group.name="Group";base.parent=group
local top=s:newLayer();top.parent=group;top.name="Offset"
local dot=Image(1,1,ColorMode.RGB);dot:clear(app.pixelColor.rgba(0,255,0,255));s:newCel(top,1,dot,Point(2,3))
local hidden=s:newLayer();hidden.name="Hidden";hidden.isVisible=false
local white=Image(8,8,ColorMode.RGB);white:clear(app.pixelColor.rgba(255,255,255,255));s:newCel(hidden,1,white)
s:saveAs(s.filename)''')
            original = source.read_bytes()
            expected1 = {f'{x},{y}': '#00FF00FF' if (x,y)==(2,3) else '#FF0000FF' for y in range(8) for x in range(8)}
            expected2 = {f'{x},{y}': '#0000FFFF' for y in range(8) for x in range(8)}
            for fmt in ['png', 'bmp', 'jpg']:
                base = out / ('walk007.' + fmt); base.write_bytes(b'existing-base')
                stale = out / ('walk007_0003.' + fmt); stale.write_bytes(b'old-extra-frame')
                result = call('export_sprite', sprite_path=str(source), output_path=str(base), format=fmt, frame_number=0)
                files = result['files']
                assert [f['path'] for f in files] == [str(out / f'walk007_{i:04d}.{fmt}') for i in [1,2]]
                assert [f['frame_number'] for f in files] == [1,2]
                assert all(Path(f['path']).stat().st_size == f['file_size'] > 0 for f in files)
                assert (result['exported_path'], result['file_size']) == (files[0]['path'], files[0]['file_size'])
                if fmt != 'jpg':
                    assert pixels(files[0]['path']) == expected1
                    assert pixels(files[1]['path']) == expected2
                else:
                    assert all(Path(f['path']).read_bytes().startswith(b'\xff\xd8') for f in files)
                    assert all(inspect(f['path'])['width'] == 8 for f in files)
                assert base.read_bytes()==b'existing-base' and stale.read_bytes()==b'old-extra-frame'
                assert source.read_bytes()==original
            print('PASS: PNG/BMP/JPG ordered sequences, digit suffix naming, sizes, grouped/offset/hidden pixels, base/stale/source preservation', flush=True)
            for fmt, ext in [('png','png'), ('jpg','jpeg'), ('bmp','bmp'), ('gif','gif')]:
                result = call('export_sprite', sprite_path=str(source), output_path=str(out / ('single.'+ext)), format=fmt, frame_number=1)
                assert 'files' not in result and Path(result['exported_path']).stat().st_size == result['file_size'] > 0
            gif = call('export_sprite', sprite_path=str(source), output_path=str(out/'animation.gif'), format='gif', frame_number=0)
            assert 'files' not in gif and len(inspect(gif['exported_path'])['frames']) == 2
            single = Path(call('create_canvas', width=8, height=8, color_mode='rgb')['file_path'])
            result = call('export_sprite', sprite_path=str(single), output_path=str(out/'one.png'), format='png', frame_number=0)
            assert 'files' not in result and result['exported_path']==str(out/'one.png')
            for kwargs in [dict(output_path=str(out/'bad.bmp'),format='png',frame_number=1),
                           dict(output_path=str(out/'bad.png'),format='png',frame_number=3)]:
                reject('export_sprite',sprite_path=str(source),**kwargs)
                assert not Path(kwargs['output_path']).exists() and source.read_bytes()==original
            alias=out/'alias.png'
            if not alias.exists(): alias.symlink_to(source)
            reject('export_sprite',sprite_path=str(source),output_path=str(alias),format='png',frame_number=1)
            assert source.read_bytes()==original
            guard=out/'guard_0002.png';guard.write_bytes(b'protected');guard.chmod(0o444)
            first=out/'guard_0001.png';first.write_bytes(b'first-original')
            reject('export_sprite',sprite_path=str(source),output_path=str(out/'guard.png'),format='png',frame_number=0)
            assert first.read_bytes()==b'first-original' and guard.read_bytes()==b'protected' and source.read_bytes()==original
            print('PASS: single-frame/GIF compatibility, jpeg extension, invalid frame/format, aliases and protected sequence outputs', flush=True)
            # Analysis of native/BMP must match the first visible composite's PNG.
            png = out/'single.png'
            baseline = call('analyze_reference',reference_path=str(png),target_width=8,target_height=8)
            for reference in [out/'single.bmp', source, out/'animation.gif']:
                before=reference.read_bytes(); mode=stat.S_IMODE(reference.stat().st_mode)
                result = call('analyze_reference',reference_path=str(reference),target_width=8,target_height=8)
                assert result['brightness_map'] == baseline['brightness_map']
                assert result['edge_map'] == baseline['edge_map']
                unchanged(reference,before,mode)
            call('analyze_reference',reference_path=str(out/'single.jpeg'),target_width=8,target_height=8)
            for mode in ['indexed','gray']:
                reference=out/(mode+'.ase');shutil.copyfile(source,reference)
                lua(reference, f'app.command.ChangePixelFormat{{ui=false,format="{mode}"}};app.activeSprite:saveAs(app.activeSprite.filename)')
                rendered=call('export_sprite',sprite_path=str(reference),output_path=str(out/(mode+'.png')),format='png',frame_number=1)
                expected=call('analyze_reference',reference_path=rendered['exported_path'],target_width=8,target_height=8)
                reference.chmod(0o444);before=reference.read_bytes()
                actual=call('analyze_reference',reference_path=str(reference),target_width=8,target_height=8)
                assert actual['brightness_map']==expected['brightness_map'] and actual['edge_map']==expected['edge_map']
                unchanged(reference,before,0o444)
            for name, content in [('corrupt.bmp',b'BMbroken'),('fake.aseprite',b'not native data')]:
                bad=out/name;bad.write_bytes(content)
                reject('analyze_reference',reference_path=str(bad),target_width=8,target_height=8)
                assert bad.read_bytes()==content
            assert not list(temp_root.glob('pixel-mcp-reference-*')), 'Reference temp data leaked'
            assert source.read_bytes()==original
            print('PASS: PNG/JPEG/GIF/BMP/native reference inputs, first-frame maps, indexed/grayscale/read-only preservation, corrupt input and temp cleanup', flush=True)
        finally:
            c.close()
            (out/'calls.json').write_text(json.dumps(calls,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExportContract))
    if not result.wasSuccessful(): raise SystemExit(1)
    if args.aseprite: live(args.aseprite, args.output)
