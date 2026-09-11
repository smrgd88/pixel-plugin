#!/usr/bin/env python3
"""Check every documented MCP example, tool allowlist, and bundled source identity."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit('Install test dependencies: python3 -m pip install -r bin/requirements-test.txt')

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'mcp__aseprite__'


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'bin' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_call(tools, call):
    if call['name'] not in tools:
        raise ValueError('Unknown tool: ' + call['name'])
    name, args = call['name'], call['arguments']
    Draft202012Validator(tools[name]['inputSchema']).validate(args)
    # These handler constraints are prose in tools/list, not JSON Schema enums.
    enum_fields = {
        'create_canvas': {'color_mode': ['rgb', 'grayscale', 'indexed']},
        'export_sprite': {'format': ['png', 'gif', 'jpg', 'bmp']},
        'export_spritesheet': {'layout': ['horizontal', 'vertical', 'rows', 'columns', 'packed']},
        'quantize_palette': {'algorithm': ['median_cut', 'kmeans', 'octree']},
        'apply_auto_shading': {'style': ['cell', 'smooth', 'soft']},
        'apply_shading': {'style': ['pillow', 'smooth', 'hard']},
        'scale_sprite': {'algorithm': ['nearest', 'bilinear', 'rotsprite']},
        'create_tag': {'direction': ['forward', 'reverse', 'pingpong']},
        'draw_with_dither': {'pattern': ['bayer_2x2', 'bayer_4x4', 'bayer_8x8', 'checkerboard', 'floyd_steinberg', 'grass', 'water', 'stone', 'cloud', 'brick', 'dots', 'diagonal', 'cross', 'noise', 'horizontal_lines', 'vertical_lines']},
    }
    for key, choices in enum_fields.get(name, {}).items():
        if args.get(key) not in choices:
            raise ValueError(f'{name}.{key}: expected one of {choices}')
    for key in ['frame_number', 'source_frame', 'target_frame', 'from_frame', 'to_frame']:
        if key in args and args[key] < (0 if name == 'export_sprite' else 1):
            raise ValueError(f'{name}.{key}: invalid frame index')
    if name == 'export_sprite' and Path(args['output_path']).suffix.lower() != '.' + args['format']:
        raise ValueError('Export extension must match format')


def validate_docs(tools):
    examples, allowed = [], set()
    docs = list((ROOT/'skills').rglob('*.md')) + list((ROOT/'commands').glob('*.md'))
    docs += list((ROOT/'docs').glob('*.md')) + [ROOT/'README.md', ROOT/'CLAUDE.md', ROOT/'CONTRIBUTING.md', ROOT/'config/README.md']
    for path in docs:
        content = path.read_text()
        for name in re.findall(PREFIX + r'(\w+)', content):
            if name not in tools:
                raise ValueError(f'{path.relative_to(ROOT)}: unknown tool {name}')
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if re.match(r'\w+://', link) or link.startswith('#'):
                continue
            target = link.split('#')[0]
            if target and not (path.parent/target).exists():
                raise ValueError(f'{path.relative_to(ROOT)}: broken reference {link}')
        if path.name == 'SKILL.md':
            allowed.update(re.findall(PREFIX+r'(\w+)', content.split('---')[1]))
        owner = path if path.name == 'SKILL.md' or path.parent.name == 'commands' else path.parent/'SKILL.md'
        allowlist = set(re.findall(PREFIX+r'(\w+)', owner.read_text().split('---')[1])) if owner.exists() and owner.read_text().startswith('---') else set()
        for text in re.findall(r'```mcp-example\n(.*?)\n```', content, re.S):
            call = json.loads(text)
            validate_call(tools, call)
            if call['name'] not in allowlist:
                raise ValueError(f'{path}: {call["name"]} absent from owning skill/command allowed-tools')
            examples.append(call)
        if owner == path and allowlist:
            body = content.split('---',2)[2]
            used = {t for t in re.findall(r'`([a-z_]+)`', body) if t in tools}
            if used - allowlist:
                raise ValueError(f'{path}: calls outside allowlist: {used - allowlist}')
    if allowed != tools.keys():
        raise ValueError(f'Skill coverage differs: missing {tools.keys()-allowed}, unknown {allowed-tools.keys()}')
    if {e['name'] for e in examples} != tools.keys():
        raise ValueError('Every live tool must have a documented, validated example')
    return examples


def regressions(tools, examples):
    originals = {c['name']: c for c in examples}
    mutations = []
    def mutate(name, key, value):
        bad = copy.deepcopy(originals[name]); bad['arguments'][key] = value; mutations.append(bad)
    mutate('export_sprite', 'scale', 2)
    mutate('export_sprite', 'frame_number', -1)
    mutate('export_spritesheet', 'layout', 'grid')
    mutate('apply_auto_shading', 'style', 'hard')
    mutate('draw_pixels', 'frame_number', 0)
    mutate('draw_pixels', 'pixels', [{'x':0,'y':0,'colour':'#FFFFFF'}])
    mutate('create_canvas', 'width', '16')
    missing = copy.deepcopy(originals['export_sprite']); del missing['arguments']['sprite_path']; mutations.append(missing)
    mutations.append({'name': 'export_png', 'arguments': {}})
    for bad in mutations:
        try:
            validate_call(tools, bad)
        except Exception:
            continue
        raise AssertionError('Validator accepted regression: ' + repr(bad))
    print(f'PASS: {len(mutations)} historical contract regressions rejected')


def compare(live, snapshot):
    actual = {t['name']: t for t in live}
    expected = {t['name']: t for t in snapshot}
    if actual != expected:
        changed = sorted(n for n in actual.keys() & expected.keys() if actual[n] != expected[n])
        raise ValueError(f'Live MCP contract drift: missing={sorted(expected.keys()-actual.keys())}, added={sorted(actual.keys()-expected.keys())}, changed={changed}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='initialize selected wrapper and compare tools/list; configuration required')
    parser.add_argument('--bundled', action='store_true', help='initialize bundled server in an isolated config; no real Aseprite needed')
    parser.add_argument('--capture-snapshot', action='store_true', help='with --live, capture a pinned-build tools/list for review instead of validating docs')
    args = parser.parse_args()
    if args.capture_snapshot and not args.live:
        parser.error('--capture-snapshot requires --live and a configured pinned build')
    contract = json.loads((ROOT/'config/mcp-contract.json').read_text())
    source = json.loads((ROOT/'config/mcp-source.json').read_text())
    if args.capture_snapshot:
        version = subprocess.check_output([str(ROOT/'bin/pixel-mcp'), '--version'], text=True).strip()
        if not re.fullmatch(r'pixel-mcp version ' + re.escape(source['commit']) + r' \(built [^\n]+\)', version):
            raise ValueError('Selected build does not identify the pinned source commit: ' + version)
        client = load_module('client', 'mcp-client.py').Client([str(ROOT/'bin/pixel-mcp')])
        try:
            captured = {'source_commit':source['commit'], 'tools':client.tools()}
            (ROOT/'config/mcp-contract.json').write_text(json.dumps(captured, indent=2)+'\n')
            print('Captured tools/list; review changes, regenerate reference, then validate examples and live workflows')
        finally:
            client.close()
        return
    assert contract['source_commit'] == source['commit'], 'Snapshot/source pin mismatch'
    metadata = json.loads((ROOT/'bin/mcp-build.json').read_text())
    assert metadata['commit'] == source['commit'], 'Bundled/source pin mismatch'
    expected_names = {'pixel-mcp-'+p+s for p,s in [('darwin-amd64',''),('darwin-arm64',''),('linux-amd64',''),('linux-arm64',''),('windows-amd64','.exe')]}
    assert set(metadata['binaries']) == expected_names, 'Missing bundled platform hash'
    for name, digest in metadata['binaries'].items():
        assert hashlib.sha256((ROOT/'bin'/name).read_bytes()).hexdigest() == digest, 'Bundled checksum mismatch: ' + name
    tools = {t['name']: t for t in contract['tools']}
    for t in tools.values():
        for key in ['inputSchema','outputSchema']:
            Draft202012Validator.check_schema(t[key])
    examples = validate_docs(tools)
    renderer = load_module('reference', 'render-mcp-reference.py')
    assert (ROOT/'docs/MCP_TOOLS.md').read_text() == renderer.render(contract), 'Regenerate docs/MCP_TOOLS.md'
    regressions(tools, examples)
    print(f'PASS: {len(tools)} tools, {len(examples)} documented examples, allowlists, links, generated reference, 5 bundled checksums')
    if args.live or args.bundled:
        client_module = load_module('client', 'mcp-client.py')
        with tempfile.TemporaryDirectory(prefix='pixel-plugin-contract-') as tmp:
            env = os.environ.copy()
            if args.bundled:
                # tools/list never executes Aseprite. The fixture only satisfies
                # startup path validation and is not a health/integration pass.
                env.pop('PIXEL_MCP_BINARY', None)
                config = Path(tmp)/'config.json'
                config.write_text(json.dumps({'aseprite_path':sys.executable,'temp_dir':tmp,'log_level':'error'}))
                env['PIXEL_MCP_CONFIG'] = str(config)
            client = client_module.Client([str(ROOT/'bin/pixel-mcp')], env)
            try:
                compare(client.tools(), contract['tools'])
                print('PASS: MCP initialize and all live input/output schemas match snapshot (' + ('bundled, no Aseprite calls' if args.bundled else 'selected server') + ')')
            finally:
                client.close()


if __name__ == '__main__':
    main()
