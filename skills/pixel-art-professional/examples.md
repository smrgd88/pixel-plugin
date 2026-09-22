# Professional call examples

Work on a copy of a drawn sprite with an Ink layer. Choose one technique at a time, inspect its response, and read back pixels/palette. Reference analysis requires a real raster image. A dither fill and full-image quantization are separate operations.

These are MCP tools/call payloads, not a script to run sequentially. Replace `/work/...` with real absolute paths and `Ink` with a verified layer name. Each `mcp-example` block is schema-checked by the plugin tests.

## get_sprite_info

```mcp-example
{
  "name": "get_sprite_info",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
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

## get_palette

```mcp-example
{
  "name": "get_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
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

## set_palette_color

```mcp-example
{
  "name": "set_palette_color",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "index": 1,
    "color": "#884422"
  }
}
```

## add_palette_color

```mcp-example
{
  "name": "add_palette_color",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "color": "#FFCC88"
  }
}
```

## sort_palette

```mcp-example
{
  "name": "sort_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "method": "luminance",
    "ascending": true
  }
}
```

## analyze_palette_harmonies

```mcp-example
{
  "name": "analyze_palette_harmonies",
  "arguments": {
    "palette": [
      "#000000",
      "#555555",
      "#AAAAAA",
      "#FFFFFF"
    ]
  }
}
```

## analyze_reference

```mcp-example
{
  "name": "analyze_reference",
  "arguments": {
    "reference_path": "/work/reference.png",
    "target_width": 16,
    "target_height": 16,
    "palette_size": 8
  }
}
```

## draw_with_dither

```mcp-example
{
  "name": "draw_with_dither",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "region": {
      "x": 0,
      "y": 0,
      "width": 8,
      "height": 8
    },
    "color1": "#000000",
    "color2": "#FFFFFF",
    "pattern": "bayer_4x4",
    "density": 0.5
  }
}
```

## apply_shading

```mcp-example
{
  "name": "apply_shading",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "region": {
      "x": 0,
      "y": 0,
      "width": 8,
      "height": 8
    },
    "palette": [
      "#000000",
      "#555555",
      "#AAAAAA",
      "#FFFFFF"
    ],
    "light_direction": "top_left",
    "intensity": 0.5,
    "style": "smooth"
  }
}
```

## apply_auto_shading

```mcp-example
{
  "name": "apply_auto_shading",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "light_direction": "top_left",
    "intensity": 0.5,
    "style": "cell",
    "hue_shift": true
  }
}
```

## quantize_palette

```mcp-example
{
  "name": "quantize_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "target_colors": 16,
    "algorithm": "median_cut",
    "dither": true,
    "preserve_transparency": true,
    "convert_to_indexed": true
  }
}
```

## suggest_antialiasing

```mcp-example
{
  "name": "suggest_antialiasing",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Ink",
    "frame_number": 1,
    "region": {
      "x": 0,
      "y": 0,
      "width": 8,
      "height": 8
    },
    "threshold": 128,
    "auto_apply": false,
    "use_palette": true
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

## Complete refinement recipes

The `steel-shading` and `manual-checker` recipes in [workflows.json](workflows.json) show the restored material-ramp and manual texture workflows. Steel starts with a flat midtone shape on Layer 1; use its explicit ramp and compare resulting colors. Manual checker expands the 4×4 A/B tile into exact pixel coordinates, making it suitable for deliberate texture placement. No nonexistent custom-pattern argument is sent.

Recipe JSON uses `{source}` for an existing absolute sprite path, `{output}` for a caller-selected output directory, and saved step results such as `{canvas.file_path}`. These are recipe substitutions, never literal MCP arguments. The runner resolves them before schema validation. Run `python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite` to validate the recipes with real files. The prerequisite fixture is created only by the test runner; production use must inspect the user's actual source.

After successful calls, report optional `warnings` using [the shared warning rules](../../docs/MCP_WARNINGS.md). Preserve unknown codes and accept older responses without this field.
