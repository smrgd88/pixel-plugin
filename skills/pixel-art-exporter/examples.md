# Exporter call examples

Use a saved sprite with at least one drawn frame. For scaling or retiming, save_as a new native copy and use its returned file_path for subsequent calls. delete_frame/delete_layer are only for explicitly filtering that copy. The basic still export below selects frame 1; for an animated GIF set format to gif, output_path to /work/hero.gif and frame_number to 0.

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

## export_sprite

```mcp-example
{
  "name": "export_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "output_path": "/work/hero.png",
    "format": "png",
    "frame_number": 1
  }
}
```

## export_spritesheet

```mcp-example
{
  "name": "export_spritesheet",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "output_path": "/work/hero-sheet.png",
    "layout": "rows",
    "padding": 1,
    "include_json": true
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

## set_frame_duration

```mcp-example
{
  "name": "set_frame_duration",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "frame_number": 1,
    "duration_ms": 150
  }
}
```

## delete_frame

```mcp-example
{
  "name": "delete_frame",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "frame_number": 2
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

## get_palette

```mcp-example
{
  "name": "get_palette",
  "arguments": {
    "sprite_path": "/work/hero.aseprite"
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

## Complete export recipe

The `scaled-animation-export` recipe in [workflows.json](workflows.json) begins with a two-frame 16×16 native sprite. It saves a separate copy, scales only that copy, applies 150/100 ms timing, and exports a PNG, GIF and sheet with JSON. Check the original is still 16×16, the PNG is 32×32, the GIF has two frames and the sheet metadata preserves both durations.

Recipe JSON uses `{source}` for an existing absolute sprite path, `{output}` for a caller-selected output directory, and saved step results such as `{canvas.file_path}`. These are recipe substitutions, never literal MCP arguments. The runner resolves them before schema validation. Run `python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite` to validate the recipes with real files. The prerequisite fixture is created only by the test runner; production use must inspect the user's actual source.

After successful calls, report optional `warnings` using [the shared warning rules](../../docs/MCP_WARNINGS.md). Preserve unknown codes and accept older responses without this field.

Before adapting quantization calls, apply [single-frame, input-mode and actual-pixel validation rules](../../docs/MCP_COLOR_OPERATIONS.md). A returned palette size alone does not establish that the intended colors survived.

## All-frame image sequence

For a multi-frame sprite, report every returned `files` entry as described in [sequence handling](../../docs/MCP_EXPORT_ANALYSIS.md). `walk007.png` is a naming base, not the first output file.

```mcp-example
{"name":"export_sprite","arguments":{"sprite_path":"/work/walk.aseprite","output_path":"/work/walk007.png","format":"png","frame_number":0}}
```

## JPEG extension alias

```mcp-example
{"name":"export_sprite","arguments":{"sprite_path":"/work/walk.aseprite","output_path":"/work/walk.jpeg","format":"jpg","frame_number":1}}
```

## Filtered sequence and protected sheet

Independent examples. First query structure; replace zero revision and layer_id with current values. The sequence assumes source frames 3–4 exist; source numbering is retained. GIF cannot use these selectors.

```mcp-example
{
  "name": "export_sprite",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "output_path": "/work/walk.png",
    "format": "png",
    "frame_number": 0,
    "frame_start": 3,
    "frame_end": 4,
    "trim": true,
    "overwrite": false
  }
}
```

```mcp-example
{
  "name": "export_spritesheet",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "output_path": "/work/selected.png",
    "layout": "horizontal",
    "padding": 2,
    "include_json": false,
    "layer_id": "1",
    "expected_revision": "0000000000000000000000000000000000000000000000000000000000000000",
    "trim": true,
    "extrude": true,
    "border_padding": 0,
    "shape_padding": 0,
    "inner_padding": null,
    "overwrite": false
  }
}
```

### Executable selected-sheet-export recipe

Query layer/revision and export a selected trimmed/extruded sheet with three explicit-zero padding overrides; verify actual PNG and source-indexed JSON. The complete schema-checked sequence is in [workflows.json](workflows.json), executed by `bin/test-skill-workflows.py`.

## Trimmed packed output within the budget

Use a distinct destination. This example keeps one-pixel extrusion, overrides border/inner
padding to zero and leaves one pixel between shapes. Verify the returned PNG and actual
JSON; duplicate samples may share bounds but preserve source_frame_number and duration.
Aseprite 1.3.18.2+ uses exact packed planning; older supported versions may reject a set
that would fit. On budget rejection, narrow the source range without bypassing guards.

```mcp-example
{"name":"export_spritesheet","arguments":{"sprite_path":"/work/walk.aseprite","output_path":"/work/walk-packed.png","layout":"packed","padding":1,"include_json":true,"trim":true,"extrude":true,"border_padding":0,"inner_padding":0,"overwrite":false}}
```
