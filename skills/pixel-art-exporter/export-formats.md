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

## Keep the delivered asset readable

Choose PNG for a still with alpha, GIF for simple animation previews, and a sheet plus actual Aseprite metadata for engine integration. GIF cannot represent the full range of partial alpha; inspect the result instead of assuming it will match PNG. JPG is lossy and is usually a poor fit for crisp sprite edges unless specifically required.

For 2× or 4× output, scale a native copy with nearest-neighbor. A single source pixel should become an integer block of the same color. Bilinear interpolation creates intermediate colors; it is useful for some artwork but changes the pixel grid. Leave originals at native size when the engine will scale them.

Engine import guidance is separate from MCP export:

- Use point/nearest sampling when a crisp pixel grid is desired; inspect the target engine's filtering, compression and mipmap settings.
- For sheets, slice using actual frame rectangles from the generated metadata. Do not assume zero padding, uniform file names or a fixed number of columns.
- Preserve per-frame durations when constructing an animation. A fixed FPS cannot represent intentional holds exactly.
- Keep atlas padding and display scaling separate: padding protects frame edges, while sampling/scale controls how they appear on screen.
- Ask which engine/version is targeted before generating engine-specific code. This guide does not promise a Unity/Godot/Phaser-specific JSON schema or reuse unverified SDK examples.

The [copy-and-export recipe](examples.md#complete-export-recipe) demonstrates native-source preservation, 2× pixel scaling and real sheet metadata rather than an invented export option.
