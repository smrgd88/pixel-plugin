# Export formats and options

See [validated examples](examples.md) and the [exact tool contract](../../docs/MCP_TOOLS.md).

| Output | MCP call | Behavior |
|---|---|---|
| Still PNG | `export_sprite`, `format: png`, `frame_number: 1` (or another one-based frame) | Preserve image transparency; specify a frame to avoid a sequence |
| Animated GIF | `export_sprite`, `format: gif`, `frame_number: 0` | All frames with saved timing; GIF has palette and alpha limits |
| JPG/BMP | `export_sprite`, matching `format` and extension | Use when that format is explicitly needed; verify transparency loss |
| Spritesheet | `export_spritesheet` | All frames; horizontal, vertical, rows, columns, packed |
| Metadata | sheet with `include_json: true` | Aseprite JSON alongside the texture; inspect before adapting to an engine |
| Native copy | `save_as` | `.aseprite` or `.ase`, preserves editable structure |

Format is validated as an argument but Aseprite selects its encoder using the file extension: keep them consistent. PNG with all frames may generate numbered files, so a zero `file_size` response is insufficient proof of export.

Spritesheet padding applies to border, shape and inner padding. Do not assume it is only the gap between frames or calculate final dimensions without reading the output. The MCP does not expose exact row/column counts, trimming, extrusion or alternate JSON formats.

Scale and FPS are plugin workflows: save a native copy, scale with nearest-neighbor and/or change frame durations, then export. For tag or layer filtering, obtain a known range or layer list and delete unwanted frames/layers on the copy. Delete frames from the end to avoid index shifts. There is no loop-count export option.

For Unity/Godot/Phaser, consume the actual frame names, coordinates and duration fields from the exported JSON; engine-specific asset/code generation is a separate adaptation, not an MCP export format.
