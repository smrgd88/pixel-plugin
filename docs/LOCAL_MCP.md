# Local MCP development and bundled builds

The plugin launches `.mcp.json` → `bin/pixel-mcp` → a platform binary. A build in a sibling MCP checkout does not automatically change the plugin's server.

## Pinned source

[config/mcp-source.json](../config/mcp-source.json) pins the merged MCP #24 safety revision at `7f439a0df1ec0d2d24ef6dabba6de4d30c2484f9`. All five bundled executables are built from that commit; [bin/mcp-build.json](../bin/mcp-build.json) records their SHA-256 hashes. The actual `tools/list` input/output schemas are in [config/mcp-contract.json](../config/mcp-contract.json).

The MCP protocol's `serverInfo.version` is still `0.1.0` in this source. It is not the plugin version or a reliable source identifier. `bin/pixel-mcp --version` in these builds reports the full source commit.

## Build and select a local server

Go 1.25+ is required by the source; a Go installation with toolchain auto-download enabled can obtain it. Python 3 and Git are needed for the build helper. This helper exports a committed revision into a temporary directory and builds there; it never checks out, cleans or writes to the referenced MCP repository. Uncommitted MCP changes are intentionally excluded.

Run from the plugin checkout:

```bash
python3 bin/build-mcp.py /path/to/pixel-mcp
# If Go is not on PATH:
python3 bin/build-mcp.py /path/to/pixel-mcp --go /path/to/go/bin/go

export PIXEL_MCP_BINARY="$PWD/bin/local/pixel-mcp"
export PIXEL_MCP_CONFIG="/absolute/path/to/pixel-mcp-config.json"
bin/pixel-mcp --version
bin/pixel-mcp --health
```

The ignored `bin/local/` contains the host build and its source/checksum record. Windows host builds use `pixel-mcp.exe`; set PIXEL_MCP_BINARY to that executable in a Bash-capable client environment. The wrapper accepts an absolute executable path, quotes paths with spaces and forwards arguments/stdio. Invalid overrides fail explicitly, without falling back to another build. Do not point the override at the wrapper itself or another launcher that invokes it.

Start the plugin host from the environment containing these exports. A GUI process or already-running MCP process will not inherit later shell changes: configure its launch environment and reconnect/restart the MCP server. A plugin installed in a cache may use a different wrapper copy; verify its actual configured path. The environment override can still point to this checkout's host binary.

`.mcp.json` does not hardcode either environment variable. Without PIXEL_MCP_BINARY it selects the bundled platform binary; without PIXEL_MCP_CONFIG the server uses the user's default configuration. To return to bundled execution, unset PIXEL_MCP_BINARY and reconnect.

For another committed development revision, add `--ref <commit>` to the build command. Compare its live contract before using it with these skills. The repository's documented contract remains pinned until explicitly updated and reviewed.

## Validation

```bash
python3 -m venv test-outputs/venv
. test-outputs/venv/bin/activate
python3 -m pip install -r bin/requirements-test.txt
./bin/test-plugin.sh

# Compare the selected local server using its configured Aseprite path:
python3 bin/validate-mcp-contract.py --live
# Isolated real calls; no user config is written or overwritten:
python3 bin/test-mcp-live.py --aseprite /absolute/path/to/aseprite
```

The default suite validates documents, examples, allowlists, all bundled checksums and actual bundled MCP initialization/tools/list. Its startup fixture uses Python as a placeholder executable and **does not test Aseprite**. The live tests require real Aseprite: test-mcp-live.py checks the smoke workflow; test-mcp-behavior.py checks every tool and selected options; test-skill-workflows.py executes the restored complete skill recipes. A missing dependency or failed call is an error, never an integration pass.

## Update bundled distribution

After reviewing a new MCP behavior-repair commit, update the source pin, capture its real `tools/list` into the contract snapshot, review input/output and handler differences, update examples/skills, and regenerate the reference:

```bash
python3 bin/build-mcp.py /path/to/pixel-mcp --release
# Use the newly built bundled server with a valid config; clear a stale override first.
unset PIXEL_MCP_BINARY
python3 bin/validate-mcp-contract.py --live --capture-snapshot
python3 bin/render-mcp-reference.py
./bin/test-plugin.sh
python3 bin/test-mcp-live.py --aseprite /absolute/path/to/aseprite
```

`--release` rebuilds darwin amd64/arm64, linux amd64/arm64 and windows amd64 from the pinned commit with CGO disabled, trimpath and a source-commit version. It stages all requested build results before replacing bundles, then updates checksums. Cross-compilation is not execution validation on those platforms; run target-specific smoke tests before release. Keep source pin, snapshot, binaries, checksums and user guidance in the same reviewed change. Build inputs include the commit's go.mod/go.sum; record the toolchain when reporting results.

Run `python3 bin/test-mcp-warnings.py` for schema/client compatibility and add `--aseprite /absolute/path/to/aseprite` for real warning conditions and failure paths. See [warning handling](MCP_WARNINGS.md) and [previous warnings validation](WARNINGS_VALIDATION.md).

This pin also includes MCP #13 capability checks and #14 single-file protection. `--health` returns JSON with version/API support status; tools/list startup alone does not probe Aseprite. File locking/staging does not replace pre-edit copy guidance, and does not provide undo or atomic publication of a spritesheet plus JSON. Run `python3 bin/test-mcp-color-operations.py --aseprite /absolute/path/to/aseprite` for exact-pixel, density and rejection regressions.

Previous color sync execution evidence and review: [color sync validation](COLOR_SYNC_VALIDATION.md).

Current [export/analysis contract](MCP_EXPORT_ANALYSIS.md) includes MCP #18 sequence output and #20 BMP/native reference support. Run `python3 bin/test-mcp-export-analysis.py --aseprite /absolute/path/to/aseprite` for actual file-list, frame pixel and reference analysis regressions.

Current execution, before/after comparison and review: [export/analysis validation](EXPORT_ANALYSIS_VALIDATION.md).

For merged fixes, confirmed remaining defects and unreleased work, use [the status ledger](BUG_STATUS.md) and [focused audit](BUG_AUDIT.md). The binary pin in this file is unchanged by that documentation-only audit.

The latest bundle verification, numeric comparisons and review scope are recorded in
[the MCP #22 sync validation](REVIEW_SYNC_VALIDATION.md). Earlier validation reports
retain the source pins and execution dates from their original runs.

The current source includes dry-run, snapshot/restore and opt-in history/undo. These are
separate from file staging: read [safety contracts](MCP_SAFETY.md). Verify with
`python3 bin/test-mcp-safety.py --aseprite /absolute/path/to/aseprite`. Test configs
must set an isolated absolute snapshot_dir and must not change the user’s history setting.
