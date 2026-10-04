#!/usr/bin/env python3
"""Small newline-delimited stdio MCP client used by contract and smoke tests."""
import json
import os
import queue
import subprocess
import threading


class ProtocolError(RuntimeError):
    """JSON-RPC failure with the original wire code and diagnostic data intact."""

    def __init__(self, method, error):
        self.error = error
        self.code = error.get('code')
        self.data = error.get('data')
        super().__init__(f'{method}: {error}')


class ToolError(RuntimeError):
    """Tool failure retaining its envelope, request ID and recovery references."""

    def __init__(self, name, result):
        self.result = result
        self.diagnostic = {}
        try:
            value = json.loads('\n'.join(x['text'] for x in result.get('content', []) if x['type'] == 'text'))
            if isinstance(value, dict):
                self.diagnostic = value
        except (ValueError, KeyError, TypeError):
            pass  # Keep legacy/non-JSON errors available in result and str(error).
        self.request_id = self.diagnostic.get('request_id')
        error = self.diagnostic.get('error', {})
        self.code = error.get('code') if isinstance(error, dict) else None
        self.recovery = error.get('recovery') if isinstance(error, dict) else None
        super().__init__(f'{name}: {result}')


class Client:
    def __init__(self, command, env=None):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True, env=env or os.environ)
        self.messages = queue.Queue()
        self.errors = []
        self.next_id = 0
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._stderr, daemon=True).start()
        try:
            self.info = self.request('initialize', {'protocolVersion': '2025-03-26',
                'capabilities': {}, 'clientInfo': {'name': 'pixel-plugin-contract-test', 'version': '1'}})
            self.send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
        except Exception:
            self.close()
            raise

    def _read(self):
        try:
            for line in self.process.stdout:
                self.messages.put(json.loads(line))
        except Exception as error:
            self.messages.put(error)
        finally:
            self.messages.put(EOFError('MCP stdout closed'))

    def _stderr(self):
        for line in self.process.stderr:
            self.errors.append(line)
            self.errors = self.errors[-30:]

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + '\n')
        self.process.stdin.flush()

    def request(self, method, params):
        self.next_id += 1
        self.send({'jsonrpc': '2.0', 'id': self.next_id, 'method': method, 'params': params})
        while True:
            try:
                response = self.messages.get(timeout=60)
            except queue.Empty:
                raise TimeoutError(f'{method}: no response within 60 seconds\n' + ''.join(self.errors))
            if isinstance(response, Exception):
                raise RuntimeError(f'{method}: {response}\n' + ''.join(self.errors))
            if response.get('id') != self.next_id:
                continue
            if 'error' in response:
                raise ProtocolError(method, response['error'])
            return response['result']

    def tools(self):
        tools, params = [], {}
        while True:
            result = self.request('tools/list', params)
            tools.extend(result['tools'])
            if not result.get('nextCursor'):
                return sorted(tools, key=lambda t: t['name'])
            params = {'cursor': result['nextCursor']}

    def call(self, name, arguments):
        result = self.request('tools/call', {'name': name, 'arguments': arguments})
        if result.get('isError'):
            raise ToolError(name, result)
        if 'structuredContent' in result:
            return result['structuredContent']
        texts = [x['text'] for x in result.get('content', []) if x['type'] == 'text']
        return json.loads('\n'.join(texts))

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdout.close()
        self.process.stderr.close()
