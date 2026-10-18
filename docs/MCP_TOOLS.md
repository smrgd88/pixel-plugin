# MCP tool contract

Generated from the actual `tools/list` response at MCP source commit `99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8`.
Regenerate with `python3 bin/render-mcp-reference.py` after reviewing a new snapshot.

Read the tool section needed for the task. All tool names use the `mcp__aseprite__` prefix in skills/commands.
Required fields come from JSON Schema, even if their descriptions mention defaults. Object and array child fields are included below.

This records what the server advertises. Handler limits and workflow caveats are documented in the domain references and [known issues](KNOWN_ISSUES.md).

MCP frame inputs start at 1, except export `frame_number: 0` (all frames) and duplicate `insert_after: 0` (append). Pixel coordinates and palette indices start at 0.

Use `structuredContent` after checking `isError`; clients exposing only text content must parse its JSON. `Success` and `success` are distinct response fields.

Report optional success `warnings` according to [completed-operation warning handling](MCP_WARNINGS.md), including unknown codes. Missing warnings do not guarantee lossless processing.

For tool/JSON-RPC failures, request IDs and partial rollback recovery, follow [the error contract](MCP_ERRORS.md). Error results have no successful output schema.

For revision-guarded IDs/linked impact read [structure editing](MCP_STRUCTURE_EDITING.md). For format-specific selection, padding and protected output sets read [export options](MCP_EXPORT_OPTIONS.md).

## Index

