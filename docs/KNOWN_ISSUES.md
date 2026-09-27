# Known issues and contract boundaries

These notes apply to the MCP develop source pinned in [mcp-source.json](../config/mcp-source.json). Plugin version is recorded in [.claude-plugin/plugin.json](../.claude-plugin/plugin.json).

- The server operates on files through batch Aseprite processes. It does not inspect the GUI's current unsaved document, control playback, or expose arbitrary Aseprite Lua execution.
- `get_sprite_info` has no tags, durations or cel-link identity fields. Native link targets must have no cel; `add_frame` may copy content. Use the [animator's construction workflow](../skills/pixel-art-animator/SKILL.md).
- Export inputs have no scale, FPS, loop, layer, tag or range selector. Scaling/retiming/filtering is a separate workflow on a native copy. There is no standalone JSON or engine-specific metadata exporter. See [export formats](../skills/pixel-art-exporter/export-formats.md).
- The `format` export argument does not select the Aseprite encoder; the output extension does. Match them. All-frame PNG may fail when Aseprite produces numbered files instead of the staged requested file; use a selected frame or GIF/spritesheet. Inspect actual output files.
- Exported sheet JSON can represent frames as an object. Read actual names/coordinates rather than assuming a fixed array shape. Padding affects border, shape and inner padding.
- Selection masks use row runs in the private pixel-mcp/selection extension-property namespace; user sprite.data remains untouched and legacy masks/bounds are still readable. Copy always targets the first layer and first frame and has no selector. Clipboard content is stored in a hidden layer in the same sprite; do not promise system or cross-file clipboard semantics.
- `analyze_reference` advertises BMP/Aseprite in its schema description but uses Go image decoding; use PNG/JPEG/GIF raster references. Do not pass a native sprite directly for analysis.
- `draw_with_dither` now preserves explicit density 0 (color1) and 1 (color2); omitted/null means 0.5. Intermediate pattern coverage is not an exact ratio; Floyd intermediate values retain a horizontal gradient. Dither-fill and palette quantization remain distinct operations.
- Legacy palette and shading outputs may use uppercase `Success`. Treat it as distinct from lowercase `success`. The [generated contract](MCP_TOOLS.md) lists exact response fields.
- The MCP protocol serverInfo.version remains 0.1.0 at this commit. Use the build's `--version` source hash and tools/list comparison to establish compatibility.

The bundled source includes the separately reviewed MCP behavior repairs described in [REPAIR_VALIDATION.md](REPAIR_VALIDATION.md). Remaining server work belongs in the MCP repository. Native integration was exercised on macOS arm64 with Aseprite 1.3.18.2. Other bundled targets are cross-built and checksum-checked; runtime behavior on those operating systems still needs target-specific validation.

Quantization now remaps pixels without dithering/indexed conversion and preserves distinct opaque colors when converting to indexed. See [color-operation limits](MCP_COLOR_OPERATIONS.md) for single-frame/raster, transparency, palette-size and pixel-validation constraints. The included capability check requires Aseprite 1.3.17.2+ / API 39+. File protection stages single-file writes; it is not undo, a backup, or multi-artifact atomic publishing.
