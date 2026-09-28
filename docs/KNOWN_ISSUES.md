# Known issues and contract boundaries

These notes apply to the MCP develop source pinned in [mcp-source.json](../config/mcp-source.json). Plugin version is recorded in [.claude-plugin/plugin.json](../.claude-plugin/plugin.json).

## Fix status

The original BUG-01–05 reports are fixed in the current bundle and integrated through
plugin PR #7. That does not mean all defects are resolved. See [the dated status ledger](BUG_STATUS.md)
for source/PR links and [the latest focused audit](BUG_AUDIT.md) for reproduction evidence.

## Confirmed remaining MCP defects

| ID | Effect | Current usage guidance |
|---|---|---|
| MCP-AUDIT-01 (P1) | Shrinking an indexed palette can move the transparent mask onto an in-use opaque color; a 32-pixel blue region became transparent with Success=true | Avoid shortening indexed palettes with set_palette. Preserve a native copy and edit entries without reducing length; use quantization only when color reduction is actually intended |
| MCP-AUDIT-02 (P2) | analyze_reference edge_threshold=0 is replaced with default 30 | Use an explicit positive threshold; 1 is not a promise of true zero-threshold behavior |
| MCP-AUDIT-03 (P2) | suggest_antialiasing threshold is advertised as sensitivity but ignored by detection | Do not promise sensitivity tuning with this argument; inspect suggestions and adjust pixels manually |

These are investigation IDs, not upstream issue numbers. The runtime fixes belong in
MCP; this plugin documents the behavior and preserves the server response.

## Documented implementation limits

Floyd–Steinberg interior density values currently produce the same horizontal gradient
(DITHER-01). Binary texture matrices have coarse coverage steps (DITHER-02). Both are
upstream follow-up work, distinct from the repaired 0/1 endpoints. In an 8×8 audit,
Floyd .25/.5/.75 each yielded red32/blue32; checkerboard yielded 32/32, 32/32, 0/64.
Bayer 4×4 responded with 48/16, 32/32, 16/48. Current guidance does not promise an exact
ratio for every pattern. Palette extraction quality/determinism needs further review;
it is not counted as a newly confirmed defect here.

## Contract boundaries

- The server operates on files through batch Aseprite processes. It does not inspect the GUI's current unsaved document, control playback, or expose arbitrary Aseprite Lua execution.
- `get_sprite_info` has no tags, durations or cel-link identity fields. Native link targets must have no cel; `add_frame` may copy content. Use the [animator's construction workflow](../skills/pixel-art-animator/SKILL.md).
- Export inputs have no scale, FPS, loop, layer, tag or range selector. Scaling/retiming/filtering is a separate workflow on a native copy. There is no standalone JSON or engine-specific metadata exporter. See [export formats](../skills/pixel-art-exporter/export-formats.md).
- Export format and extension must match (.jpeg is accepted for jpg). Multi-frame PNG/JPG/BMP now returns all numbered outputs in optional `files`; legacy `exported_path`/`file_size` identify only the first. Read the full array and inspect actual files.
- Exported sheet JSON can represent frames as an object. Read actual names/coordinates rather than assuming a fixed array shape. Padding affects border, shape and inner padding.
- Selection masks use row runs in the private pixel-mcp/selection extension-property namespace; user sprite.data remains untouched and legacy masks/bounds are still readable. Copy always targets the first layer and first frame and has no selector. Clipboard content is stored in a hidden layer in the same sprite; do not promise system or cross-file clipboard semantics.
- `analyze_reference` now supports BMP and native .ase/.aseprite via supported Aseprite. Native analysis is the visible composite of frame 1; GIF uses its first decoded image. There is no frame selector or full-animation analysis.
- `draw_with_dither` now preserves explicit density 0 (color1) and 1 (color2); omitted/null means 0.5. Intermediate pattern coverage is not an exact ratio; Floyd intermediate values retain a horizontal gradient. Dither-fill and palette quantization remain distinct operations.
- Legacy palette and shading outputs may use uppercase `Success`. Treat it as distinct from lowercase `success`. The [generated contract](MCP_TOOLS.md) lists exact response fields.
- The MCP protocol serverInfo.version remains 0.1.0 at this commit. Use the build's `--version` source hash and tools/list comparison to establish compatibility.

The bundled source includes the separately reviewed MCP behavior repairs described in [REPAIR_VALIDATION.md](REPAIR_VALIDATION.md). Remaining server work belongs in the MCP repository. Native integration was exercised on macOS arm64 with Aseprite 1.3.18.2. Other bundled targets are cross-built and checksum-checked; runtime behavior on those operating systems still needs target-specific validation.

Quantization now remaps pixels without dithering/indexed conversion and preserves distinct opaque colors when converting to indexed. See [color-operation limits](MCP_COLOR_OPERATIONS.md) for single-frame/raster, transparency, palette-size and pixel-validation constraints. The included capability check requires Aseprite 1.3.17.2+ / API 39+. File protection stages single-file writes; it is not undo, a backup, or multi-artifact atomic publishing.

See [export and analysis contracts](MCP_EXPORT_ANALYSIS.md). Sequence exports stage all outputs and attempt rollback for ordinary failures, but the set is not OS/crash-atomic and external writers or rollback failure can require recovery from retained backups. Spritesheet texture+JSON atomic publication remains separate.
