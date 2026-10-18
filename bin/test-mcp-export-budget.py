#!/usr/bin/env python3
"""Real bundled MCP export-budget regressions; isolated files/config, unchanged 30s timeout.

Optionally compare the prior bundle's rejection of formerly overestimated requests.
Pillow checks complete PNG content independently of the server's native decoder.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'bin' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def state(path):
    p = Path(path)
    s = p.stat()
    return (hashlib.sha256(p.read_bytes()).hexdigest(), s.st_ino, s.st_mtime_ns, s.st_mode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', required=True, type=Path)
    parser.add_argument('--previous-binary', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'test-outputs/export-budget')
    args = parser.parse_args()
    ase = str(args.aseprite.resolve(strict=True))
    out = args.output.resolve() / ('run-' + uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    config = out / 'config.json'
    config.write_text(json.dumps({'aseprite_path': ase, 'temp_dir': str(out / 'temp'),
        'snapshot_dir': str(out / 'snapshots'), 'enable_history': False, 'timeout': 30,
        'log_level': 'error'}))
    env = dict(os.environ, PIXEL_MCP_CONFIG=str(config))
    env.pop('PIXEL_MCP_BINARY', None)
    client_module = load('client', 'mcp-client.py')
    current = client_module.Client([str(ROOT / 'bin/pixel-mcp')], env)
    previous = None
    calls, checks, ids = [], [], set()
    complete = False

    def call(client, arguments, code=None):
        wire = client.request('tools/call', {'name': 'export_spritesheet', 'arguments': arguments})
        calls.append({'server': 'previous' if client is previous else 'current',
                      'arguments': arguments, 'wire': wire})
        rid = wire['_meta']['io.github.smrgd88.pixel-mcp/request_id']
        uuid.UUID(rid)
        assert rid not in ids
        ids.add(rid)
        if code:
            value = json.loads('\n'.join(c['text'] for c in wire['content'] if c['type'] == 'text'))
            assert wire.get('isError') and value['error']['code'] == code, wire
            assert value['request_id'] == rid
            return value
        assert not wire.get('isError'), wire
        return wire['structuredContent']

    def mark(label):
        checks.append(label)
        print('PASS:', label, flush=True)

    def fixture(name, width, height, count, body):
        path = out / (name + '.aseprite')
        script = out / (name + '.lua')
        script.write_text(f'''local s=Sprite({width},{height});s.data="budget source metadata"
for i=1,{count} do
 if i>1 then s:newEmptyFrame() end
 s.frames[i].duration=(100+i)/1000
 {body}
end
s:saveAs(app.params.fixture_path)
''')
        # JSON string escaping is not Lua syntax (notably \uXXXX). Pass the
        # filename as one argv parameter so Unicode/quotes stay data.
        r = subprocess.run([ase, '--batch', '--script-param', f'fixture_path={path}',
                            '--script', str(script)], capture_output=True,
                           text=True, timeout=30)
        assert r.returncode == 0, r.stdout + r.stderr
        return path

    def arguments(source, name, layout='horizontal', **options):
        return dict(sprite_path=str(source), output_path=str(out / (name + '.png')),
                    layout=layout, padding=0, include_json=True, **options)

    def reject(arguments, code='invalid_arguments', client=None):
        # Seed both members, then require every output byte and stat to survive.
        texture = Path(arguments['output_path'])
        sidecar = texture.with_suffix('.json')
        texture.write_bytes(b'KEEP texture')
        sidecar.write_bytes(b'KEEP JSON')
        paths = [Path(arguments['sprite_path']), texture, sidecar]
        before = [state(p) for p in paths]
        entries = {str(p.relative_to(out)) for p in out.rglob('*')}
        call(client or current, arguments, code)
        assert [state(p) for p in paths] == before
        assert {str(p.relative_to(out)) for p in out.rglob('*')} == entries, 'staging leaked'

    def export(arguments, expected_size, source_size, count, content, client=None):
        before = state(arguments['sprite_path'])
        value = call(client or current, arguments)
        assert value['frame_count'] == count
        texture = Path(value['spritesheet_path'])
        metadata = json.loads(Path(value['metadata_path']).read_text())
        with Image.open(texture) as decoded:
            image = decoded.convert('RGBA')
        if expected_size:
            assert image.size == expected_size, image.size
        assert metadata['meta']['size'] == dict(w=image.width, h=image.height)
        assert metadata['meta']['image'] == texture.name
        frames = metadata['frames']
        frames = list(frames.values()) if isinstance(frames, dict) else frames
        frames.sort(key=lambda f: f['source_frame_number'])
        assert [f['source_frame_number'] for f in frames] == list(range(1, count + 1))
        expected = Image.new('RGBA', image.size)
        for n, frame in enumerate(frames, 1):
            assert frame['duration'] == 100 + n
            assert frame['sourceSize'] == dict(w=source_size[0], h=source_size[1])
            b = frame['frame']
            assert 0 <= b['x'] <= image.width - b['w'] and 0 <= b['y'] <= image.height - b['h']
            content(expected, frame, n)
            box = (b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h'])
            assert image.crop(box).tobytes() == expected.crop(box).tobytes(), (texture, n)
        assert image.tobytes() == expected.tobytes(), texture
        assert state(arguments['sprite_path']) == before
        return image, frames

    def solid(image, frame, n):
        b = frame['frame']
        image.paste((n, 0, 0, 255), (b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']))

    try:
        if args.previous_binary:
            previous = client_module.Client([str(args.previous_binary.resolve(strict=True))], env)
        snapshot = json.loads((ROOT / 'config/mcp-contract.json').read_text())
        load('contract', 'validate-mcp-contract.py').compare(current.tools(), snapshot['tools'])
        if previous:
            assert previous.tools() == current.tools(), 'Unexpected public schema change'
        many = fixture('many-한글 sprite', 128, 128, 65,
            'local im=Image(128,128);im:clear(app.pixelColor.rgba(i,0,0,255));s:newCel(s.layers[1],i,im)')
        def canvas(image, frame, n):
            assert frame['spriteSourceSize'] == dict(x=0,y=0,w=128,h=128)
            b = frame['frame']
            assert (b['w'], b['h']) == (128,128)
            if layout == 'rows':
                assert (b['x'], b['y']) == ((n-1)*128, 0)
            elif layout == 'columns':
                assert (b['x'], b['y']) == (0, (n-1)*128)
            solid(image, frame, n)
        for layout, size in [('rows', (8320,128)), ('columns', (128,8320)), ('packed', None)]:
            a = arguments(many, layout, layout)
            if previous:
                reject(dict(a, output_path=str(out / ('old-' + layout + '.png'))), client=previous)
            image, _ = export(a, size, (128,128), 65, canvas)
            assert image.width * image.height < 2 * 1024 * 1024
        mark('65 distinct 128x128 frames: rows/columns/packed accepted, full pixels/JSON/source preserved')
        wide = fixture('wide', 32767, 1, 2,
            'local im=Image(1,1);im:clear(app.pixelColor.rgba(i,0,0,255));s:newCel(s.layers[1],i,im,Point(i,0))')
        def trimmed(image, frame, n):
            assert frame['spriteSourceSize'] == dict(x=n, y=0, w=1, h=1)
            b = frame['frame']
            assert (b['w'], b['h']) == (1,1)
            if layout in ['horizontal','rows']:
                assert (b['x'], b['y']) == (n-1, 0)
            elif layout in ['vertical','columns']:
                assert (b['x'], b['y']) == (0, n-1)
            solid(image, frame, n)
        for layout in ['horizontal','vertical','rows','columns','packed']:
            a = arguments(wide, 'trim-' + layout, layout, trim=True)
            if previous:
                old = dict(a, output_path=str(out / ('old-trim-' + layout + '.png')))
                if layout == 'vertical':
                    export(old, (1,2), (32767,1), 2, trimmed, client=previous)
                else:
                    reject(old, client=previous)
            image, _ = export(a, None, (32767,1), 2, trimmed)
            assert image.width * image.height == 2
        mark('32767x1 canvas trim: all five layouts produce two pixels' +
             ('; four prior rejections and legacy vertical preserved' if previous else '; current bundle only'))
        duplicates = fixture('duplicates', 128, 128, 65,
            'local im=Image(128,128);im:clear(app.pixelColor.rgba(255,0,0,255));s:newCel(s.layers[1],i,im)')
        def red(image, frame, n):
            b = frame['frame'];assert b == dict(x=0,y=0,w=128,h=128)
            image.paste((255,0,0,255), (0,0,128,128))
        export(arguments(duplicates,'duplicates','packed'), (128,128), (128,128), 65, red)
        mark('packed duplicate samples share bounds while preserving 65 durations/source numbers')
        for label, options, size in [('omitted', {}, (20,11)),
                ('null', dict(border_padding=None,shape_padding=None,inner_padding=None), (20,11)),
                ('zero', dict(border_padding=0,shape_padding=0,inner_padding=0), (6,3))]:
            a = arguments(wide,'padding-' + label,trim=True,extrude=True,**options)
            a['padding'] = 2
            def padded(image, frame, n):
                inner = 0 if label == 'zero' else 2
                b = frame['frame'];assert (b['w'],b['h']) == (1+inner*2,1+inner*2)
                assert frame['spriteSourceSize'] == dict(x=n,y=0,w=1,h=1)
                # Native extrusion surrounds content inside the padded allocation.
                x, y = b['x'] + inner, b['y'] + inner
                image.paste((n,0,0,255),(x-1,y-1,x+2,y+2))
            export(a,size,(32767,1),2,padded)
        mark('omitted/null fallback versus explicit zero: exact padding and extrusion pixels/bounds')
        reject(arguments(wide,'over-side',trim=False))
        reject(arguments(wide,'over-border',frame_start=1,frame_end=1,border_padding=1))
        reject(arguments(wide,'bad-endpoint',frame_end=65536))
        reject(arguments(wide,'stale',trim=True,expected_revision='0'*64), 'file_changed')
        reject(arguments(wide,'no-overwrite',trim=True,overwrite=False))
        mark('dimension/endpoint/stale/overwrite rejections retain source and both output members')
        complex_source = fixture('complex',1,1,2000,
            'local im=Image(1,1);im:clear(app.pixelColor.rgba(i%256,math.floor(i/256),0,255));s:newCel(s.layers[1],i,im)')
        rejected = arguments(complex_source,'work-limit','packed')
        reject(rejected)
        # Public diagnostics deliberately sanitize internal budget messages.
        # The pinned allocator unit test independently isolates the work limit.
        mark('2000 distinct one-pixel samples: geometry-work rejection before sheet allocation')
        complete = True
    finally:
        current.close()
        if previous:
            previous.close()
        (out / 'calls.json').write_text(json.dumps(calls,indent=2)+'\n')
        (out / 'summary.json').write_text(json.dumps({'result':'PASS' if complete else 'FAIL',
            'checks':checks,'calls':len(calls),'previous_comparison':previous is not None},indent=2)+'\n')
        print('Evidence:',out)


if __name__ == '__main__':
    main()
