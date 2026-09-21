#!/usr/bin/env python3
"""Build a committed MCP revision without touching its checkout or worktree."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'config/mcp-source.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='local pixel-mcp Git repository')
    parser.add_argument('--ref', help='committed revision; defaults to config/mcp-source.json')
    parser.add_argument('--go', default='go', help='Go executable (Go 1.25+ or toolchain auto-download)')
    parser.add_argument('--release', action='store_true', help='rebuild all five bundled platforms at the pinned revision')
    args = parser.parse_args()
    if os.path.dirname(args.go):
        args.go = str(Path(args.go).resolve())
    lock = json.loads(LOCK.read_text())
    revision = subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', '--verify', (args.ref or lock['commit']) + '^{commit}'], text=True).strip()
    if args.release and revision != lock['commit']:
        parser.error('release builds must use config/mcp-source.json commit; review the contract before changing the pin')
    targets = [('darwin', 'amd64'), ('darwin', 'arm64'), ('linux', 'amd64'), ('linux', 'arm64'), ('windows', 'amd64')]
    if not args.release:
        host = {'Darwin': 'darwin', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
        arch = {'arm64': 'arm64', 'aarch64': 'arm64', 'x86_64': 'amd64', 'AMD64': 'amd64'}[platform.machine()]
        targets = [(host, arch)]
    destination = ROOT / 'bin' if args.release else ROOT / 'bin/local'
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pixel-plugin-build-') as tmp:
        tmp = Path(tmp)
        archive = tmp / 'source.tar'
        with archive.open('wb') as output:
            subprocess.run(['git', '-C', str(args.source), 'archive', '--format=tar', revision], stdout=output, check=True)
        source = tmp / 'source'
        source.mkdir()
        subprocess.run(['tar', '-xf', str(archive), '-C', str(source)], check=True)
        # Go chooses the module's required toolchain. go.mod/go.sum are immutable
        # inputs from the selected commit; no build outputs enter the source repo.
        toolchain = subprocess.check_output([args.go, 'version'], cwd=source, text=True).strip()
        built = {}
        for host, arch in targets:
            name = ('pixel-mcp-' + host + '-' + arch) if args.release else 'pixel-mcp'
            if host == 'windows':
                name += '.exe'
            output = tmp / name
            env = dict(os.environ, GOOS=host, GOARCH=arch, CGO_ENABLED='0')
            subprocess.run([args.go, 'build', '-mod=readonly', '-trimpath', '-buildvcs=false',
                            '-ldflags=-s -w -X main.Version=' + revision + ' -X main.BuildTime=source-commit',
                            '-o', str(output), './cmd/pixel-mcp'], cwd=source, env=env, check=True)
            built[name] = output.read_bytes()
        # Publish only once every requested target builds successfully.
        for name, data in built.items():
            output = destination / name
            output.write_bytes(data)
            output.chmod(0o755)
            print(output)
        metadata = {'commit': revision, 'toolchain': toolchain, 'binaries': {name: hashlib.sha256(data).hexdigest() for name, data in built.items()}}
        (destination / ('mcp-build.json' if args.release else 'build.json')).write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    main()
