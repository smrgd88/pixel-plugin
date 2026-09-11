#!/usr/bin/env python3
"""Exercise executable selection, quoting, failure behavior and config precedence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
wrapper=ROOT/'bin/pixel-mcp'


def run(env, *args):
    return subprocess.run([str(wrapper),*args],env=env,text=True,capture_output=True,input="",timeout=10)


with tempfile.TemporaryDirectory(prefix='pixel plugin wrapper ') as tmp:
    work=Path(tmp)
    fake=work/'fake server'
    fake.write_text('#!/bin/bash\nprintf \'%s\\n\' "$@"\nexit 7\n')
    fake.chmod(0o755)
    env=dict(os.environ,PIXEL_MCP_BINARY=str(fake))
    result=run(env,'argument with spaces','--config',str(work/'a b.json'))
    assert result.returncode==7 and result.stdout.splitlines()==['argument with spaces','--config',str(work/'a b.json')],result
    for bad in ['relative/path',str(work/'missing'),str(wrapper)]:
        result=run(dict(env,PIXEL_MCP_BINARY=bad),'--version')
        assert result.returncode!=0 and not result.stdout and 'Error:' in result.stderr,result
    alias=work/'wrapper alias'; alias.symlink_to(wrapper)
    assert run(dict(env,PIXEL_MCP_BINARY=str(alias))).returncode!=0
    fake.chmod(0o644)
    assert run(env).returncode!=0
    env.pop('PIXEL_MCP_BINARY')
    commit=json.loads((ROOT/'config/mcp-source.json').read_text())['commit']
    result=run(env,'--version')
    assert result.returncode==0 and commit in result.stdout,result
    # Config is loaded before the server loop; EOF yields a clean shutdown.
    good=work/'explicit config.json'
    good.write_text(json.dumps({'aseprite_path':sys.executable,'temp_dir':str(work/'temp'),'log_level':'error'}))
    env['PIXEL_MCP_CONFIG']=str(work/'missing.json')
    assert run(env).returncode!=0
    assert run(env,'--config',str(good)).returncode==0, 'CLI --config must override environment'
    env['PIXEL_MCP_CONFIG']=str(good)
    assert run(env).returncode==0, 'Environment config must be honored'
    manifest=json.loads((ROOT/'.mcp.json').read_text())['mcpServers']['aseprite']
    assert manifest['command']=='${CLAUDE_PLUGIN_ROOT}/bin/pixel-mcp'
    assert not {'PIXEL_MCP_CONFIG','PIXEL_MCP_BINARY'} & manifest.get('env',{}).keys(), 'Manifest masks caller overrides'
print('PASS: wrapper selection, spaces/argv, error exit, recursion guard, bundled revision and config precedence')
