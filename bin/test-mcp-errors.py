#!/usr/bin/env python3
"""Error envelope/client regressions, with optional real bundled MCP/Aseprite calls."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import queue
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('client', ROOT / 'bin/mcp-client.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
REQUEST = 'io.github.smrgd88.pixel-mcp/request_id'
ERROR = 'io.github.smrgd88.pixel-mcp/error'


def tool_error(result, code):
    assert result.get('isError') is True, result
    assert 'structuredContent' not in result, result
    diagnostic = json.loads('\n'.join(x['text'] for x in result['content'] if x['type'] == 'text'))
    assert str(UUID(diagnostic['request_id'])) == diagnostic['request_id']
    assert diagnostic['error']['code'] == code, diagnostic
    assert diagnostic['error']['message']
    assert result['_meta'][REQUEST] == diagnostic['request_id']
    assert result['_meta'][ERROR] == diagnostic['error']
    return diagnostic


class ClientCompatibility(unittest.TestCase):
    def test_recovery_and_unknown_codes_survive_without_retry(self):
        client = module.Client.__new__(module.Client)
        recovery = [dict(output_index=1, directory='.pixel-mcp-stage-one',
                         backup_file='.original-backup', rollback_failed=True),
                    dict(output_index=2, directory='.pixel-mcp-stage-two', rollback_failed=False)]
        for code in ['file_rollback_failed', 'future_error']:
            diagnostic = {'request_id': '61e61bd5-5cfc-4239-8b27-c9a1d8de3369',
                          'error': {'code': code, 'message': 'Manual recovery required.', 'recovery': recovery}}
            wire = {'isError': True, 'content': [{'type': 'text', 'text': json.dumps(diagnostic)}],
                    '_meta': {REQUEST: diagnostic['request_id'], ERROR: diagnostic['error']}}
            with patch.object(client, 'request', return_value=wire) as request:
                with self.assertRaises(module.ToolError) as caught:
                    client.call('export_sprite', {})
                error = caught.exception
                self.assertIs(error.result, wire)
                self.assertEqual(error.request_id, diagnostic['request_id'])
                self.assertEqual(error.code, code)
                self.assertEqual(error.recovery, recovery)
                self.assertNotIn('backup_file', error.recovery[1])
                self.assertIsInstance(error, RuntimeError)
                request.assert_called_once()

    def test_protocol_data_survives_request(self):
        client = module.Client.__new__(module.Client)
        client.next_id, client.messages, client.send = 0, queue.Queue(), Mock()
        error = {'code': -32602, 'message': 'Invalid tool arguments.',
                 'data': {'request_id': '61e61bd5-5cfc-4239-8b27-c9a1d8de3369',
                          'error': {'code': 'invalid_arguments', 'message': 'Invalid tool arguments.'}}}
        client.messages.put({'jsonrpc': '2.0', 'id': 1, 'error': error})
        with self.assertRaises(module.ProtocolError) as caught:
            client.request('tools/call', {'name': 'create_canvas', 'arguments': {}})
        self.assertIs(caught.exception.error, error)
        self.assertEqual(caught.exception.code, -32602)
        self.assertEqual(caught.exception.data, error['data'])
        client.send.assert_called_once()

    def test_legacy_error_and_success_payload(self):
        client = module.Client.__new__(module.Client)
        for text in ['old failure', 'null', '["old failure"]']:
            wire = {'isError': True, 'content': [{'type': 'text', 'text': text}]}
            with patch.object(client, 'request', return_value=wire):
                with self.assertRaises(module.ToolError) as caught:
                    client.call('legacy', {})
                self.assertIs(caught.exception.result, wire)
        result = {'success': True, 'warnings': [{'code': 'future_warning', 'message': 'Effect'}]}
        for structured in [False, True]:
            wire = {'_meta': {REQUEST: 'some-id'}, 'content': [{'type': 'text', 'text': json.dumps(result)}]}
            if structured:
                wire['structuredContent'] = result
            with patch.object(client, 'request', return_value=wire) as request:
                self.assertEqual(client.call('flatten_layers', {}), result)
                request.assert_called_once()


def live(aseprite):
    with tempfile.TemporaryDirectory(prefix='pixel-errors-') as temp:
        root = Path(temp).resolve()
        ids = set()
        sent_id = '00000000-0000-4000-8000-000000000001'
        for timing in [False, True]:
            current_ids = set()
            config = root / 'config.json'
            config.write_text(json.dumps(dict(aseprite_path=str(aseprite.resolve(strict=True)),
                temp_dir=str(root / 'sprites'), snapshot_dir=str(root / 'snapshots'),
                enable_history=False, enable_timing=timing, log_level='info')))
            env = dict(os.environ, PIXEL_MCP_CONFIG=str(config)); env.pop('PIXEL_MCP_BINARY', None)
            client = module.Client([str(ROOT / 'bin/pixel-mcp')], env)
            def remember(request_id):
                assert str(UUID(request_id)) == request_id
                assert request_id not in ids and request_id != sent_id
                ids.add(request_id)
                current_ids.add(request_id)
            def call(name, arguments, code=None):
                wire = client.request('tools/call', dict(name=name, arguments=arguments, _meta={REQUEST: sent_id}))
                remember(wire['_meta'][REQUEST])
                if code:
                    diagnostic = tool_error(wire, code)
                    assert str(root) not in json.dumps(wire)
                    assert 'private-missing-layer' not in json.dumps(wire)
                    return diagnostic
                assert not wire.get('isError'), wire
                assert ERROR not in wire['_meta']
                payload = wire['structuredContent']
                assert payload == json.loads(wire['content'][0]['text'])
                assert 'request_id' not in payload
                return payload
            try:
                path = call('create_canvas', dict(width=8, height=8, color_mode='rgb'))['file_path']
                call('add_layer', dict(sprite_path=path, layer_name='Extra'))
                preview = call('flatten_layers', dict(sprite_path=path, dry_run=True))
                assert [x['code'] for x in preview['warnings']] == ['layer_flattening']
                before = Path(path).read_bytes()
                call('get_sprite_info', dict(sprite_path=str(root / 'private-missing.aseprite')), 'not_found')
                call('set_palette', dict(sprite_path=path, colors=[]), 'invalid_arguments')
                call('delete_layer', dict(sprite_path=path, layer_name='private-missing-layer'), 'lua_error')
                assert Path(path).read_bytes() == before
                for name, arguments in [('create_canvas', {}), ('create_canvas', dict(width='private-value', height=8, color_mode='rgb')), ('private-unknown-tool', {})]:
                    try:
                        client.request('tools/call', dict(name=name, arguments=arguments))
                    except module.ProtocolError as error:
                        assert error.code == -32602, error.error
                        remember(error.data['request_id'])
                        assert error.data['error']['code'] == 'invalid_arguments'
                        assert 'private-' not in json.dumps(error.error)
                    else:
                        raise AssertionError('Expected JSON-RPC rejection')
            finally:
                client.close()
            logs = ''.join(client.errors)
            assert str(root) not in logs and 'private-' not in logs, logs
            # Completion logs remain correlated even with timing disabled.
            assert all(request_id in logs for request_id in current_ids), logs
            print(f'PASS: timing={timing}: success/warnings, unique server IDs, tool/schema/unknown errors, Lua classification, redacted logs')
        print(f'PASS: {len(ids)} distinct live request IDs across timing on/off; isolated history disabled')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aseprite', type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ClientCompatibility))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.aseprite:
        live(args.aseprite)
