#!/usr/bin/env python3
"""Warning schema/client compatibility; optional real bundled MCP/Aseprite matrix."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('client', ROOT / 'bin/mcp-client.py')
client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client_module)
TOOLS = {t['name']: t for t in json.loads((ROOT / 'config/mcp-contract.json').read_text())['tools']}
LEGACY = {
    'flatten_layers': {'success': True},
    'quantize_palette': {'success': True, 'original_colors': 3, 'quantized_colors': 2,
                         'color_mode': 'indexed', 'palette': ['#000000', '#FFFFFF'], 'algorithm_used': 'median_cut'},
    'scale_sprite': {'success': True, 'new_width': 16, 'new_height': 16},
}


class Compatibility(unittest.TestCase):
    def test_optional_warning_schema(self):
        for name, old in LEGACY.items():
            validator = Draft202012Validator(TOOLS[name]['outputSchema'])
            for warnings in [None, [], [{'code': 'future_code', 'message': 'Future effect'}]]:
                with self.subTest(tool=name, warnings=warnings):
                    response = copy.deepcopy(old)
                    if warnings is not None:
                        response['warnings'] = warnings
                    validator.validate(response)
            for bad in [[{'code': 'x'}], [{'code': 1, 'message': 'x'}], 'warning']:
                with self.subTest(tool=name, invalid=bad), self.assertRaises(ValidationError):
                    validator.validate(dict(old, warnings=bad))

    def test_client_preserves_results(self):
        # Exercise the actual Client.call decoder, without launching a server.
        client = client_module.Client.__new__(client_module.Client)
        for name, old in LEGACY.items():
            for response in [old, dict(old, warnings=[{'code': 'future_code', 'message': 'Translated message'}])]:
                for structured in [False, True]:
                    envelope = {'content': [{'type': 'text', 'text': json.dumps(response)}]}
                    if structured:
                        envelope['structuredContent'] = response
                        envelope['content'][0]['text'] = '{}'
                    with self.subTest(tool=name, structured=structured, response=response):
                        with patch.object(client, 'request', return_value=envelope) as request:
                            self.assertEqual(client.call(name, {}), response)
                            request.assert_called_once()  # Warnings must not trigger a retry.
        with patch.object(client, 'request', return_value={'isError': True, 'structuredContent': LEGACY['flatten_layers']}):
            with self.assertRaises(RuntimeError):
                client.call('flatten_layers', {})


def live(aseprite):
    with tempfile.TemporaryDirectory(prefix='pixel-plugin-warnings-') as tmp:
        config = Path(tmp) / 'config.json'
        config.write_text(json.dumps({'aseprite_path': str(aseprite.resolve(strict=True)), 'temp_dir': tmp, 'log_level': 'error'}))
        env = dict(os.environ, PIXEL_MCP_CONFIG=str(config))
        env.pop('PIXEL_MCP_BINARY', None)
        client = client_module.Client([str(ROOT / 'bin/pixel-mcp')], env)
        cases = [('flatten', 'flatten_layers', {}, ['layer_flattening'])]
        for conversion in [None, False, True]:
            for dither in [False, True]:
                args = {'target_colors': 2, 'algorithm': 'median_cut', 'dither': dither}
                if conversion is not None:
                    args['convert_to_indexed'] = conversion
                codes = ['palette_quantization']
                if conversion is not False:
                    codes.append('color_mode_conversion')
                if dither:
                    codes.append('layer_flattening')
                cases.append((f'quantize indexed={conversion} dither={dither}', 'quantize_palette', args, codes))
        for algorithm in ['', 'nearest', 'bilinear', 'rotsprite']:
            for x, y in [(2, 2), (1, 2), (2, 1), (1, 1)]:
                codes = ['resampling'] if algorithm in ['bilinear', 'rotsprite'] and (x, y) != (1, 1) else []
                cases.append((f'scale {algorithm!r} {x}x{y}', 'scale_sprite', {'algorithm': algorithm, 'scale_x': x, 'scale_y': y}, codes))
        try:
            assert client.tools() == sorted(TOOLS.values(), key=lambda t: t['name'])
            for label, name, args, codes in cases:
                path = client.call('create_canvas', {'width': 8, 'height': 8, 'color_mode': 'rgb'})['file_path']
                client.call('draw_pixels', {'sprite_path': path, 'layer_name': 'Layer 1', 'frame_number': 1,
                    'pixels': [{'x': 1, 'y': 1, 'color': '#FF0000'}, {'x': 2, 'y': 2, 'color': '#00FF00'}, {'x': 3, 'y': 3, 'color': '#0000FF'}]})
                client.call('add_layer', {'sprite_path': path, 'layer_name': 'Extra'})
                arguments = dict(args, sprite_path=path)
                Draft202012Validator(TOOLS[name]['inputSchema']).validate(arguments)
                wire = client.request('tools/call', {'name': name, 'arguments': arguments})
                assert not wire.get('isError'), wire
                result = wire['structuredContent']
                text_result = json.loads('\n'.join(c['text'] for c in wire['content'] if c['type'] == 'text'))
                assert text_result == result
                Draft202012Validator(TOOLS[name]['outputSchema']).validate(result)
                assert result['success'] is True
                assert [w['code'] for w in result.get('warnings', [])] == codes, (label, result)
                assert all(w['message'] for w in result.get('warnings', []))
                if not codes:
                    assert 'warnings' not in result
                info = client.call('get_sprite_info', {'sprite_path': path})
                if name == 'quantize_palette':
                    assert result['color_mode'] == ('rgb' if args.get('convert_to_indexed') is False else 'indexed')
                    assert info['layer_count'] == (1 if args['dither'] else 2)
                elif name == 'flatten_layers':
                    assert info['layer_count'] == 1
                else:
                    assert (info['width'], info['height']) == (8 * args['scale_x'], 8 * args['scale_y'])
                print('PASS:', label)
            for name, args in [('flatten_layers', {}), ('quantize_palette', {'target_colors': 2, 'algorithm': 'median_cut', 'dither': True}),
                               ('scale_sprite', {'scale_x': 2, 'scale_y': 2, 'algorithm': 'bilinear'})]:
                wire = client.request('tools/call', {'name': name, 'arguments': dict(args, sprite_path=str(Path(tmp) / 'missing.aseprite'))})
                assert wire.get('isError') is True and not wire.get('structuredContent'), wire
                assert 'sprite file not found' in str(wire['content'])
                print('PASS:', name, 'failure remains error')
            print(f'PASS: {len(cases)} successful warning conditions and 3 real failure paths; text/structured equality')
        finally:
            client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Compatibility))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.aseprite:
        live(args.aseprite)
