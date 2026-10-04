# Configuration guide

The server needs a JSON file containing an absolute `aseprite_path`. Copy [pixel-mcp-config.json](pixel-mcp-config.json) as a starting point, then set the real executable path. Existing user settings should be preserved when changing the path.

Configuration precedence at the [pinned MCP develop revision](mcp-source.json):

1. CLI `--config /absolute/path/config.json`.
2. `PIXEL_MCP_CONFIG` environment variable.
3. The user's `.config/pixel-mcp/config.json` (`~/.config/pixel-mcp/config.json` on macOS/Linux; `%USERPROFILE%\.config\pixel-mcp\config.json` on Windows).

The default is not APPDATA or XDG_CONFIG_HOME. Neither `CONFIG_PATH` nor `ASEPRITE_PATH` selects the server config. Shell variables and `~` in JSON paths are not expanded. The plugin's `.mcp.json` leaves environment overrides intact.

```json
{
  "aseprite_path": "/Applications/Aseprite.app/Contents/MacOS/aseprite",
  "temp_dir": "",
  "timeout": 30,
  "log_level": "info",
  "log_file": "",
  "enable_timing": false,
  "snapshot_dir": "",
  "enable_history": false
}
```

`temp_dir` defaults to the OS temp directory plus `pixel-mcp`; the server creates it. `timeout` is seconds and defaults to 30 when omitted or zero; negative values fail. Logging levels are debug/info/warn/error. Empty log_file means stderr only. enable_timing logs operation timing; stdout is reserved for MCP JSON-RPC. [Request IDs](../docs/MCP_ERRORS.md) are assigned even when timing is off. Non-debug CLI logs redact sensitive values; explicitly enabled debug can include paths, inputs and process output.

Example executable paths:

- macOS: `/Applications/Aseprite.app/Contents/MacOS/aseprite` (not the `.app` directory).
- Linux: `/usr/bin/aseprite` or another verified executable.
- Windows JSON: `"aseprite_path": "C:\\Program Files\\Aseprite\\Aseprite.exe"`.

Run `/pixel-setup` to discover and configure Aseprite, or `/pixel-setup /absolute/path/to/aseprite` for a manual location. Reconnect after configuration changes so the server reloads the file.

```bash
bin/pixel-mcp --health
bin/pixel-mcp --config /absolute/path/config.json --health
```

Health checks execute Aseprite to read its version and check the temporary directory. This is not a drawing test. For actual MCP calls and selecting a local server build, see [local development](../docs/LOCAL_MCP.md).

Optional `snapshot_dir` is an absolute durable private store path; empty uses os.UserConfigDir()/pixel-mcp/snapshots, separate from the legacy config directory and temp_dir. `enable_history` defaults false. Enable it only when the user requests automatic saved-file history; it adds backup costs and quota-dependent edit failures. Preserve both settings when configuring Aseprite and reconnect after changes. Read [preview/recovery limits](../docs/MCP_SAFETY.md).

## Codex plugin launch

Codex uses [.codex-plugin/plugin.json](../.codex-plugin/plugin.json) with
[codex-mcp.json](codex-mcp.json). Its stdio command is relative to the installed root;
`cwd: "."` makes Codex resolve that directory at installation/runtime. `env_vars` explicitly
forwards PIXEL_MCP_CONFIG and PIXEL_MCP_BINARY. Neither a shell expansion nor
CLAUDE_PLUGIN_ROOT is used for this connection. Default server config selection is unchanged.

Use the [CLI installation workflow](../README.md) and [recorded validation](../docs/CODEX_INSTALL_VALIDATION.md).
Adding a local plugin can create a separate installed cache; updating source files with the
same version does not necessarily refresh it. Reinstall after source changes and inspect the
actual cached path/version before claiming the new source is active.
