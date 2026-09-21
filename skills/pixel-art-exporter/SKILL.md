---
name: pixel-art-exporter
description: Export pixel art to PNG, animated GIF or spritesheets with Aseprite JSON metadata. Use for game assets, native save copies and scaled exports.
allowed-tools: Read, Bash, mcp__aseprite__get_sprite_info, mcp__aseprite__export_sprite, mcp__aseprite__export_spritesheet, mcp__aseprite__save_as, mcp__aseprite__scale_sprite, mcp__aseprite__set_frame_duration, mcp__aseprite__delete_frame, mcp__aseprite__delete_layer, mcp__aseprite__get_palette, mcp__aseprite__quantize_palette
---

# Pixel Art Exporter

Read [the shared MCP contract](../../docs/MCP_TOOLS.md) for exact inputs and output fields, then [examples.md](examples.md) for validated calls. Use the actual connected tool schema if it differs and report the server mismatch; never guess an unsupported tool or option.

Operations act on files, not the Aseprite GUI's current document. Keep the absolute `file_path` returned by canvas creation or save-as and pass it as `sprite_path`. Verify existing files with `get_sprite_info`; it returns dimensions, color mode, frame/layer counts and layer names, **not** frame durations or tags. Drawing coordinates are zero-based canvas coordinates. MCP frame numbers are one-based; only export's `frame_number: 0` means all frames. Include every required field, even when its description mentions a default.

Check MCP `isError` before reading `structuredContent` (or JSON text content). Responses are tool-specific: some legacy palette/shading tools return uppercase `Success`. Report actual returned values and inspect the affected pixels or output file before claiming success.

Read and apply [completed-operation warning handling](../../docs/MCP_WARNINGS.md): report every returned `warnings` message, including unknown codes, with the successful result. Warnings do not request approval, retry or undo; absent warnings do not guarantee lossless processing.

## Workflow

1. Inspect the source path and frame count. Use `export_sprite` with distinct `sprite_path` and `output_path`, matching `format` (`png`, `gif`, `jpg`, `bmp`) and extension. Use a one-based frame for a still PNG, or `frame_number: 0` for all GIF frames.
2. Use `export_spritesheet` with `layout` (`horizontal`, `vertical`, `rows`, `columns`, `packed`), `padding` 0–100 and explicit `include_json`. A requested grid maps to `rows`; fixed row/column counts are not exposed. Read `spritesheet_path`, `metadata_path`, `frame_count` from the response.
3. For scaled exports, `save_as` to a separate native copy, then `scale_sprite` with equal integer `scale_x`/`scale_y` and `algorithm: nearest`, then export that copy. No export tool accepts a `scale` argument.
4. For an FPS override, change every frame's `duration_ms` on that copy before exporting. Exports have no `fps`, `loop`, `animation_tag`, `layer` or frame-range argument. For a known frame range, save a copy and delete unwanted frames in descending order; for a layer-only export delete other layers from a copy. If a tag range is unknown, request its range or inspect real exported metadata rather than inventing a tag-list tool.
5. `include_json` requests Aseprite metadata alongside a sheet. Read the resulting JSON before engine adaptation; there is no engine-specific format selector or standalone metadata tool. Do not invent frame names or assume `frames` is an array.
6. Check the files exist and have content. `export_sprite` can return `file_size: 0` when its requested path does not exist (for example a numbered image sequence). Treat that as unverified output, not success.

Read [export-formats.md](export-formats.md) for format limits and copy-based option handling. Use actual dimensions and file size in the result.