- [add_frame](#add_frame)
- [add_layer](#add_layer)
- [add_palette_color](#add_palette_color)
- [analyze_palette_harmonies](#analyze_palette_harmonies)
- [analyze_reference](#analyze_reference)
- [apply_auto_shading](#apply_auto_shading)
- [apply_outline](#apply_outline)
- [apply_shading](#apply_shading)
- [copy_selection](#copy_selection)
- [create_canvas](#create_canvas)
- [create_layer_group](#create_layer_group)
- [create_snapshot](#create_snapshot)
- [create_tag](#create_tag)
- [crop_sprite](#crop_sprite)
- [cut_selection](#cut_selection)
- [delete_frame](#delete_frame)
- [delete_layer](#delete_layer)
- [delete_snapshot](#delete_snapshot)
- [delete_tag](#delete_tag)
- [deselect](#deselect)
- [downsample_image](#downsample_image)
- [draw_circle](#draw_circle)
- [draw_contour](#draw_contour)
- [draw_line](#draw_line)
- [draw_pixels](#draw_pixels)
- [draw_rectangle](#draw_rectangle)
- [draw_with_dither](#draw_with_dither)
- [duplicate_frame](#duplicate_frame)
- [export_sprite](#export_sprite)
- [export_spritesheet](#export_spritesheet)
- [fill_area](#fill_area)
- [flatten_layers](#flatten_layers)
- [flip_sprite](#flip_sprite)
- [get_palette](#get_palette)
- [get_pixels](#get_pixels)
- [get_sprite_info](#get_sprite_info)
- [get_sprite_structure](#get_sprite_structure)
- [get_sprite_tags](#get_sprite_tags)
- [import_image](#import_image)
- [link_cel](#link_cel)
- [list_operation_history](#list_operation_history)
- [list_snapshots](#list_snapshots)
- [move_layer](#move_layer)
- [move_selection](#move_selection)
- [paste_clipboard](#paste_clipboard)
- [quantize_palette](#quantize_palette)
- [resize_canvas](#resize_canvas)
- [restore_snapshot](#restore_snapshot)
- [rotate_sprite](#rotate_sprite)
- [save_as](#save_as)
- [scale_sprite](#scale_sprite)
- [select_all](#select_all)
- [select_ellipse](#select_ellipse)
- [select_rectangle](#select_rectangle)
- [set_cel_properties](#set_cel_properties)
- [set_frame_duration](#set_frame_duration)
- [set_layer_properties](#set_layer_properties)
- [set_palette](#set_palette)
- [set_palette_color](#set_palette_color)
- [set_tag_properties](#set_tag_properties)
- [sort_palette](#sort_palette)
- [suggest_antialiasing](#suggest_antialiasing)
- [undo_last_operation](#undo_last_operation)
- [unlink_cel](#unlink_cel)

## add_frame

Add a new frame to an existing Aseprite sprite. Returns the frame number (1-based index).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `duration_ms` | integer | yes | Frame duration in milliseconds (1-65535) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `frame_number` | integer | yes | Index of the created frame (1-based) |

## add_layer

Add a new layer to an existing Aseprite sprite. Returns success status.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name for the new layer |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the layer was added successfully |

## add_palette_color

Add a new color to the palette. The palette will be resized to accommodate the new color. Returns the index of the newly added color. Maximum palette size is 256 colors.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `color` | string | yes | Hex color to add (#RRGGBB format) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `color_index` | integer | yes | Index of the newly added color |

## analyze_palette_harmonies

Analyze color palette for harmonious relationships. Identifies complementary pairs (opposite colors on color wheel), triadic sets (3 evenly spaced colors), analogous groups (adjacent colors), and color temperature (warm/cool/neutral). Essential for creating professional, cohesive pixel art palettes based on color theory.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `palette` | null/array | yes | Array of hex colors to analyze (#RRGGBB format) |
| `palette[]` | string | — | Array item |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `complementary` | null/array | yes |  |
| `complementary[].color1` | string | yes |  |
| `complementary[].color2` | string | yes |  |
| `complementary[].contrast` | number | yes |  |
| `complementary[].description` | string | yes |  |
| `triadic` | null/array | yes |  |
| `triadic[].colors` | null/array | yes |  |
| `triadic[].colors[]` | string | — | Array item |
| `triadic[].balance` | number | yes |  |
| `triadic[].description` | string | yes |  |
| `analogous` | null/array | yes |  |
| `analogous[].colors` | null/array | yes |  |
| `analogous[].colors[]` | string | — | Array item |
| `analogous[].harmony` | number | yes |  |
| `analogous[].description` | string | yes |  |
| `temperature` | object | yes |  |
| `temperature.warm_colors` | null/array | yes |  |
| `temperature.warm_colors[]` | string | — | Array item |
| `temperature.cool_colors` | null/array | yes |  |
| `temperature.cool_colors[]` | string | — | Array item |
| `temperature.neutral_colors` | null/array | yes |  |
| `temperature.neutral_colors[]` | string | — | Array item |
| `temperature.dominant` | string | yes |  |
| `temperature.description` | string | yes |  |

## analyze_reference

Extract structured data from PNG, JPEG, GIF, BMP, or Aseprite reference images to guide pixel art creation. GIF uses the first decoded image; Aseprite uses the visible composite of frame 1. BMP and Aseprite require the configured supported Aseprite runtime. The reference is not modified. Performs k-means palette extraction, brightness/edge detection, and composition analysis. Returns palette sorted by hue/lightness, brightness map with quantized levels, edge map with major contours, composition guides (rule of thirds, focal points), and suggested dithering zones.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `reference_path` | string | yes | Path to PNG, JPEG, GIF, BMP, or Aseprite (.ase/.aseprite) reference; analyzes the first frame only |
| `target_width` | integer | yes | Pixel art target width (1-65535) |
| `target_height` | integer | yes | Pixel art target height (1-65535) |
| `palette_size` | integer | no | Number of colors to extract (5-32, default: 16) |
| `brightness_levels` | integer | no | Quantize brightness into N levels (2-10, default: 5) |
| `edge_threshold` | null/integer | no | Sobel edge threshold (0-255); omitted or null defaults to 30, explicit zero is preserved |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `palette` | null/array | yes |  |
| `palette[].color` | string | yes |  |
| `palette[].hue` | number | yes |  |
| `palette[].saturation` | number | yes |  |
| `palette[].lightness` | number | yes |  |
| `palette[].usage_percent` | number | yes |  |
| `palette[].role` | string | yes |  |
| `brightness_map` | null/object | yes |  |
| `brightness_map.grid` | null/array | yes |  |
| `brightness_map.grid[]` | ['null', 'array'] | — | Array item |
| `brightness_map.legend` | object | yes |  |
| `edge_map` | null/object | yes |  |
| `edge_map.grid` | null/array | yes |  |
| `edge_map.grid[]` | ['null', 'array'] | — | Array item |
| `edge_map.major_edges` | null/array | yes |  |
| `edge_map.major_edges[].from` | object | yes |  |
| `edge_map.major_edges[].from.x` | integer | yes |  |
| `edge_map.major_edges[].from.y` | integer | yes |  |
| `edge_map.major_edges[].to` | object | yes |  |
| `edge_map.major_edges[].to.x` | integer | yes |  |
| `edge_map.major_edges[].to.y` | integer | yes |  |
| `edge_map.major_edges[].strength` | number | yes |  |
| `composition` | null/object | yes |  |
| `composition.focal_points` | null/array | yes |  |
| `composition.focal_points[].x` | integer | yes |  |
| `composition.focal_points[].y` | integer | yes |  |
| `composition.focal_points[].weight` | number | yes |  |
| `composition.rule_of_thirds` | object | yes |  |
| `composition.rule_of_thirds.vertical_lines` | null/array | yes |  |
| `composition.rule_of_thirds.vertical_lines[]` | integer | — | Array item |
| `composition.rule_of_thirds.horizontal_lines` | null/array | yes |  |
| `composition.rule_of_thirds.horizontal_lines[]` | integer | — | Array item |
| `composition.rule_of_thirds.intersections` | null/array | yes |  |
| `composition.rule_of_thirds.intersections[].x` | integer | yes |  |
| `composition.rule_of_thirds.intersections[].y` | integer | yes |  |
| `composition.rule_of_thirds.intersections[].has_focal_point` | boolean | yes |  |
| `composition.dominant_region` | object | yes |  |
| `composition.dominant_region.x` | integer | yes |  |
| `composition.dominant_region.y` | integer | yes |  |
| `composition.dominant_region.width` | integer | yes |  |
| `composition.dominant_region.height` | integer | yes |  |
| `dithering_zones` | null/array | yes |  |
| `dithering_zones[].region` | object | yes |  |
| `dithering_zones[].region.x` | integer | yes |  |
| `dithering_zones[].region.y` | integer | yes |  |
| `dithering_zones[].region.width` | integer | yes |  |
| `dithering_zones[].region.height` | integer | yes |  |
| `dithering_zones[].type` | string | yes |  |
| `dithering_zones[].colors` | null/array | yes |  |
| `dithering_zones[].colors[]` | string | — | Array item |
| `dithering_zones[].pattern` | string | yes |  |
| `dithering_zones[].reason` | string | yes |  |
| `metadata` | null/object | yes |  |
| `metadata.source_dimensions` | object | yes |  |
| `metadata.source_dimensions.width` | integer | yes |  |
| `metadata.source_dimensions.height` | integer | yes |  |
| `metadata.target_dimensions` | object | yes |  |
| `metadata.target_dimensions.width` | integer | yes |  |
| `metadata.target_dimensions.height` | integer | yes |  |
| `metadata.scale_factor` | number | yes |  |
| `metadata.dominant_hue` | number | yes |  |
| `metadata.color_harmony` | string | yes |  |
| `metadata.contrast_ratio` | string | yes |  |

## apply_auto_shading

Automatically add shading to sprite based on light direction. Analyzes sprite geometry to identify surfaces/regions, determines which surfaces face toward/away from light, generates shadow and highlight colors for each base color (with optional hue shifting), and applies shading pixels with smooth transitions. Supports three styles: cell (hard-edged 2-3 bands), smooth (gradient with dithering), soft (subtle gradient). Indexed sprites preserve existing palette indices and the transparent index; distinct generated colors are appended when capacity allows, otherwise non-exact shades retain the original pixel index. Use dry_run=true to simulate on a disposable copy and return a before/after preview without modifying the source.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | Simulate on a disposable copy without modifying the source (default: false) |
| `sprite_path` | string | yes | Path to .aseprite file |
| `layer_name` | string | yes | Layer to apply shading to |
| `frame_number` | integer | yes | Frame number (1-based) |
| `light_direction` | string | yes | Light direction: top_left, top, top_right, left, right, bottom_left, bottom, bottom_right |
| `intensity` | number | yes | Shading intensity (0.0-1.0) |
| `style` | string | yes | Shading style: cell, smooth, or soft |
| `hue_shift` | boolean | yes | Apply hue shifting (shadows→cool, highlights→warm) default: true |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | True when only a temporary copy was modified |
| `preview` | null/object | no | Before/after state for a completed dry-run; omitted for actual edits |
| `preview.before` | object | yes | State of the temporary sprite before the operation |
| `preview.before.width` | integer | yes |  |
| `preview.before.height` | integer | yes |  |
| `preview.before.color_mode` | string | yes |  |
| `preview.before.frame_count` | integer | yes |  |
| `preview.before.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.before.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.after` | object | yes | State after simulating the operation |
| `preview.after.width` | integer | yes |  |
| `preview.after.height` | integer | yes |  |
| `preview.after.color_mode` | string | yes |  |
| `preview.after.frame_count` | integer | yes |  |
| `preview.after.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.after.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.would_change_file` | boolean | yes | Whether the simulated file bytes changed; not a semantic pixel comparison |
| `success` | boolean | yes | Whether the operation succeeded |
| `colors_added` | integer | yes | Number of colors added to palette |
| `palette` | null/array | yes | Final palette after shading |
| `palette[]` | string | — | Array item |
| `regions_shaded` | integer | yes | Number of regions shaded |

## apply_outline

Apply an outline effect to a layer at a specified frame. The outline is drawn around non-transparent pixels with configurable color and thickness.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to apply outline to |
| `frame_number` | integer | yes | Frame number (1-based index) |
| `color` | string | yes | Outline color in hex format (#RRGGBB or #RRGGBBAA) |
| `thickness` | integer | yes | Outline thickness in pixels (1-10) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |

## apply_shading

Apply palette-constrained shading to a region based on light direction. Automatically adjusts pixel colors to create highlights and shadows while staying within the provided palette. Supports smooth, hard, and pillow shading styles. Essential for adding depth and dimension to pixel art.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to apply shading to |
| `frame_number` | integer | yes | Frame number (1-based index) |
| `region` | object | yes | Rectangular region to apply shading to |
| `region.x` | integer | yes | X coordinate of top-left corner |
| `region.y` | integer | yes | Y coordinate of top-left corner |
| `region.width` | integer | yes | Width of region |
| `region.height` | integer | yes | Height of region |
| `palette` | null/array | yes | Array of hex colors ordered darkest to lightest (#RRGGBB format) |
| `palette[]` | string | — | Array item |
| `light_direction` | string | yes | Light direction: top_left, top, top_right, left, right, bottom_left, bottom, bottom_right |
| `intensity` | number | yes | Shading intensity (0.0-1.0) |
| `style` | string | yes | Shading style: pillow, smooth, or hard |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `Success` | boolean | yes |  |

## copy_selection

Copy the selected pixels to clipboard without removing them. Requires an active selection.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the copy was successful |

## create_canvas

Create a new Aseprite sprite with specified dimensions and color mode. Returns the path to the created .aseprite file.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `width` | integer | yes | Canvas width in pixels (1-65535) |
| `height` | integer | yes | Canvas height in pixels (1-65535) |
| `color_mode` | string | yes | Color mode: rgb, grayscale, or indexed |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `file_path` | string | yes | Absolute path to the created Aseprite file |

## create_layer_group

Create an empty group at an explicit parent and sibling index using a fresh structure revision. Empty parent_id is root. Rejects locked/non-group destinations. Does not move or delete layers. Requery structure after success.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file |
| `expected_revision` | string | yes | Fresh revision from get_sprite_structure |
| `name` | string | yes | Group name; empty and duplicate names allowed |
| `parent_id` | string | yes | Parent group ID in expected_revision; empty string means sprite root |
| `stack_index` | integer | yes | Required 1-based bottom-to-top insertion index, 1 through child count plus one |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `layer` | object | yes |  |
| `layer.layer_id` | string | yes |  |
| `layer.parent_id` | string | yes |  |
| `layer.name` | string | yes |  |
| `layer.kind` | string | yes |  |
| `layer.stack_index` | integer | yes |  |
| `layer.visible` | boolean | yes |  |
| `layer.editable` | boolean | yes |  |
| `layer.effective_visible` | boolean | yes |  |
| `layer.effective_editable` | boolean | yes |  |
| `layer.opacity` | null/integer | no |  |
| `layer.blend_mode` | string | no |  |

## create_snapshot

Save a byte-exact recovery copy of a saved sprite. Persists across server restarts for 7 days; store limit 100 snapshots / 512 MiB. Does not capture unsaved editor changes.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path of the saved sprite to copy byte-for-byte; unsaved editor changes are not included |
| `label` | string | no | Optional label, at most 256 UTF-8 bytes |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `snapshot` | object | yes |  |
| `snapshot.operation` | null/object | no |  |
| `snapshot.operation.operation_id` | string | yes |  |
| `snapshot.operation.tool` | string | yes |  |
| `snapshot.operation.sequence` | integer | yes |  |
| `snapshot.operation.created_at` | string | yes |  |
| `snapshot.operation.state` | string | yes |  |
| `snapshot.operation.before_sha256` | string | yes |  |
| `snapshot.operation.after_sha256` | string | yes |  |
| `snapshot.snapshot_id` | string | yes |  |
| `snapshot.sprite_path` | string | yes |  |
| `snapshot.created_at` | string | yes |  |
| `snapshot.expires_at` | string | yes |  |
| `snapshot.size_bytes` | integer | yes |  |
| `snapshot.sha256` | string | yes |  |
| `snapshot.label` | string | no |  |

## create_tag

Create an animation tag to define a named frame range with playback direction.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `tag_name` | string | yes | Name for the animation tag |
| `from_frame` | integer | yes | Starting frame number (1-based, inclusive) |
| `to_frame` | integer | yes | Ending frame number (1-based, inclusive) |
| `direction` | string | yes | Playback direction: forward, reverse, or pingpong |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the tag was created successfully |

## crop_sprite

Crop a sprite to a specified rectangular region. The crop bounds must be within the sprite dimensions.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `x` | integer | yes | Crop region X coordinate |
| `y` | integer | yes | Crop region Y coordinate |
| `width` | integer | yes | Crop region width (must be positive) |
| `height` | integer | yes | Crop region height (must be positive) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |

## cut_selection

Cut the selected pixels to clipboard. Removes pixels from the specified layer and frame, placing them on the clipboard. Requires an active selection.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to cut from |
| `frame_number` | integer | yes | Frame number to cut from (1-based index) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the cut was successful |

## delete_frame

Delete a frame from an existing sprite. Cannot delete the last remaining frame.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the sprite file |
| `frame_number` | integer | yes | Frame number to delete (1-based) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the frame was deleted successfully |

## delete_layer

Delete a layer from an existing sprite. Cannot delete the last remaining layer.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the sprite file |
| `layer_name` | string | yes | Name of the layer to delete |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the layer was deleted successfully |

## delete_snapshot

Permanently delete one recovery copy by UUID. Does not change the original sprite. Unknown IDs return an error.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `snapshot_id` | string | yes | UUID of the snapshot to permanently delete |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `snapshot_id` | string | yes |  |

## delete_tag

Delete an animation tag by name.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `tag_name` | string | yes | Name of the tag to delete |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Deletion success status |

## deselect

Clear the current selection. Removes any active selection from the sprite.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether deselect was successful |

## downsample_image

Downsample an image to smaller dimensions using box filter (area averaging) algorithm. Accepts any image format supported by Aseprite (.aseprite, .png, .jpg, .bmp, .gif) and creates a new downsampled sprite. This is useful for creating pixel art versions of high-resolution images or reducing image size while maintaining quality.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `source_path` | string | yes | Path to source image file (.aseprite, .png, .jpg, .bmp, .gif) |
| `target_width` | integer | yes | Target width in pixels (1-65535) |
| `target_height` | integer | yes | Target height in pixels (1-65535) |
| `output_path` | string | no | Optional output path for downsampled sprite (defaults to temp directory) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `output_path` | string | yes | Path to the downsampled sprite file |
| `source_width` | integer | yes | Original source image width |
| `source_height` | integer | yes | Original source image height |
| `target_width` | integer | yes | Downsampled image width |
| `target_height` | integer | yes | Downsampled image height |

## draw_circle

Draw a circle with specified center, radius, color, and fill option.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `center_x` | integer | yes | X coordinate of circle center |
| `center_y` | integer | yes | Y coordinate of circle center |
| `radius` | integer | yes | Radius of circle in pixels |
| `color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `filled` | boolean | yes | Fill interior (true) or draw outline only (false) |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the circle was drawn successfully |

## draw_contour

Draw a polyline or polygon by connecting multiple points. Supports both open paths and closed shapes.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `points` | null/array | yes | Array of points to connect (minimum 2 points) |
| `points[].x` | integer | yes | X coordinate of the point |
| `points[].y` | integer | yes | Y coordinate of the point |
| `color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `thickness` | integer | yes | Line thickness in pixels (1-100) |
| `closed` | boolean | yes | Connect last point to first to form a closed polygon (default: false) |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the contour was drawn successfully |

## draw_line

Draw a line between two points with specified color and thickness.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `x1` | integer | yes | X coordinate of line start point |
| `y1` | integer | yes | Y coordinate of line start point |
| `x2` | integer | yes | X coordinate of line end point |
| `y2` | integer | yes | Y coordinate of line end point |
| `color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `thickness` | integer | yes | Line thickness in pixels (1-100) |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the line was drawn successfully |

## draw_pixels

Draw individual pixels at specified coordinates with colors. Supports batch operations for efficiency.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Unique exact raster layer name at any group depth; duplicate names are rejected |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `pixels` | null/array | yes | Array of pixels to draw |
| `pixels[].x` | integer | yes | X coordinate of the pixel |
| `pixels[].y` | integer | yes | Y coordinate of the pixel |
| `pixels[].color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `pixels_drawn` | integer | yes | Number of pixels successfully drawn |

## draw_rectangle

Draw a rectangle with specified position, size, color, and fill option.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `x` | integer | yes | X coordinate of rectangle top-left corner |
| `y` | integer | yes | Y coordinate of rectangle top-left corner |
| `width` | integer | yes | Width of rectangle in pixels |
| `height` | integer | yes | Height of rectangle in pixels |
| `color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `filled` | boolean | yes | Fill interior (true) or draw outline only (false) |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the rectangle was drawn successfully |

## draw_with_dither

Fill a region with one of 16 ordered, texture, or Floyd-Steinberg dithering patterns. Omitted or null density defaults to 0.5; explicit 0 fills color1 and 1 fills color2. Interior density values control ordered matrix thresholds or ranked texture coverage. Texture .5 preserves the legacy pattern, not necessarily a 50/50 ratio. Floyd density biases a horizontal gradient toward color2; .5 preserves the legacy gradient for widths greater than one. Exact rendered color ratios are not guaranteed.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `region` | object | yes | Rectangular region to fill with dithering |
| `region.x` | integer | yes | X coordinate of top-left corner |
| `region.y` | integer | yes | Y coordinate of top-left corner |
| `region.width` | integer | yes | Width of region |
| `region.height` | integer | yes | Height of region |
| `color1` | string | yes | First color (hex #RRGGBB or #RRGGBBAA) |
| `color2` | string | yes | Second color (hex #RRGGBB or #RRGGBBAA) |
| `pattern` | string | yes | Dithering pattern: bayer_2x2\|bayer_4x4\|bayer_8x8\|checkerboard\|floyd_steinberg\|grass\|water\|stone\|cloud\|brick\|dots\|diagonal\|cross\|noise\|horizontal_lines\|vertical_lines |
| `density` | null/number | no | Density threshold in [0,1]; omitted or null defaults to 0.5, 0 fills color1, 1 fills color2. Interior values bias the Floyd gradient or select ordered texture ranks; .5 retains the legacy pattern, coverage is pattern-dependent |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `Success` | boolean | yes |  |

## duplicate_frame

Duplicate an existing frame and insert it at the specified position.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `source_frame` | integer | yes | Frame number to duplicate (1-based) |
| `insert_after` | integer | yes | Insert duplicated frame after this frame number (1-based, 0 = insert at end) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `new_frame_number` | integer | yes | Index of the newly created frame (1-based) |

## export_sprite

Export sprite to PNG, GIF, JPG, or BMP. All-frame PNG/JPG/BMP exports use numbered files (stem_0001.ext etc.) and return files in frame order. exported_path and file_size identify the first real file. Single-frame exports and animated GIF retain a single output path. The output extension must match format. PNG/JPG/BMP support tag or inclusive frame range, revision-guarded layer/group selection and trim. GIF retains its existing frame_number behavior and rejects these new rendering options.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `tag` | null/string | no | Exact saved native tag name; mutually exclusive with frame range and nonzero frame_number |
| `layer_id` | string | no | Structural layer or group ID from get_sprite_structure; requires expected_revision |
| `expected_revision` | string | no | Saved SHA-256 revision; required with layer_id |
| `frame_start` | null/integer | no | First inclusive source frame, 1-based; omitted defaults to 1 |
| `frame_end` | null/integer | no | Last inclusive source frame; omitted defaults to last frame |
| `include_hidden` | boolean | no | Include hidden target and descendants; requires layer_id; default respects saved visibility |
| `trim` | boolean | no | Trim transparent frame margins; default false |
| `overwrite` | null/boolean | no | Replace existing planned outputs; omitted or null defaults to true; false rejects any existing destination |
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `output_path` | string | yes | Output file path; multi-frame PNG/JPG/BMP uses stem_0001.ext, stem_0002.ext, etc. |
| `format` | string | yes | Export format: png, gif, jpg, bmp |
| `frame_number` | integer | yes | Specific frame to export (0 = all frames, 1-based) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `exported_path` | string | yes | Path to the exported file; first file for an image sequence |
| `file_size` | integer | yes | Size of exported_path in bytes; first file only for a sequence |
| `files` | null/array | no | All generated files in frame order for a multi-file image sequence; omitted for single-file exports |
| `files[].path` | string | yes | Actual output file path |
| `files[].file_size` | integer | yes | Size of this file in bytes |
| `files[].frame_number` | integer | yes | Source frame number (1-based) |

## export_spritesheet

Export saved frames as a spritesheet with optional tag/frame range, revision-guarded layer/group selection, trim, extrude and individual padding. Texture and the legacy JSON sidecar are staged and published together with ordinary-error rollback. include_json controls metadata_path in the response; both outputs are always protected.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `tag` | null/string | no | Exact saved native tag name; mutually exclusive with frame_start/frame_end |
| `layer_id` | string | no | Structural layer or group ID from get_sprite_structure; requires expected_revision |
| `expected_revision` | string | no | Saved SHA-256 revision; required with layer_id |
| `frame_start` | null/integer | no | First inclusive source frame, 1-based; omitted defaults to 1 |
| `frame_end` | null/integer | no | Last inclusive source frame; omitted defaults to last frame |
| `include_hidden` | boolean | no | Include hidden target and descendants; requires layer_id; default respects saved visibility |
| `trim` | boolean | no | Trim transparent frame margins; visible native background keeps the full canvas; default false |
| `overwrite` | null/boolean | no | Replace existing planned outputs; omitted or null defaults to true; false rejects any existing destination |
| `extrude` | boolean | no | Repeat edge pixels by one pixel outside each sheet frame; default false |
| `border_padding` | null/integer | no | Sheet outer padding 0-100; overrides padding including explicit zero |
| `shape_padding` | null/integer | no | Space between sheet shapes 0-100; overrides padding including explicit zero |
| `inner_padding` | null/integer | no | Transparent inset inside each sheet frame 0-100; overrides padding including explicit zero |
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `output_path` | string | yes | Output file path for spritesheet |
| `layout` | string | yes | Spritesheet layout: horizontal, vertical, rows, columns, or packed |
| `padding` | integer | yes | Default border, shape and inner padding in pixels (0-100); individual options override |
| `include_json` | boolean | yes | Return metadata_path; the legacy JSON sidecar is always generated and protected |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `spritesheet_path` | string | yes | Path to exported spritesheet |
| `metadata_path` | null/string | no | Path to JSON metadata if included |
| `frame_count` | integer | yes | Number of frames in spritesheet |

## fill_area

Flood fill from a starting point with specified color (paint bucket tool).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to draw on |
| `frame_number` | integer | yes | Frame number to draw on (1-based) |
| `x` | integer | yes | X coordinate of starting point |
| `y` | integer | yes | Y coordinate of starting point |
| `color` | string | yes | Hex color string in format #RRGGBB or #RRGGBBAA |
| `tolerance` | integer | yes | Color matching tolerance (0-255, default 0) |
| `use_palette` | boolean | no | Snap colors to nearest palette color (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the fill operation was successful |

## flatten_layers

Flatten all layers in a sprite into a single layer. Use dry_run=true to simulate on a disposable copy and return a before/after preview without modifying the source.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | Simulate on a disposable copy without modifying the source (default: false) |
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | True when only a temporary copy was modified |
| `preview` | null/object | no | Before/after state for a completed dry-run; omitted for actual edits |
| `preview.before` | object | yes | State of the temporary sprite before the operation |
| `preview.before.width` | integer | yes |  |
| `preview.before.height` | integer | yes |  |
| `preview.before.color_mode` | string | yes |  |
| `preview.before.frame_count` | integer | yes |  |
| `preview.before.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.before.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.after` | object | yes | State after simulating the operation |
| `preview.after.width` | integer | yes |  |
| `preview.after.height` | integer | yes |  |
| `preview.after.color_mode` | string | yes |  |
| `preview.after.frame_count` | integer | yes |  |
| `preview.after.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.after.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.would_change_file` | boolean | yes | Whether the simulated file bytes changed; not a semantic pixel comparison |
| `warnings` | null/array | no | Potentially destructive effects of this completed operation; omitted when none apply |
| `warnings[].code` | string | yes | Stable warning code |
| `warnings[].message` | string | yes | Human-readable description of the operation's potential effect |
| `success` | boolean | yes | Whether the layers were flattened successfully |

## flip_sprite

Flip a sprite, layer, or cel horizontally or vertically. This operation mirrors the image content along the specified axis.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `direction` | string | yes | Flip direction: horizontal or vertical |
| `target` | string | yes | What to flip: sprite, layer, or cel (default: sprite) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |

## get_palette

Retrieve the current sprite palette as an array of hex colors. Returns both the color array and palette size. Useful for inspecting existing palettes before modification.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `colors` | null/array | yes | Array of hex colors in the palette |
| `colors[]` | string | — | Array item |
| `size` | integer | yes | Number of colors in the palette |

## get_pixels

Read pixel data from a rectangular region of a sprite. Returns an array of pixels with their coordinates and colors in hex format (#RRGGBBAA). Supports pagination for large regions using cursor and page_size parameters (default page size: 1000, max: 10000).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to read from |
| `frame_number` | integer | yes | Frame number to read from (1-based) |
| `x` | integer | yes | X coordinate of top-left corner of region |
| `y` | integer | yes | Y coordinate of top-left corner of region |
| `width` | integer | yes | Width of region to read |
| `height` | integer | yes | Height of region to read |
| `cursor` | string | no | Pagination cursor for fetching next page (optional) |
| `page_size` | integer | no | Number of pixels to return per page (default: 1000, max: 10000) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `pixels` | null/array | yes | Array of pixels with coordinates and colors |
| `pixels[].x` | integer | yes |  |
| `pixels[].y` | integer | yes |  |
| `pixels[].color` | string | yes |  |
| `next_cursor` | string | no | Cursor for fetching next page (empty if no more pages) |
| `total_pixels` | integer | yes | Total number of pixels in the region |

## get_sprite_info

Retrieve metadata about an existing Aseprite sprite including dimensions, color mode, frame count, layer count, and layer names.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `width` | integer | yes | Sprite width in pixels |
| `height` | integer | yes | Sprite height in pixels |
| `color_mode` | string | yes | Color mode (rgb, grayscale, or indexed) |
| `frame_count` | integer | yes | Number of frames in the sprite |
| `layer_count` | integer | yes | Number of layers in the sprite |
| `layers` | null/array | yes | Names of all layers in the sprite |
| `layers[]` | string | — | Array item |

## get_sprite_structure

Read saved layer hierarchy and frame/cel existence, bounds, opacity and native image sharing. Structural layer IDs are sibling-index paths valid while hierarchy order is unchanged; revision-guarded cel and layer/group editing tools accept these IDs; requery after every edit. Returns at most 100 layers x 100 frames, with exact layer filter and continuation offsets.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Saved sprite to inspect without saving or recording history |
| `layer_id` | string | no | Exact structural layer ID such as 2/1; does not include descendants |
| `layer_offset` | integer | no | Zero-based offset in matching depth-first layers; default 0 |
| `page_size` | integer | no | Layer page size; default 50, range 1-100 |
| `frame_start` | integer | no | First frame (1-based); default 1 |
| `frame_end` | integer | no | Last inclusive frame; default at most 100 frames from frame_start; maximum span 100 |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `revision` | string | yes |  |
| `width` | integer | yes |  |
| `height` | integer | yes |  |
| `color_mode` | string | yes |  |
| `frame_count` | integer | yes |  |
| `layer_count` | integer | yes |  |
| `matching_layer_count` | integer | yes |  |
| `frame_start` | integer | yes |  |
| `frame_end` | integer | yes |  |
| `next_frame_start` | integer | no |  |
| `next_layer_offset` | null/integer | no |  |
| `layers` | null/array | yes |  |
| `layers[].layer_id` | string | yes |  |
| `layers[].parent_id` | string | yes |  |
| `layers[].name` | string | yes |  |
| `layers[].name_path` | null/array | yes |  |
| `layers[].name_path[]` | string | — | Array item |
| `layers[].kind` | string | yes |  |
| `layers[].stack_index` | integer | yes |  |
| `layers[].visible` | boolean | yes |  |
| `layers[].editable` | boolean | yes |  |
| `layers[].effective_visible` | boolean | yes |  |
| `layers[].effective_editable` | boolean | yes |  |
| `layers[].opacity` | null/integer | no |  |
| `layers[].blend_mode` | string | no |  |
| `layers[].cels` | null/array | yes |  |
| `layers[].cels[].frame_number` | integer | yes |  |
| `layers[].cels[].exists` | boolean | yes |  |
| `layers[].cels[].x` | null/integer | no |  |
| `layers[].cels[].y` | null/integer | no |  |
| `layers[].cels[].width` | null/integer | no |  |
| `layers[].cels[].height` | null/integer | no |  |
| `layers[].cels[].opacity` | null/integer | no |  |
| `layers[].cels[].z_index` | null/integer | no |  |
| `layers[].cels[].image_ref` | string | no |  |
| `layers[].cels[].linked_cel_count` | integer | no |  |

## get_sprite_tags

Read all saved tags in native order with names, inclusive 1-based ranges, four playback directions, repeats and RGBA color. Duplicate/empty names are retained. tag_id is an array position valid only with this revision; no save or history.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Saved sprite to inspect without saving or recording history |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `revision` | string | yes |  |
| `frame_count` | integer | yes |  |
| `tags` | null/array | yes |  |
| `tags[].tag_id` | integer | yes |  |
| `tags[].name` | string | yes |  |
| `tags[].from_frame` | integer | yes |  |
| `tags[].to_frame` | integer | yes |  |
| `tags[].direction` | string | yes |  |
| `tags[].repeats` | integer | yes |  |
| `tags[].color` | string | yes |  |

## import_image

Import an external image file as a layer in the sprite.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `image_path` | string | yes | Path to image file to import |
| `layer_name` | string | yes | Layer name for imported image |
| `frame_number` | integer | yes | Frame number to place image (1-based) |
| `position` | null/object | no | Position to place image (optional defaults to 0,0) |
| `position.x` | integer | yes |  |
| `position.y` | integer | yes |  |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Import success status |

## link_cel

Create a linked cel that references another cel's image data, useful for animation optimization.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer |
| `source_frame` | integer | yes | Source frame with the cel to link (1-based) |
| `target_frame` | integer | yes | Target frame where linked cel will be created (1-based) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the cel was linked successfully |

## list_operation_history

List confirmed saved-file edits newest first, including undone entries. Automatic recording requires enable_history=true. History expires or disappears when its snapshot is expired or deleted. May reconcile a pending journal without modifying the sprite.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Original sprite path whose confirmed edit history to list |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `operations` | null/array | yes |  |
| `operations[].operation_id` | string | yes |  |
| `operations[].tool` | string | yes |  |
| `operations[].sequence` | integer | yes |  |
| `operations[].created_at` | string | yes |  |
| `operations[].state` | string | yes |  |
| `operations[].before_sha256` | string | yes |  |
| `operations[].after_sha256` | string | yes |  |
| `operations[].snapshot_id` | string | yes |  |
| `operations[].expires_at` | string | yes |  |
| `recording_enabled` | boolean | yes |  |

## list_snapshots

List unexpired recovery copies, oldest first. Performs lazy expiry cleanup. Optionally filter by original sprite path.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | no | Optional original sprite path filter; omit to list all unexpired snapshots |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `snapshots` | null/array | yes |  |
| `snapshots[].operation` | null/object | no |  |
| `snapshots[].operation.operation_id` | string | yes |  |
| `snapshots[].operation.tool` | string | yes |  |
| `snapshots[].operation.sequence` | integer | yes |  |
| `snapshots[].operation.created_at` | string | yes |  |
| `snapshots[].operation.state` | string | yes |  |
| `snapshots[].operation.before_sha256` | string | yes |  |
| `snapshots[].operation.after_sha256` | string | yes |  |
| `snapshots[].snapshot_id` | string | yes |  |
| `snapshots[].sprite_path` | string | yes |  |
| `snapshots[].created_at` | string | yes |  |
| `snapshots[].expires_at` | string | yes |  |
| `snapshots[].size_bytes` | integer | yes |  |
| `snapshots[].sha256` | string | yes |  |
| `snapshots[].label` | string | no |  |

## move_layer

Move/reorder an ordinary raster layer or whole group subtree at a fresh revision. Both source and destination IDs refer to that revision. Required stack_index is the final bottom-to-top sibling index. Empty parent_id is root. Rejects cycles, locked source/descendants/destination, special layers and no-op. All structural IDs must be requeried after success.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file |
| `expected_revision` | string | yes | Fresh revision from get_sprite_structure |
| `layer_id` | string | yes | Source structural ID in expected_revision |
| `parent_id` | string | yes | Destination group ID in expected_revision; empty string means sprite root |
| `stack_index` | integer | yes | Required final 1-based bottom-to-top index, after removing source from its old position |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `layer` | object | yes |  |
| `layer.layer_id` | string | yes |  |
| `layer.parent_id` | string | yes |  |
| `layer.name` | string | yes |  |
| `layer.kind` | string | yes |  |
| `layer.stack_index` | integer | yes |  |
| `layer.visible` | boolean | yes |  |
| `layer.editable` | boolean | yes |  |
| `layer.effective_visible` | boolean | yes |  |
| `layer.effective_editable` | boolean | yes |  |
| `layer.opacity` | null/integer | no |  |
| `layer.blend_mode` | string | no |  |

## move_selection

Move the current selection by a specified offset. Does not move the pixel content, only the selection bounds. Requires an active selection.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `dx` | integer | yes | Horizontal offset in pixels (can be negative) |
| `dy` | integer | yes | Vertical offset in pixels (can be negative) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the selection was moved successfully |

## paste_clipboard

Paste clipboard content onto the specified layer and frame. Optionally specify paste position (x, y). Requires clipboard to contain image data.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to paste onto |
| `frame_number` | integer | yes | Frame number to paste onto (1-based index) |
| `x` | null/integer | no | X coordinate for paste position (optional) |
| `y` | null/integer | no | Y coordinate for paste position (optional) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the paste was successful |

## quantize_palette

Reduce pixels to a quantized palette in single-frame sprites (tilemap layers are unsupported). Supports three algorithms: median_cut (fast, balanced quality), kmeans (highest quality, slower), octree (very fast, good for photos). Can apply Floyd-Steinberg dithering for smoother gradients. Always remaps pixels, even without dithering or indexed conversion. Non-dithered remapping preserves layers; dithering flattens them. Disabling indexed conversion preserves the input color mode. Palette size does not bound colors created by layer blending. Use dry_run=true to simulate on a disposable copy and return a before/after preview without modifying the source.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | Simulate on a disposable copy without modifying the source (default: false) |
| `sprite_path` | string | yes | Path to source .aseprite file |
| `target_colors` | integer | yes | Maximum palette entries (2-256); indexed output reserves a transparent index and supports at most 255 opaque entries |
| `algorithm` | string | yes | Quantization algorithm: median_cut (default), kmeans, or octree |
| `dither` | boolean | yes | Apply Floyd-Steinberg dithering during quantization (default: false) |
| `preserve_transparency` | null/boolean | no | Reserve a palette entry for fully transparent pixels (default: true); transparent pixels remain transparent in either setting |
| `convert_to_indexed` | null/boolean | no | Convert to indexed (default: true); false preserves the input color mode while still remapping pixels |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `dry_run` | boolean | no | True when only a temporary copy was modified |
| `preview` | null/object | no | Before/after state for a completed dry-run; omitted for actual edits |
| `preview.before` | object | yes | State of the temporary sprite before the operation |
| `preview.before.width` | integer | yes |  |
| `preview.before.height` | integer | yes |  |
| `preview.before.color_mode` | string | yes |  |
| `preview.before.frame_count` | integer | yes |  |
| `preview.before.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.before.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.after` | object | yes | State after simulating the operation |
| `preview.after.width` | integer | yes |  |
| `preview.after.height` | integer | yes |  |
| `preview.after.color_mode` | string | yes |  |
| `preview.after.frame_count` | integer | yes |  |
| `preview.after.layer_count` | integer | yes | All layer nodes including groups and hidden layers |
| `preview.after.palette_size` | integer | yes | Number of entries in the first palette |
| `preview.would_change_file` | boolean | yes | Whether the simulated file bytes changed; not a semantic pixel comparison |
| `warnings` | null/array | no | Potentially destructive effects of this completed operation; omitted when none apply |
| `warnings[].code` | string | yes | Stable warning code |
| `warnings[].message` | string | yes | Human-readable description of the operation's potential effect |
| `success` | boolean | yes | Whether the operation succeeded |
| `original_colors` | integer | yes | Number of unique colors in original sprite |
| `quantized_colors` | integer | yes | Number of colors in quantized palette |
| `color_mode` | string | yes | Color mode after quantization (indexed, rgb, or grayscale) |
| `palette` | null/array | yes | Array of hex colors in the quantized palette |
| `palette[]` | string | — | Array item |
| `algorithm_used` | string | yes | Quantization algorithm that was used |

## resize_canvas

Resize the canvas without scaling content. Content is positioned according to the anchor point (center, top_left, top_right, bottom_left, or bottom_right).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `width` | integer | yes | New canvas width (1-65535) |
| `height` | integer | yes | New canvas height (1-65535) |
| `anchor` | string | yes | Anchor position: center, top_left, top_right, bottom_left, or bottom_right (default: center) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |

## restore_snapshot

Replace the existing original sprite with verified snapshot bytes using atomic replacement. First creates a recovery snapshot of the current file; fails without replacing the source if backup capacity is unavailable. Unsaved editor changes are not included.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Existing writable original sprite path; must match the snapshot source |
| `snapshot_id` | string | yes | UUID returned by create_snapshot or list_snapshots |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `snapshot_id` | string | yes |  |
| `backup_snapshot` | object | yes | Pre-restore bytes, subject to the same expiry and storage limits |
| `backup_snapshot.operation` | null/object | no |  |
| `backup_snapshot.operation.operation_id` | string | yes |  |
| `backup_snapshot.operation.tool` | string | yes |  |
| `backup_snapshot.operation.sequence` | integer | yes |  |
| `backup_snapshot.operation.created_at` | string | yes |  |
| `backup_snapshot.operation.state` | string | yes |  |
| `backup_snapshot.operation.before_sha256` | string | yes |  |
| `backup_snapshot.operation.after_sha256` | string | yes |  |
| `backup_snapshot.snapshot_id` | string | yes |  |
| `backup_snapshot.sprite_path` | string | yes |  |
| `backup_snapshot.created_at` | string | yes |  |
| `backup_snapshot.expires_at` | string | yes |  |
| `backup_snapshot.size_bytes` | integer | yes |  |
| `backup_snapshot.sha256` | string | yes |  |
| `backup_snapshot.label` | string | no |  |

## rotate_sprite

Rotate a sprite, layer, or cel by 90, 180, or 270 degrees clockwise.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `angle` | integer | yes | Rotation angle: 90, 180, or 270 degrees |
| `target` | string | yes | What to rotate: sprite, layer, or cel (default: sprite) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |

## save_as

Save sprite to a new .aseprite file path.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `output_path` | string | yes | New .aseprite file path |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Save success status |
| `file_path` | string | yes | Path to saved file |

## scale_sprite

Scale a sprite by specified X and Y factors using a chosen algorithm (nearest, bilinear, or rotsprite). Returns the new dimensions.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `scale_x` | number | yes | Horizontal scale factor (0.01 to 100.0) |
| `scale_y` | number | yes | Vertical scale factor (0.01 to 100.0) |
| `algorithm` | string | yes | Scaling algorithm: nearest, bilinear, or rotsprite (default: nearest) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `warnings` | null/array | no | Potentially destructive effects of this completed operation; omitted when none apply |
| `warnings[].code` | string | yes | Stable warning code |
| `warnings[].message` | string | yes | Human-readable description of the operation's potential effect |
| `success` | boolean | yes |  |
| `new_width` | integer | yes | New sprite width after scaling |
| `new_height` | integer | yes | New sprite height after scaling |

## select_all

Select the entire canvas. This selects all pixels in the sprite, regardless of layers or frames.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether select all was successful |

## select_ellipse

Create an elliptical selection with specified mode (replace/add/subtract/intersect). The ellipse is defined by a bounding box.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `x` | integer | yes | X coordinate of selection ellipse bounding box |
| `y` | integer | yes | Y coordinate of selection ellipse bounding box |
| `width` | integer | yes | Width of selection ellipse (minimum 1) |
| `height` | integer | yes | Height of selection ellipse (minimum 1) |
| `mode` | string | yes | Selection mode: replace, add, subtract, or intersect (default: replace) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the selection was created successfully |

## select_rectangle

Create a rectangular selection with specified mode (replace/add/subtract/intersect). Selections define which pixels will be affected by editing operations.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `x` | integer | yes | X coordinate of selection rectangle |
| `y` | integer | yes | Y coordinate of selection rectangle |
| `width` | integer | yes | Width of selection rectangle (minimum 1) |
| `height` | integer | yes | Height of selection rectangle (minimum 1) |
| `mode` | string | yes | Selection mode: replace, add, subtract, or intersect (default: replace) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the selection was created successfully |

## set_cel_properties

Set existing raster cel position and/or opacity using a fresh get_sprite_structure revision. Negative/off-canvas coordinates allowed within signed 16-bit range. Rejects locked ancestors, group/tilemap/reference/background layers, absent cels and unchanged requests. Hidden layers allowed. Linked cels require allow_linked=true and change as a whole; never unlinks.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file to edit |
| `layer_id` | string | yes | Exact structural ID from get_sprite_structure, such as 2/1 |
| `frame_number` | integer | yes | Existing cel frame, 1-based |
| `expected_revision` | string | yes | Required revision from get_sprite_structure; refresh after every edit |
| `x` | null/integer | no | Sprite-absolute x, -32768 to 32767; omitted or null keeps current value |
| `y` | null/integer | no | Sprite-absolute y, -32768 to 32767; omitted or null keeps current value |
| `opacity` | null/integer | no | Cel opacity, 0 to 255; omitted or null keeps current value |
| `allow_linked` | boolean | no | Explicitly permit changing ALL cels sharing the native image; default false rejects linked cels |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `affected_cels` | null/array | yes |  |
| `affected_cels[].layer_id` | string | yes |  |
| `affected_cels[].frame_number` | integer | yes |  |
| `affected_cels[].x` | integer | yes |  |
| `affected_cels[].y` | integer | yes |  |
| `affected_cels[].opacity` | integer | yes |  |
| `warnings` | null/array | no |  |
| `warnings[].code` | string | yes | Stable warning code |
| `warnings[].message` | string | yes | Human-readable description of the operation's potential effect |

## set_frame_duration

Set the duration of an existing animation frame in milliseconds.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `frame_number` | integer | yes | Frame number to modify (1-based) |
| `duration_ms` | integer | yes | Frame duration in milliseconds (1-65535) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the frame duration was set successfully |

## set_layer_properties

Edit name, local visibility/editability, raster opacity/blend using a fresh structure revision. Ordinary raster/group only; hidden targets allowed. Locked ancestors rejected; a locally locked target accepts only editable=true (unlock first). Group opacity/blend unsupported. No-op rejected. Requery structure after success.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file |
| `expected_revision` | string | yes | Fresh revision from get_sprite_structure |
| `layer_id` | string | yes | Structural sibling-index path, e.g. 2/1 |
| `name` | null/string | no | New name; empty allowed; omitted or null keeps current value |
| `visible` | null/boolean | no | Local visibility; omitted or null keeps current value |
| `editable` | null/boolean | no | Local editability; false locks; omitted or null keeps current value |
| `opacity` | null/integer | no | Raster layer opacity 0-255; groups unsupported; omitted or null keeps current value |
| `blend_mode` | null/string | no | Native layer mode: normal, multiply, screen, overlay, darken, lighten, color_dodge, color_burn, hard_light, soft_light, difference, exclusion, hsl_hue, hsl_saturation, hsl_color, hsl_luminosity, addition, subtract, divide; groups unsupported |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `layer` | object | yes |  |
| `layer.layer_id` | string | yes |  |
| `layer.parent_id` | string | yes |  |
| `layer.name` | string | yes |  |
| `layer.kind` | string | yes |  |
| `layer.stack_index` | integer | yes |  |
| `layer.visible` | boolean | yes |  |
| `layer.editable` | boolean | yes |  |
| `layer.effective_visible` | boolean | yes |  |
| `layer.effective_editable` | boolean | yes |  |
| `layer.opacity` | null/integer | no |  |
| `layer.blend_mode` | string | no |  |

## set_palette

Set the sprite's color palette to the specified colors. Useful for applying extracted palettes from analyze_reference or creating custom limited palettes for pixel art. Colors should be in #RRGGBB hex format.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `colors` | null/array | yes | Array of hex colors to set as palette (#RRGGBB format) |
| `colors[]` | string | — | Array item |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `Success` | boolean | yes |  |

## set_palette_color

Set a specific palette index to a color. Index must be within the current palette range (0 to palette size - 1). Useful for modifying individual palette entries.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `index` | integer | yes | Palette index (0-255) |
| `color` | string | yes | Hex color to set (#RRGGBB format) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `Success` | boolean | yes |  |

## set_tag_properties

Edit an existing tag using get_sprite_tags tag_id and expected_revision. Supports name, inclusive range, direction and repeats; overlapping tags allowed. Empty/duplicate new names and unchanged requests rejected. Preserves existing empty/duplicate names when not renaming. Returns saved tag_id, which can change when range changes. Refresh tags after any edit.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file to edit |
| `tag_id` | integer | yes | 1-based tag_id from get_sprite_tags; not a permanent ID |
| `expected_revision` | string | yes | Required revision from get_sprite_tags; refresh after every edit |
| `name` | null/string | no | New nonblank name; rename to another tag's name is rejected; omitted/null keeps current value |
| `from_frame` | null/integer | no | First inclusive frame, 1-based; omitted/null keeps current value |
| `to_frame` | null/integer | no | Last inclusive frame, 1-based; omitted/null keeps current value |
| `direction` | null/string | no | forward, reverse, pingpong or pingpong_reverse; omitted/null keeps current value |
| `repeats` | null/integer | no | 0-65535; 0 is native unspecified (infinite UI, once on export); omitted/null keeps current value |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `tag` | object | yes |  |
| `tag.tag_id` | integer | yes |  |
| `tag.name` | string | yes |  |
| `tag.from_frame` | integer | yes |  |
| `tag.to_frame` | integer | yes |  |
| `tag.direction` | string | yes |  |
| `tag.repeats` | integer | yes |  |
| `tag.color` | string | yes |  |

## sort_palette

Sort the palette by hue, saturation, brightness, or luminance. Can sort in ascending or descending order. Useful for organizing palettes for easier color selection.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `method` | string | yes | Sort method: hue, saturation, brightness, or luminance |
| `ascending` | boolean | yes | Sort in ascending order (default: true) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `Success` | boolean | yes |  |

## suggest_antialiasing

Analyze pixel art for jagged diagonal edges and suggest intermediate colors to smooth them (antialiasing). Detects stair-step patterns on diagonals and calculates blended colors to create smoother curves. Use auto_apply to automatically apply suggestions or use_palette to constrain intermediate colors to the sprite's palette. Returns suggestions with positions, colors, and directions for manual review or automatic application.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `layer_name` | string | yes | Name of the layer to analyze |
| `frame_number` | integer | yes | Frame number to analyze (1-based) |
| `region` | null/object | no | Region to analyze (defaults to entire sprite) |
| `region.x` | integer | yes | X coordinate of top-left corner |
| `region.y` | integer | yes | Y coordinate of top-left corner |
| `region.width` | integer | yes | Width of region |
| `region.height` | integer | yes | Height of region |
| `threshold` | null/integer | no | Minimum edge contrast: max premultiplied RGBA channel difference must exceed this value (0-255); omitted or null defaults to 128 |
| `auto_apply` | boolean | no | If true applies smoothing automatically (default: false) |
| `use_palette` | boolean | no | If true snaps intermediate colors to palette (default: false) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `suggestions` | null/array | yes |  |
| `suggestions[].x` | integer | yes |  |
| `suggestions[].y` | integer | yes |  |
| `suggestions[].current_color` | string | yes |  |
| `suggestions[].neighbor_color` | string | yes |  |
| `suggestions[].suggested_color` | string | yes |  |
| `suggestions[].direction` | string | yes |  |
| `applied` | boolean | yes |  |
| `total_edges` | integer | yes |  |

## undo_last_operation

Undo the latest still-applied recorded edit by expected operation ID. Refuses external changes, missing/expired snapshots, and stale IDs. Creates a pre-undo snapshot subject to the same capacity and expiry policy; only saved-file changes are included.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Existing writable original sprite |
| `expected_operation_id` | string | yes | Latest applied operation_id from list_operation_history; guards retries and concurrent edits |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `operation` | object | yes |  |
| `operation.operation_id` | string | yes |  |
| `operation.tool` | string | yes |  |
| `operation.sequence` | integer | yes |  |
| `operation.created_at` | string | yes |  |
| `operation.state` | string | yes |  |
| `operation.before_sha256` | string | yes |  |
| `operation.after_sha256` | string | yes |  |
| `operation.snapshot_id` | string | yes |  |
| `operation.expires_at` | string | yes |  |
| `backup_snapshot` | object | yes |  |
| `backup_snapshot.operation` | null/object | no |  |
| `backup_snapshot.operation.operation_id` | string | yes |  |
| `backup_snapshot.operation.tool` | string | yes |  |
| `backup_snapshot.operation.sequence` | integer | yes |  |
| `backup_snapshot.operation.created_at` | string | yes |  |
| `backup_snapshot.operation.state` | string | yes |  |
| `backup_snapshot.operation.before_sha256` | string | yes |  |
| `backup_snapshot.operation.after_sha256` | string | yes |  |
| `backup_snapshot.snapshot_id` | string | yes |  |
| `backup_snapshot.sprite_path` | string | yes |  |
| `backup_snapshot.created_at` | string | yes |  |
| `backup_snapshot.expires_at` | string | yes |  |
| `backup_snapshot.size_bytes` | integer | yes |  |
| `backup_snapshot.sha256` | string | yes |  |
| `backup_snapshot.label` | string | no |  |

## unlink_cel

Detach exactly one existing raster cel from its native shared image using a fresh get_sprite_structure revision. Copies pixels and cel metadata without moving or converting them; other members retain sharing. Rejects independent/absent cels, locked ancestors and group/tilemap/reference/background targets. Hidden targets allowed. Returns the independent cel and former peers (a sole remaining peer is independent).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Native .aseprite or .ase file to edit |
| `layer_id` | string | yes | Exact structural ID from get_sprite_structure, such as 2/1 |
| `frame_number` | integer | yes | Existing linked cel frame, 1-based |
| `expected_revision` | string | yes | Required revision from get_sprite_structure; refresh after every edit |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes |  |
| `revision` | string | yes |  |
| `cel` | object | yes |  |
| `cel.layer_id` | string | yes |  |
| `cel.frame_number` | integer | yes |  |
| `remaining_linked_cels` | null/array | yes |  |
| `remaining_linked_cels[].layer_id` | string | yes |  |
| `remaining_linked_cels[].frame_number` | integer | yes |  |
