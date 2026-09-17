# MCP tool contract

Generated from the actual `tools/list` response at MCP source commit `b166b166ddb63af1a0d843f2cf30ec38541529eb`.
Regenerate with `python3 bin/render-mcp-reference.py` after reviewing a new snapshot.

Read the tool section needed for the task. All tool names use the `mcp__aseprite__` prefix in skills/commands.
Required fields come from JSON Schema, even if their descriptions mention defaults. Object and array child fields are included below.

This records what the server advertises. Handler limits and workflow caveats are documented in the domain references and [known issues](KNOWN_ISSUES.md).

MCP frame inputs start at 1, except export `frame_number: 0` (all frames) and duplicate `insert_after: 0` (append). Pixel coordinates and palette indices start at 0.

Use `structuredContent` after checking `isError`; clients exposing only text content must parse its JSON. `Success` and `success` are distinct response fields.

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
- [create_tag](#create_tag)
- [crop_sprite](#crop_sprite)
- [cut_selection](#cut_selection)
- [delete_frame](#delete_frame)
- [delete_layer](#delete_layer)
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
- [import_image](#import_image)
- [link_cel](#link_cel)
- [move_selection](#move_selection)
- [paste_clipboard](#paste_clipboard)
- [quantize_palette](#quantize_palette)
- [resize_canvas](#resize_canvas)
- [rotate_sprite](#rotate_sprite)
- [save_as](#save_as)
- [scale_sprite](#scale_sprite)
- [select_all](#select_all)
- [select_ellipse](#select_ellipse)
- [select_rectangle](#select_rectangle)
- [set_frame_duration](#set_frame_duration)
- [set_palette](#set_palette)
- [set_palette_color](#set_palette_color)
- [sort_palette](#sort_palette)
- [suggest_antialiasing](#suggest_antialiasing)

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

Extract structured data from reference images to guide pixel art creation. Performs k-means palette extraction, brightness/edge detection, and composition analysis. Returns palette sorted by hue/lightness, brightness map with quantized levels, edge map with major contours, composition guides (rule of thirds, focal points), and suggested dithering zones.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `reference_path` | string | yes | Path to reference image (.jpg, .png, .gif, .bmp, .aseprite) |
| `target_width` | integer | yes | Pixel art target width (1-65535) |
| `target_height` | integer | yes | Pixel art target height (1-65535) |
| `palette_size` | integer | no | Number of colors to extract (5-32, default: 16) |
| `brightness_levels` | integer | no | Quantize brightness into N levels (2-10, default: 5) |
| `edge_threshold` | integer | no | Edge detection sensitivity (0-255, default: 30) |

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

Automatically add shading to sprite based on light direction. Analyzes sprite geometry to identify surfaces/regions, determines which surfaces face toward/away from light, generates shadow and highlight colors for each base color (with optional hue shifting), and applies shading pixels with smooth transitions. Supports three styles: cell (hard-edged 2-3 bands), smooth (gradient with dithering), soft (subtle gradient). Indexed sprites preserve existing palette indices and the transparent index; distinct generated colors are appended when capacity allows, otherwise non-exact shades retain the original pixel index.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
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
| `layer_name` | string | yes | Name of the layer to draw on |
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

Fill a region with a dithering pattern to create smooth gradients and textures. Supports 16 patterns: Bayer matrix (bayer_2x2, bayer_4x4, bayer_8x8) for ordered dithering, Floyd-Steinberg error diffusion (floyd_steinberg) for high-quality gradients, checkerboard for 50/50 blends, and texture patterns (grass, water, stone, cloud, brick, dots, diagonal, cross, noise, horizontal_lines, vertical_lines) for organic effects. Use density parameter to control the ratio of color1 to color2 (0.0 = all color1, 1.0 = all color2, 0.5 = even mix). Essential for professional pixel art gradients and textures.

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
| `density` | number | no | Ratio of color1 to color2 (0.0-1.0, default: 0.5) |

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

Export sprite to common image formats (PNG, GIF, JPG, BMP).

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `output_path` | string | yes | Output file path for exported image |
| `format` | string | yes | Export format: png, gif, jpg, bmp |
| `frame_number` | integer | yes | Specific frame to export (0 = all frames, 1-based) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `exported_path` | string | yes | Path to the exported file |
| `file_size` | integer | yes | Size of exported file in bytes |

## export_spritesheet

Export animation frames as spritesheet with layout options.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |
| `output_path` | string | yes | Output file path for spritesheet |
| `layout` | string | yes | Spritesheet layout: horizontal, vertical, rows, columns, or packed |
| `padding` | integer | yes | Padding between frames in pixels (0-100) |
| `include_json` | boolean | yes | Include JSON metadata file |

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

Flatten all layers in a sprite into a single layer.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to the Aseprite sprite file |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
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

Automatically reduce sprite colors using industry-standard quantization algorithms. Supports three algorithms: median_cut (fast, balanced quality), kmeans (highest quality, slower), octree (very fast, good for photos). Can apply Floyd-Steinberg dithering for smoother gradients. Optionally converts to indexed color mode for true palette constraint or keeps RGB mode for flexible multi-pass workflows.

### Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `sprite_path` | string | yes | Path to source .aseprite file |
| `target_colors` | integer | yes | Target palette size (2-256) |
| `algorithm` | string | yes | Quantization algorithm: median_cut (default), kmeans, or octree |
| `dither` | boolean | yes | Apply Floyd-Steinberg dithering during quantization (default: false) |
| `preserve_transparency` | null/boolean | no | Keep transparent pixels transparent (default: true) |
| `convert_to_indexed` | null/boolean | no | Convert sprite to indexed color mode (default: true) |

### Output

| Field | Type | Required | Meaning |
|---|---|---|---|
| `success` | boolean | yes | Whether the operation succeeded |
| `original_colors` | integer | yes | Number of unique colors in original sprite |
| `quantized_colors` | integer | yes | Number of colors in quantized palette |
| `color_mode` | string | yes | Color mode after quantization (indexed or rgb) |
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
| `threshold` | integer | no | Edge detection sensitivity 0-255 (default: 128) |
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
