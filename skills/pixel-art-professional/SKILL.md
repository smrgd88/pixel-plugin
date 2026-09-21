---
name: pixel-art-professional
description: Apply dithering, palette editing and quantization, automatic or palette-based shading, reference analysis and antialiasing to pixel art.
allowed-tools: Read, Bash, mcp__aseprite__get_sprite_info, mcp__aseprite__get_pixels, mcp__aseprite__draw_pixels, mcp__aseprite__get_palette, mcp__aseprite__set_palette, mcp__aseprite__set_palette_color, mcp__aseprite__add_palette_color, mcp__aseprite__sort_palette, mcp__aseprite__analyze_palette_harmonies, mcp__aseprite__analyze_reference, mcp__aseprite__draw_with_dither, mcp__aseprite__apply_shading, mcp__aseprite__apply_auto_shading, mcp__aseprite__quantize_palette, mcp__aseprite__suggest_antialiasing, mcp__aseprite__save_as
---

# Pixel Art Professional

Read [the shared MCP contract](../../docs/MCP_TOOLS.md) for exact inputs and output fields, then [examples.md](examples.md) for validated calls. Use the actual connected tool schema if it differs and report the server mismatch; never guess an unsupported tool or option.

Operations act on files, not the Aseprite GUI's current document. Keep the absolute `file_path` returned by canvas creation or save-as and pass it as `sprite_path`. Verify existing files with `get_sprite_info`; it returns dimensions, color mode, frame/layer counts and layer names, **not** frame durations or tags. Drawing coordinates are zero-based canvas coordinates. MCP frame numbers are one-based; only export's `frame_number: 0` means all frames. Include every required field, even when its description mentions a default.

Check MCP `isError` before reading `structuredContent` (or JSON text content). Responses are tool-specific: some legacy palette/shading tools return uppercase `Success`. Report actual returned values and inspect the affected pixels or output file before claiming success.

## Workflow

1. Inspect dimensions, layer/frame and palette. Save a copy before palette remapping or automatic shading when the source must be preserved.
2. Use `draw_with_dither` to fill a rectangular `region` with `color1`, `color2` and a supported `pattern`; it does not quantize an existing picture. For full-sprite color reduction use `quantize_palette` with `target_colors`, `algorithm` and `dither`. Optional `preserve_transparency` and `convert_to_indexed` default true. See [dithering-patterns.md](dithering-patterns.md).
3. For a hand-selected ramp use `apply_shading`, with a `palette` ordered darkest to lightest, `region`, light direction, intensity and style `pillow`, `smooth` or `hard`.
4. For generated shading use `apply_auto_shading` on the named layer/frame, with intensity 0–1, explicit `hue_shift`, and style `cell`, `smooth` or `soft`. Its styles differ from palette-based shading. Check `colors_added`, `palette`, and `regions_shaded`; on indexed sprites the MCP develop fix preserves palette colors rather than treating an index as RGBA.
5. Use `get_palette`, `set_palette`, `set_palette_color` (zero-based index), `add_palette_color`, and `sort_palette` for editing. `analyze_palette_harmonies` takes a color array, not a sprite path. `analyze_reference` takes a raster path and target dimensions; use PNG/JPEG/GIF inputs because the handler uses Go image decoding, despite its broad schema description.
6. Use `suggest_antialiasing` first with `auto_apply: false`; inspect `suggestions` and `total_edges`. Set `auto_apply: true` to apply smoothing, with `use_palette: true` for palette snapping. Verify `applied` and inspect pixels.

Read [reference.md](reference.md) for algorithm choices and response fields. Keep intentional hard edges on small sprites; antialiasing is optional.
