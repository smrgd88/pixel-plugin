# Known issues and contract boundaries

These notes apply to the MCP develop source pinned in [mcp-source.json](../config/mcp-source.json). Plugin version is recorded in [.claude-plugin/plugin.json](../.claude-plugin/plugin.json).

- The server operates on files through batch Aseprite processes. It does not inspect the GUI's current unsaved document, control playback, or expose arbitrary Aseprite Lua execution.
- `get_sprite_info` has no tags, durations or cel-link identity fields. Native link targets must have no cel; `add_frame` may copy content. Use the [animator's construction workflow](../skills/pixel-art-animator/SKILL.md).
- Export inputs have no scale, FPS, loop, layer, tag or range selector. Scaling/retiming/filtering is a separate workflow on a native copy. There is no standalone JSON or engine-specific metadata exporter. See [export formats](../skills/pixel-art-exporter/export-formats.md).
- The `format` export argument does not select the Aseprite encoder; the output extension does. Match them. `export_sprite` may report file_size=0 if the requested file does not exist (including numbered multi-frame PNG output); inspect the real files.
- Exported sheet JSON can represent frames as an object. Read actual names/coordinates rather than assuming a fixed array shape. Padding affects border, shape and inner padding.
- Selection masks are stored as row runs in sprite.data, with legacy rectangular states still readable. Copy always targets the first layer and first frame and has no selector. Clipboard content is stored in a hidden layer in the same sprite; do not promise system or cross-file clipboard semantics.
- `analyze_reference` advertises BMP/Aseprite in its schema description but uses Go image decoding; use PNG/JPEG/GIF raster references. Do not pass a native sprite directly for analysis.
- `draw_with_dither` density zero currently maps to the handler default 0.5. Use a filled shape for a uniform color. Dither-fill and full-image palette quantization are different operations.
- Legacy palette and shading outputs may use uppercase `Success`. Treat it as distinct from lowercase `success`. The [generated contract](MCP_TOOLS.md) lists exact response fields.
- The MCP protocol serverInfo.version remains 0.1.0 at this commit. Use the build's `--version` source hash and tools/list comparison to establish compatibility.

The bundled source includes the separately reviewed MCP behavior repairs described in [REPAIR_VALIDATION.md](REPAIR_VALIDATION.md). Remaining server work belongs in the MCP repository. Native integration was exercised on macOS arm64 with Aseprite 1.3.18.2. Other bundled targets are cross-built and checksum-checked; runtime behavior on those operating systems still needs target-specific validation.
