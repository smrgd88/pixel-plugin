#!/usr/bin/env python3
"""Real bundled MCP color contracts; independently reopen native files and PNGs."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ['bayer_2x2', 'bayer_4x4', 'bayer_8x8', 'checkerboard', 'floyd_steinberg',
            'grass', 'water', 'stone', 'cloud', 'brick', 'dots', 'diagonal', 'cross',
            'noise', 'horizontal_lines', 'vertical_lines']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path, required=True)
    parser.add_argument('--output', type=Path, help='retain calls and independent inspection evidence')
    args = parser.parse_args()
    aseprite = str(args.aseprite.resolve(strict=True))
    spec = importlib.util.spec_from_file_location('client', ROOT / 'bin/mcp-client.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tools = {t['name']: t for t in json.loads((ROOT / 'config/mcp-contract.json').read_text())['tools']}
    with tempfile.TemporaryDirectory(prefix='pixel-color-contract-') as tmp:
        out = args.output.resolve() if args.output else Path(tmp) / 'outputs'
        out.mkdir(parents=True, exist_ok=True)
        config = Path(tmp) / 'config.json'
        config.write_text(json.dumps({'aseprite_path': aseprite, 'temp_dir': str(out / 'sprites'), 'log_level': 'error'}))
        env = dict(os.environ, PIXEL_MCP_CONFIG=str(config))
        env.pop('PIXEL_MCP_BINARY', None)
        wrapper = str(ROOT / 'bin/pixel-mcp')
        health = subprocess.run([wrapper, '--health'], env=env, capture_output=True, text=True, check=True)
        assert json.loads(health.stdout)["success"] is True
        client = module.Client([wrapper], env)
        calls, observations = [], []
        def call(name, **arguments):
            Draft202012Validator(tools[name]['inputSchema']).validate(arguments)
            result = client.call(name, arguments)
            Draft202012Validator(tools[name]['outputSchema']).validate(result)
            calls.append({'name': name, 'arguments': arguments, 'result': result})
            return result
        def inspect(path):
            data = subprocess.check_output([aseprite, '--batch', path, '--script', str(ROOT / 'bin/inspect-sprite.lua')], text=True)
            return json.loads(data)
        def pixels(info):
            return {xy: color for layer in info['layers'] for cel in layer['cels']
                    for xy, color in (cel['pixels'].items() if isinstance(cel['pixels'], dict) else [])}
        def sprite(mode='rgb', transparent=False):
            p = call('create_canvas', width=8, height=8, color_mode=mode)['file_path']
            colors = ['#000000', '#FFFFFF'] if mode == 'grayscale' else ['#FF0000', '#0000FF']
            if mode == 'indexed':
                # Keep an unused slot at both ends: Aseprite palette resizing
                # can clamp an existing transparent mask to the last entry.
                call('set_palette', sprite_path=p, colors=['#000000', *colors, '#000000'])
            data = [{'x': x, 'y': y, 'color': colors[x >= 4]} for y in range(8) for x in range(8)
                    if not (transparent and x == 0 and y == 0)]
            call('draw_pixels', sprite_path=p, layer_name='Layer 1', frame_number=1, pixels=data)
            return p
        def reject(name, path, **arguments):
            before = Path(path).read_bytes()
            try:
                wire = client.request('tools/call', {'name': name, 'arguments': dict(arguments, sprite_path=path)})
            except RuntimeError as error:
                # Schema type failures are JSON-RPC invalid-params errors, not tool results.
                if "'code': -32602" not in str(error):
                    raise
                wire = {'isError': True, 'invalid_params': str(error)}
            calls.append({'name': name, 'arguments': dict(arguments, sprite_path=path), 'wire': wire})
            assert wire.get('isError'), wire
            assert Path(path).read_bytes() == before, 'Rejected operation changed original'
            return wire
        try:
            assert client.tools() == sorted(tools.values(), key=lambda t: t['name'])
            # Exact two-color positions catch collapse-to-one regressions that <= N misses.
            for mode in ['rgb', 'grayscale', 'indexed']:
                for algorithm in ['median_cut', 'kmeans', 'octree']:
                    for dither in [False, True]:
                        for conversion in [False, True]:
                            p = sprite(mode)
                            before = pixels(inspect(p))
                            expected_colors = ['#000000FF', '#FFFFFFFF'] if mode == 'grayscale' else ['#FF0000FF', '#0000FFFF']
                            assert before == {f'{x},{y}': expected_colors[x >= 4] for y in range(8) for x in range(8)}
                            call('add_layer', sprite_path=p, layer_name='Extra')
                            r = call('quantize_palette', sprite_path=p, target_colors=2, algorithm=algorithm,
                                     dither=dither, convert_to_indexed=conversion)
                            info = inspect(p)
                            assert pixels(info) == before, (mode, algorithm, dither, conversion, info)
                            assert info['mode'] == (2 if conversion or mode == 'indexed' else 1 if mode == 'grayscale' else 0)
                            assert len(info['layers']) == (1 if dither else 2)
                            expected = ['palette_quantization'] + (['color_mode_conversion'] if conversion else []) + (['layer_flattening'] if dither else [])
                            assert [w['code'] for w in r['warnings']] == expected
                            png = str(out / f'{mode}-{algorithm}-{dither}-{conversion}.png')
                            call('export_sprite', sprite_path=p, output_path=png, format='png', frame_number=1)
                            assert pixels(inspect(png)) == before, 'Exported pixels differ'
                            observations.append({'case': 'quantize', 'mode': mode, 'algorithm': algorithm,
                                                 'dither': dither, 'conversion': conversion, 'colors': dict(Counter(before.values()))})
            print('PASS: 36 quantization mode/algorithm/dither/conversion cases, exact native and exported pixels', flush=True)
            # Three colors must really remap in RGB without either optional transformation.
            p = sprite()
            call('draw_pixels', sprite_path=p, layer_name='Layer 1', frame_number=1, pixels=[{'x': 0, 'y': 0, 'color': '#00FF00'}])
            before = pixels(inspect(p))
            r = call('quantize_palette', sprite_path=p, target_colors=2, algorithm='median_cut', dither=False, convert_to_indexed=False)
            after = pixels(inspect(p))
            assert len(set(before.values())) == 3 and len(set(after.values())) == 2 and before != after
            assert set(after.values()) <= {c.upper() + ('FF' if len(c) == 7 else '') for c in r['palette']}
            for preserve in [False, True]:
                p = sprite(transparent=True)
                call('quantize_palette', sprite_path=p, target_colors=3, algorithm='median_cut', dither=True,
                     convert_to_indexed=True, preserve_transparency=preserve)
                actual = pixels(inspect(p))
                assert '0,0' not in actual and len(actual) == 63 and len(set(actual.values())) == 2
            # Explicit null and omitted input are distinct on the wire; both default to .5.
            base = dict(layer_name='Layer 1', frame_number=1, region={'x': 2, 'y': 2, 'width': 4, 'height': 4},
                        color1='#FF0000', color2='#0000FF', pattern='bayer_2x2')
            defaults = []
            for extra in [{}, {'density': None}, {'density': .5}]:
                p = sprite(); before = pixels(inspect(p))
                call('draw_with_dither', sprite_path=p, **base, **extra)
                actual = pixels(inspect(p)); defaults.append(actual)
                assert sum(actual[f'{x},{y}'] == '#FF0000FF' for y in range(2, 6) for x in range(2, 6)) == 8
            assert defaults[0] == defaults[1] == defaults[2]
            for pattern in PATTERNS:
                for endpoint, expected in [(0, '#FF0000FF'), (1, '#0000FFFF')]:
                    p = sprite(); before = pixels(inspect(p))
                    call('draw_with_dither', sprite_path=p, **dict(base, pattern=pattern), density=endpoint)
                    after = pixels(inspect(p))
                    assert after.keys() == before.keys(), 'Density fill lost opaque pixels'
                    for xy, color in after.items():
                        x, y = map(int, xy.split(','))
                        assert color == (expected if 2 <= x < 6 and 2 <= y < 6 else before[xy]), (pattern, endpoint, xy)
            for endpoint, expected in [(0, '#FF0000FF'), (1, '#0000FFFF')]:
                p = sprite('indexed')
                call('draw_with_dither', sprite_path=p, **base, density=endpoint)
                actual = pixels(inspect(p))
                assert len(actual) == 64
                assert all(actual[f'{x},{y}'] == expected for y in range(2, 6) for x in range(2, 6))
            p = sprite()
            call('draw_with_dither', sprite_path=p, **base, density=0.0000001)
            actual = pixels(inspect(p))
            assert sum(actual[f'{x},{y}'] == '#FF0000FF' for y in range(2, 6) for x in range(2, 6)) == 12
            p = sprite()
            for invalid in [-.1, 1.1, 'invalid']:
                reject('draw_with_dither', p, **base, density=invalid)
            print('PASS: RGB pixel remap, transparent pixels, density omitted/null/default and 32 endpoints; invalid input preserves original', flush=True)
            p = sprite(); call('add_frame', sprite_path=p, duration_ms=100)
            reject('quantize_palette', p, target_colors=2, algorithm='median_cut', dither=True)
            output = out / 'sequence.png'; output.write_bytes(b'original-output-sentinel')
            reject('export_sprite', p, output_path=str(output), format='png', frame_number=0)
            assert output.read_bytes() == b'original-output-sentinel'
            assert not list(out.glob('sequence[0-9]*.png'))
            p = sprite()
            tile_script = Path(tmp) / 'tilemap.lua'
            # Fixture-only CLI API; the plugin exposes no arbitrary Lua tool.
            # https://www.aseprite.org/api/command/NewLayer
            tile_script.write_text('app.command.NewLayer{name="Tiles",tilemap=true,ask=false};'
                                   'assert(app.activeLayer.isTilemap);app.activeSprite:saveAs(app.activeSprite.filename)')
            subprocess.run([aseprite, '--batch', p, '--script', str(tile_script)], check=True, capture_output=True, timeout=30)
            error = reject('quantize_palette', p, target_colors=2, algorithm='median_cut', dither=True)
            assert 'tilemap' in str(error)
            p = sprite(); alias = out / (Path(p).stem + '-hardlink.aseprite'); os.link(p, alias)
            reject('quantize_palette', p, target_colors=2, algorithm='median_cut', dither=True)
            p = sprite(); peer = module.Client([wrapper], env)
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(c.call, 'add_layer', {'sprite_path': p, 'layer_name': name})
                               for c, name in [(client, 'One'), (peer, 'Two')]]
                    for future in futures:
                        assert future.result()['success']
                assert {l['name'] for l in inspect(p)['layers']} == {'Layer 1', 'One', 'Two'}
            finally:
                peer.close()
            print('PASS: animation/tilemap and PNG-sequence rejection, original/output preservation, hardlink refusal and concurrent writers', flush=True)
        finally:
            client.close()
            (out / 'calls.json').write_text(json.dumps(calls, indent=2))
            (out / 'observations.json').write_text(json.dumps(observations, indent=2))
            (out / 'health.json').write_text(health.stdout)


if __name__ == '__main__':
    main()
