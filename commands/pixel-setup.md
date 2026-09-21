---
description: Configure Aseprite and verify the selected MCP server
argument-hint: [aseprite-path]
allowed-tools: Read, Write, Bash
---

# /pixel-setup

Use `$ARGUMENTS` as an optional Aseprite executable path. Read [configuration](../config/README.md). Use the plugin's `config/detect-aseprite.sh` for discovery when no path is supplied; validate the selected executable with `--version`.

Resolve the configuration destination from PIXEL_MCP_CONFIG when set, otherwise the current user's `.config/pixel-mcp/config.json`. On Windows the default is under USERPROFILE, not APPDATA. Preserve existing configuration fields; update aseprite_path to an absolute path and fill absent defaults from the template. Do not replace a populated user config with the template.

Write JSON using proper escaping (use the Windows JSON example in config/README.md). Never store an unexpanded `~` or shell variable in JSON paths. The current plugin passes the environment through; CLI --config overrides PIXEL_MCP_CONFIG, which overrides the default path.

Run the selected plugin wrapper with `--health` and inspect its exit status. Health verifies Aseprite accessibility and version, not actual drawing. For protocol and drawing verification, use the commands in [local development](../docs/LOCAL_MCP.md). Report each check as passed, failed or not run.

PIXEL_MCP_BINARY can select an absolute local server executable; use the reproducible build workflow in LOCAL_MCP.md. After changing process environment or config, restart the MCP connection so the server reloads it. Report the selected binary/config and resulting health status.
