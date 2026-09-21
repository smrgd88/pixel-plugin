# Creator call examples

Create a canvas, retain its returned file_path, add Ink, draw and inspect, then save_as. Other calls below are independent alternatives with their own preconditions: reference.png must exist; destructive edits run on a copy; selection copy/cut must precede paste. See reference.md for mask persistence limits.

These are MCP tools/call payloads, not a script to run sequentially. Replace `/work/...` with real absolute paths and `Ink` with a verified layer name. Each `mcp-example` block is schema-checked by the plugin tests.

## create_canvas

```mcp-example
{
  "name": "create_canvas",
  "arguments": {
    "width": 16,
    "height": 16,
    "color_mode": "rgb"
  }
}
```

## add_layer

```mcp-example
{
  "name": "add_layer",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink"
  }
}
```

## delete_layer

```mcp-example
{
  "name": "delete_layer",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Unused"
  }
}
```

## flatten_layers

```mcp-example
{
  "name": "flatten_layers",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## get_sprite_info

```mcp-example
{
  "name": "get_sprite_info",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## draw_pixels

```mcp-example
{
  "name": "draw_pixels",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "pixels": [
      {
        "x": 2,
        "y": 3,
        "color": "#FF0000"
      }
    ],
    "use_palette": false
  }
}
```

## draw_line

```mcp-example
{
  "name": "draw_line",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "x1": 1,
    "y1": 1,
    "x2": 8,
    "y2": 4,
    "color": "#FFFFFF",
    "thickness": 1
  }
}
```

## draw_contour

```mcp-example
{
  "name": "draw_contour",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "points": [
      {
        "x": 1,
        "y": 1
      },
      {
        "x": 8,
        "y": 1
      },
      {
        "x": 4,
        "y": 8
      }
    ],
    "color": "#FFFFFF",
    "thickness": 1,
    "closed": true
  }
}
```

## draw_rectangle

```mcp-example
{
  "name": "draw_rectangle",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "x": 0,
    "y": 0,
    "width": 8,
    "height": 8,
    "color": "#C04040",
    "filled": true
  }
}
```

## draw_circle

```mcp-example
{
  "name": "draw_circle",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "center_x": 8,
    "center_y": 8,
    "radius": 3,
    "color": "#FFFFFF",
    "filled": false
  }
}
```

## fill_area

```mcp-example
{
  "name": "fill_area",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "x": 2,
    "y": 2,
    "color": "#408040",
    "tolerance": 0
  }
}
```

## get_pixels

```mcp-example
{
  "name": "get_pixels",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "x": 0,
    "y": 0,
    "width": 8,
    "height": 8,
    "page_size": 16
  }
}
```

## set_palette

```mcp-example
{
  "name": "set_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "colors": [
      "#000000",
      "#555555",
      "#AAAAAA",
      "#FFFFFF"
    ]
  }
}
```

## get_palette

```mcp-example
{
  "name": "get_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## import_image

```mcp-example
{
  "name": "import_image",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "image_path": "/work/reference.png",
    "position": {
      "x": 1,
      "y": 2
    }
  }
}
```

## save_as

```mcp-example
{
  "name": "save_as",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "output_path": "/work/hero-copy.aseprite"
  }
}
```

## downsample_image

```mcp-example
{
  "name": "downsample_image",
  "arguments": {
    "source_path": "/work/reference.png",
    "target_width": 16,
    "target_height": 16,
    "output_path": "/work/small.aseprite"
  }
}
```

## flip_sprite

```mcp-example
{
  "name": "flip_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "direction": "horizontal",
    "target": "sprite"
  }
}
```

## rotate_sprite

```mcp-example
{
  "name": "rotate_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "angle": 90,
    "target": "sprite"
  }
}
```

## scale_sprite

```mcp-example
{
  "name": "scale_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "scale_x": 2,
    "scale_y": 2,
    "algorithm": "nearest"
  }
}
```

## crop_sprite

```mcp-example
{
  "name": "crop_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "x": 0,
    "y": 0,
    "width": 8,
    "height": 8
  }
}
```

## resize_canvas

```mcp-example
{
  "name": "resize_canvas",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "width": 32,
    "height": 32,
    "anchor": "center"
  }
}
```

## apply_outline

```mcp-example
{
  "name": "apply_outline",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "color": "#000000",
    "thickness": 1
  }
}
```

## select_rectangle

```mcp-example
{
  "name": "select_rectangle",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "x": 0,
    "y": 0,
    "width": 8,
    "height": 8,
    "mode": "replace"
  }
}
```

## select_ellipse

```mcp-example
{
  "name": "select_ellipse",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "x": 0,
    "y": 0,
    "width": 8,
    "height": 8,
    "mode": "replace"
  }
}
```

## select_all

```mcp-example
{
  "name": "select_all",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## deselect

```mcp-example
{
  "name": "deselect",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## move_selection

```mcp-example
{
  "name": "move_selection",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "dx": 2,
    "dy": 1
  }
}
```

## cut_selection

```mcp-example
{
  "name": "cut_selection",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1
  }
}
```

## copy_selection

```mcp-example
{
  "name": "copy_selection",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
  }
}
```

## paste_clipboard

```mcp-example
{
  "name": "paste_clipboard",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "x": 4,
    "y": 4
  }
}
```

## Complete creation recipes

The executable recipes `heart`, `sword` and `layered-character` in [workflows.json](workflows.json) preserve the original icon/item/character approach with corrected MCP payloads. Heart uses the original 8×8 silhouette; sword builds blade, guard and handle; the character keeps background and actor separate. Each starts with create_canvas and carries the returned file_path. Read a recipe to adapt its composition rather than merely copying a single primitive.

Recipe JSON uses `{source}` for an existing absolute sprite path, `{output}` for a caller-selected output directory, and saved step results such as `{canvas.file_path}`. These are recipe substitutions, never literal MCP arguments. The runner resolves them before schema validation. Run `python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite` to validate the recipes with real files. The prerequisite fixture is created only by the test runner; production use must inspect the user's actual source.

After successful calls, report optional `warnings` using [the shared warning rules](../../docs/MCP_WARNINGS.md). Preserve unknown codes and accept older responses without this field.
