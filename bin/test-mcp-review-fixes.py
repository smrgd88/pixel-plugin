#!/usr/bin/env python3
"""Regression gate for bundled MCP #22 palette, threshold and density repairs."""
import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {t['name']: t for t in json.loads((ROOT / 'config/mcp-contract.json').read_text())['tools']}


class ThresholdSchemas(unittest.TestCase):
    def test_nullable_integer_controls(self):
        for tool, field, required in [
            ('analyze_reference', 'edge_threshold', {'reference_path': '/fixture.png', 'target_width': 8, 'target_height': 8}),
            ('suggest_antialiasing', 'threshold', {'sprite_path': '/fixture.aseprite', 'layer_name': 'Layer 1', 'frame_number': 1}),
        ]:
            validator = Draft202012Validator(TOOLS[tool]['inputSchema'])
            validator.validate(required)
            for value in [None, 0, 1, 128, 255]:
                with self.subTest(tool=tool, value=value):
                    validator.validate(dict(required, **{field: value}))
            for bad in ['0', .5, True]:
                with self.subTest(tool=tool, bad=bad), self.assertRaises(ValidationError):
                    validator.validate(dict(required, **{field: bad}))


def live(aseprite, output):
    aseprite = str(aseprite.resolve(strict=True))
    spec = importlib.util.spec_from_file_location('client', ROOT / 'bin/mcp-client.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='pixel-review-controls-') as tmp:
        out = output.resolve() if output else Path(tmp) / 'results'
        out.mkdir(parents=True, exist_ok=True)
        config = Path(tmp) / 'config.json'
        config.write_text(json.dumps({'aseprite_path': aseprite, 'temp_dir': str(out / 'sprites'), 'log_level': 'error'}))
        env = dict(os.environ, PIXEL_MCP_CONFIG=str(config)); env.pop('PIXEL_MCP_BINARY', None)
        c = module.Client([str(ROOT / 'bin/pixel-mcp')], env)
        calls, result = [], {}
        def call(name, **args):
            Draft202012Validator(TOOLS[name]['inputSchema']).validate(args)
            value = c.call(name, args)
            Draft202012Validator(TOOLS[name]['outputSchema']).validate(value)
            calls.append({'name': name, 'arguments': args, 'result': value})
            return value
        def sprite():
            return call('create_canvas', width=8, height=8, color_mode='rgb')['file_path']
        def draw(path, colors):
            call('draw_pixels', sprite_path=path, layer_name='Layer 1', frame_number=1, pixels=colors)
        def inspect(path):
            info = json.loads(subprocess.check_output([aseprite, '--batch', str(path), '--script', str(ROOT / 'bin/inspect-sprite.lua')], text=True, timeout=30))
            pixels = {xy: color for l in info['layers'] for ce in l['cels'] for xy, color in ce['pixels'].items()}
            return info, pixels
        def reject(name, path, **args):
            before = Path(path).read_bytes()
            try:
                wire = c.request('tools/call', {'name': name, 'arguments': args})
                assert wire.get('isError'), wire
            except RuntimeError as error:
                assert "'code': -32602" in str(error), error
                wire = {'invalid_params': str(error)}
            calls.append({'name': name, 'arguments': args, 'error': wire})
            assert Path(path).read_bytes() == before
        try:
            assert c.tools() == sorted(TOOLS.values(), key=lambda t: t['name'])
            p = sprite()
            expected = {f'{x},{y}': '#FF0000FF' if x < 4 else '#0000FFFF' for y in range(8) for x in range(8)}
            draw(p, [{'x': x, 'y': y, 'color': expected[f'{x},{y}']} for y in range(8) for x in range(8)])
            call('quantize_palette', sprite_path=p, target_colors=2, algorithm='median_cut', dither=False, convert_to_indexed=True)
            info, pixels = inspect(p); assert pixels == expected
            mask = info['transparent']
            for colors in [['#FF0000', '#0000FF', '#000000', '#FFFFFF'], ['#FF0000', '#0000FF']]:
                call('set_palette', sprite_path=p, colors=colors)
                info, pixels = inspect(p)
                assert info['transparent'] == mask and pixels == expected
            call('add_palette_color', sprite_path=p, color='#00FF00')
            info, pixels = inspect(p); assert info['transparent'] == mask and pixels == expected
            result['palette'] = {'mask': mask, 'pixels': dict(Counter(pixels.values()))}
            print('PASS: indexed mask and all 64 pixels survive palette expansion/shrink/add', flush=True)

            p = sprite()
            draw(p, [{'x': x, 'y': y, 'color': '#646464' if x < 4 else '#656565'} for y in range(8) for x in range(8)])
            ref = call('export_sprite', sprite_path=p, output_path=str(out/'low.png'), format='png', frame_number=1)['exported_path']
            edges = []
            for extra in [{}, {'edge_threshold': None}, {'edge_threshold': 0}, {'edge_threshold': 1}, {'edge_threshold': 30}]:
                value = call('analyze_reference', reference_path=ref, target_width=8, target_height=8, **extra)
                edges.append(sum(bool(v) for row in value['edge_map']['grid'] for v in row))
            assert edges == [0, 0, 12, 12, 0], edges
            for bad in [-1, 256, '0']:
                reject('analyze_reference', ref, reference_path=ref, target_width=8, target_height=8, edge_threshold=bad)
            result['edge_counts_omitted_null_0_1_30'] = edges

            p = sprite()
            draw(p, [{'x': x, 'y': y, 'color': '#FFFFFF40'} for y in range(1,7) for x in range(y,min(y+2,8))])
            original = Path(p).read_bytes(); counts = []
            for extra in [{}, {'threshold': None}, {'threshold': 0}, {'threshold': 63}, {'threshold': 64}, {'threshold': 255}]:
                value = call('suggest_antialiasing', sprite_path=p, layer_name='Layer 1', frame_number=1, auto_apply=False, **extra)
                counts.append(value['total_edges']); assert not value['applied']
                assert Path(p).read_bytes() == original
            assert counts == [0, 0, 5, 5, 0, 0], counts
            for bad in [-1, 256, '0']:
                reject('suggest_antialiasing', p, sprite_path=p, layer_name='Layer 1', frame_number=1, threshold=bad, auto_apply=True)
            applied = call('suggest_antialiasing', sprite_path=p, layer_name='Layer 1', frame_number=1, threshold=0, auto_apply=True)
            assert applied['applied'] and applied['total_edges'] == 5 and Path(p).read_bytes() != original
            result['aa_counts_omitted_null_0_63_64_255'] = counts
            print('PASS: omitted/null/explicit threshold boundaries, invalid input/source preservation, preview and apply', flush=True)

            profiles = {}
            for pattern, blue_counts in [('floyd_steinberg', [16,32,49]), ('checkerboard', [16,32,48]), ('dots', [28,56,60]), ('bayer_4x4', [16,32,48])]:
                counts = []
                for density in [.25,.5,.75]:
                    p = sprite()
                    call('draw_with_dither', sprite_path=p, layer_name='Layer 1', frame_number=1,
                         region={'x':0,'y':0,'width':8,'height':8}, color1='#FF0000', color2='#0000FF', pattern=pattern, density=density)
                    _, pixels = inspect(p)
                    assert len(pixels) == 64 and set(pixels.values()) <= {'#FF0000FF','#0000FFFF'}
                    counts.append(sum(v == '#0000FFFF' for v in pixels.values()))
                assert counts == blue_counts, (pattern, counts)
                profiles[pattern] = counts
            result['density_profiles'] = profiles

            p = sprite()
            draw(p, [{'x':x,'y':y,'color':'#00FF00' if (x,y)==(2,3) else '#FF0000'} for y in range(8) for x in range(8)])
            ref = call('export_sprite', sprite_path=p, output_path=str(out/'rare.png'), format='png', frame_number=1)['exported_path']
            reference = Path(ref).read_bytes(); baseline = None
            for _ in range(5):
                value = call('analyze_reference', reference_path=ref, target_width=8, target_height=8, palette_size=5)
                palette = value['palette']; usage = {}
                assert len(palette) == 5  # Output cardinality is retained, not unique color count.
                for entry in palette:
                    usage[entry['color']] = usage.get(entry['color'],0) + entry['usage_percent']
                assert usage['#FF0000'] == 98.4375 and usage['#00FF00'] == 1.5625, usage
                if baseline is not None: assert palette == baseline
                baseline = palette
                assert Path(ref).read_bytes() == reference
            result['rare_palette'] = baseline
            print('PASS: measured density profiles and 5 identical rare-color analyses with correct usage', flush=True)
        finally:
            c.close()
            (out/'calls.json').write_text(json.dumps(calls,indent=2))
            (out/'results.json').write_text(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    tests = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ThresholdSchemas))
    if not tests.wasSuccessful(): raise SystemExit(1)
    if args.aseprite: live(args.aseprite, args.output)
