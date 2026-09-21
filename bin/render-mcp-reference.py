#!/usr/bin/env python3
"""Render the reviewed tools/list snapshot as searchable Markdown (no server needed)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(contract):
    lines = ['# MCP tool contract', '',
             'Generated from the actual `tools/list` response at MCP source commit `' + contract['source_commit'] + '`.',
             'Regenerate with `python3 bin/render-mcp-reference.py` after reviewing a new snapshot.', '',
             'Read the tool section needed for the task. All tool names use the `mcp__aseprite__` prefix in skills/commands.',
             'Required fields come from JSON Schema, even if their descriptions mention defaults. Object and array child fields are included below.', '',
             'This records what the server advertises. Handler limits and workflow caveats are documented in the domain references and [known issues](KNOWN_ISSUES.md).', '',
             'MCP frame inputs start at 1, except export `frame_number: 0` (all frames) and duplicate `insert_after: 0` (append). Pixel coordinates and palette indices start at 0.', '',
             'Use `structuredContent` after checking `isError`; clients exposing only text content must parse its JSON. `Success` and `success` are distinct response fields.', '',
             '## Index', '']
    for tool in contract['tools']:
        lines.append('- [' + tool['name'] + '](#' + tool['name'] + ')')
    def fields(schema, prefix=''):
        rows=[]
        for name, prop in schema.get('properties', {}).items():
            field=prefix+name
            kind=prop.get('type', '')
            if isinstance(kind,list): kind='/'.join(kind)
            required='yes' if name in schema.get('required',[]) else 'no'
            desc=prop.get('description','').replace('|','\\|').replace('\n',' ')
            rows.append(f'| `{field}` | {kind} | {required} | {desc} |')
            rows += fields(prop,field+'.')
            if 'items' in prop:
                item=prop['items']
                if item.get('properties'):
                    rows += fields(item,field+'[].')
                else:
                    rows.append(f'| `{field}[]` | {item.get("type", "")} | — | Array item |')
        return rows
    for tool in contract['tools']:
        lines += ['', '## '+tool['name'], '', tool.get('description','')]
        for label,key in [('Input','inputSchema'),('Output','outputSchema')]:
            lines += ['', '### '+label, '', '| Field | Type | Required | Meaning |', '|---|---|---|---|'] + fields(tool[key])
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    (ROOT/'docs/MCP_TOOLS.md').write_text(render(json.loads((ROOT/'config/mcp-contract.json').read_text())))
