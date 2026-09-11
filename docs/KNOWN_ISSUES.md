# Known issues and contract boundaries

These notes apply to the MCP develop source pinned in [mcp-source.json](../config/mcp-source.json). Plugin version is recorded in [.claude-plugin/plugin.json](../.claude-plugin/plugin.json).

- The server operates on files through batch Aseprite processes. It does not inspect the GUI's current unsaved document, control playback, or expose arbitrary Aseprite Lua execution.
- `get_sprite_info` has no tags, durations or cel-link identity fields. Native link targets must have no cel; `add_frame` may copy content. Use the [animator's construction workflow](../skills/pixel-art-animator/SKILL.md).
- Export inputs have no scale, FPS, loop, layer, tag or range selector. Scaling/retiming/filtering is a separate workflow on a native copy. There is no standalone JSON or engine-specific metadata exporter. See [export formats](../skills/pixel-art-exporter/export-formats.md).
- The `format` export argument does not select the Aseprite encoder; the output extension does. Match them. `export_sprite` may report file_size=0 if the requested file does not exist (including numbered multi-frame PNG output); inspect the real files.
- Exported sheet JSON can represent frames as an object. Read actual names/coordinates rather than assuming a fixed array shape. Padding affects border, shape and inner padding.
- Selection persistence stores rectangular bounds in sprite.data, so multi-call ellipse/compound masks are not exact and existing custom sprite.data can be overwritten. Copy uses the batch process's active cel, has no explicit layer/frame selector, and stores a hidden clipboard layer in the same sprite. Do not promise system or cross-file clipboard semantics.
- `analyze_reference` advertises BMP/Aseprite in its schema description but uses Go image decoding; use PNG/JPEG/GIF raster references. Do not pass a native sprite directly for analysis.
- `draw_with_dither` density zero currently maps to the handler default 0.5. Use a filled shape for a uniform color. Dither-fill and full-image palette quantization are different operations.
- Transparent-image quantization with preserve_transparency=true fails when the quantizer emits `#00000000`: the MCP color parser rejects that alpha hex string. Reproduced through tools/call on the pinned develop build; opaque-image quantization is tested separately. Preserve the source and report the failure. Fixing alpha color parsing/transparent-palette mapping requires a separate MCP task. Do not silently disable transparency preservation.
- Legacy palette and shading outputs may use uppercase `Success`. Treat it as distinct from lowercase `success`. The [generated contract](MCP_TOOLS.md) lists exact response fields.
- The MCP protocol serverInfo.version remains 0.1.0 at this commit. Use the build's `--version` source hash and tools/list comparison to establish compatibility.

The plugin documents these upstream boundaries; it does not change MCP source. Any fixes to those server behaviors belong in a separate MCP task. Native integration was exercised on macOS arm64 with Aseprite 1.3.18.2. Other bundled targets are cross-built and checksum-checked; runtime behavior on those operating systems still needs target-specific validation.
