---
name: pixel-art-creator
description: Create and edit pixel art sprites, layers, shapes, selections and transforms. Use for new sprites, drawing, importing reference images, cropping, scaling or adding outlines.
allowed-tools: Read, Bash, mcp__aseprite__create_canvas, mcp__aseprite__add_layer, mcp__aseprite__delete_layer, mcp__aseprite__flatten_layers, mcp__aseprite__get_sprite_info, mcp__aseprite__draw_pixels, mcp__aseprite__draw_line, mcp__aseprite__draw_contour, mcp__aseprite__draw_rectangle, mcp__aseprite__draw_circle, mcp__aseprite__fill_area, mcp__aseprite__get_pixels, mcp__aseprite__set_palette, mcp__aseprite__get_palette, mcp__aseprite__import_image, mcp__aseprite__save_as, mcp__aseprite__downsample_image, mcp__aseprite__flip_sprite, mcp__aseprite__rotate_sprite, mcp__aseprite__scale_sprite, mcp__aseprite__crop_sprite, mcp__aseprite__resize_canvas, mcp__aseprite__apply_outline, mcp__aseprite__select_rectangle, mcp__aseprite__select_ellipse, mcp__aseprite__select_all, mcp__aseprite__deselect, mcp__aseprite__move_selection, mcp__aseprite__cut_selection, mcp__aseprite__copy_selection, mcp__aseprite__paste_clipboard
---

# Pixel Art Creator

Read [the shared MCP contract](../../docs/MCP_TOOLS.md) for exact inputs and output fields, then [examples.md](examples.md) for validated calls. Use the actual connected tool schema if it differs and report the server mismatch; never guess an unsupported tool or option.

Operations act on files, not the Aseprite GUI's current document. Keep the absolute `file_path` returned by canvas creation or save-as and pass it as `sprite_path`. Verify existing files with `get_sprite_info`; it returns dimensions, color mode, frame/layer counts and layer names, **not** frame durations or tags. Drawing coordinates are zero-based canvas coordinates. MCP frame numbers are one-based; only export's `frame_number: 0` means all frames. Include every required field, even when its description mentions a default.

Check MCP `isError` before reading `structuredContent` (or JSON text content). Responses are tool-specific: some legacy palette/shading tools return uppercase `Success`. Report actual returned values and inspect the affected pixels or output file before claiming success.

Read and apply [completed-operation warning handling](../../docs/MCP_WARNINGS.md): report every returned `warnings` message, including unknown codes, with the successful result. Warnings do not request approval, retry or undo; absent warnings do not guarantee lossless processing.

## Workflow

1. Choose dimensions and `rgb`, `grayscale` or `indexed`; create a canvas. For retro palettes, read [palette presets](../../config/palettes.json), then call `set_palette` with explicit hex colors. Preset names are plugin conveniences, not MCP arguments.
2. Read layer names. Add named layers for separate components and batch `draw_pixels` calls on a specified layer and frame. Supply `thickness` for lines, `closed` for contours, `filled` for shapes and `tolerance` for fills. Use `use_palette: true` when colors must snap to the palette.
3. Inspect small regions with `get_pixels`; follow `next_cursor` until absent for larger reads. Add outlines with `apply_outline`. Save the native file to the user's destination using `save_as` before the temporary canvas is discarded.
4. For image conversion, `downsample_image` returns a new `output_path`; `import_image` places an image at `position: {x,y}` in a named layer/frame. See [reference.md](reference.md) for transforms and selection limitations.

Use clear silhouettes and small palettes for tiny sprites. Separate foreground and background layers when later animation or editing needs them. Delete layers or flatten only as part of the requested edit; operate on a saved copy when preparing a destructive export transformation.
