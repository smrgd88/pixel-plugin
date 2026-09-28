# Known issues and contract boundaries

These notes apply to the MCP develop source pinned in [mcp-source.json](../config/mcp-source.json). Plugin version is recorded in [.claude-plugin/plugin.json](../.claude-plugin/plugin.json).

## Fix status

The original BUG-01–05 reports are fixed in the current bundle and integrated through
plugin PR #7. That does not mean all defects are resolved. See [the dated status ledger](BUG_STATUS.md)
for source/PR links and [the latest focused audit](BUG_AUDIT.md) for reproduction evidence.

## Audited defects now included in the bundle

MCP #22 is merged and pinned as bd13cdb, integrated through plugin PR #9. MCP-AUDIT-01 (indexed mask resize),
MCP-AUDIT-02 (explicit edge_threshold=0), and MCP-AUDIT-03 (inactive AA threshold)
are fixed in this bundle. The [original audit](BUG_AUDIT.md) records old behavior;
[current status](BUG_STATUS.md) and [control semantics](MCP_REVIEW_CONTROLS.md)
describe the included fixes. This is not a claim that every MCP defect is eliminated.

## Remaining algorithm and validation boundaries

Floyd and texture intermediate densities now affect output. A .5 texture retains its
original pattern: dots still selects color2 for 56/64 pixels in the documented 8×8 case.
Floyd error diffusion, tile quantization, indexed mapping and alpha/compositing mean
these settings do not guarantee a global exact ratio. No new exact-ratio mode is provided.
AA threshold filters existing candidate patterns, not arbitrary edge geometry.
Palette extraction now has deterministic seeds and correct initial convergence, but
keeps k entries; duplicates/zero-usage entries can remain when there are fewer unique
sampled colors. Large-image subsampling is not a guarantee of retaining every rare color.

## Contract boundaries

- The server operates on files through batch Aseprite processes. It does not inspect the GUI's current unsaved document, control playback, or expose arbitrary Aseprite Lua execution.
- `get_sprite_info` has no tags, durations or cel-link identity fields. Native link targets must have no cel; `add_frame` may copy content. Use the [animator's construction workflow](../skills/pixel-art-animator/SKILL.md).
- Export inputs have no scale, FPS, loop, layer, tag or range selector. Scaling/retiming/filtering is a separate workflow on a native copy. There is no standalone JSON or engine-specific metadata exporter. See [export formats](../skills/pixel-art-exporter/export-formats.md).
- Export format and extension must match (.jpeg is accepted for jpg). Multi-frame PNG/JPG/BMP now returns all numbered outputs in optional `files`; legacy `exported_path`/`file_size` identify only the first. Read the full array and inspect actual files.
- Exported sheet JSON can represent frames as an object. Read actual names/coordinates rather than assuming a fixed array shape. Padding affects border, shape and inner padding.
- Selection masks use row runs in the private pixel-mcp/selection extension-property namespace; user sprite.data remains untouched and legacy masks/bounds are still readable. Copy always targets the first layer and first frame and has no selector. Clipboard content is stored in a hidden layer in the same sprite; do not promise system or cross-file clipboard semantics.
- `analyze_reference` now supports BMP and native .ase/.aseprite via supported Aseprite. Native analysis is the visible composite of frame 1; GIF uses its first decoded image. There is no frame selector or full-animation analysis.
- `draw_with_dither` now preserves explicit density 0 (color1) and 1 (color2); omitted/null means 0.5. Intermediate coverage is not an exact ratio; Floyd now biases the horizontal gradient mean and textures use finer ranks. Dither-fill and palette quantization remain distinct operations.
- Legacy palette and shading outputs may use uppercase `Success`. Treat it as distinct from lowercase `success`. The [generated contract](MCP_TOOLS.md) lists exact response fields.
- The MCP protocol serverInfo.version remains 0.1.0 at this commit. Use the build's `--version` source hash and tools/list comparison to establish compatibility.

The bundled source includes the separately reviewed MCP behavior repairs described in [REPAIR_VALIDATION.md](REPAIR_VALIDATION.md). Remaining server work belongs in the MCP repository. Native integration was exercised on macOS arm64 with Aseprite 1.3.18.2. Other bundled targets are cross-built and checksum-checked; runtime behavior on those operating systems still needs target-specific validation.

Quantization now remaps pixels without dithering/indexed conversion and preserves distinct opaque colors when converting to indexed. See [color-operation limits](MCP_COLOR_OPERATIONS.md) for single-frame/raster, transparency, palette-size and pixel-validation constraints. The included capability check requires Aseprite 1.3.17.2+ / API 39+. File protection stages single-file writes; it is not undo, a backup, or multi-artifact atomic publishing.

See [export and analysis contracts](MCP_EXPORT_ANALYSIS.md). Sequence exports stage all outputs and attempt rollback for ordinary failures, but the set is not OS/crash-atomic and external writers or rollback failure can require recovery from retained backups. Spritesheet texture+JSON atomic publication remains separate.

Merged MCP #21 dry-run is not included in this pin. It is pending plugin integration,
not an available bundled feature. See [next work and completion criteria](NEXT_STEPS.md).
