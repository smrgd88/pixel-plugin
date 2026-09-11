# Animator call examples

Start with a saved sprite. The tag example assumes two frames. For link_cel, create the two frames first, add a new Shared layer, and draw pixels on Shared frame 1 only. Target frame 2 must have no cel on that layer. Do not execute delete_frame before an example requiring frame 2. DuplicateFrame returns new_frame_number, while AddFrame returns frame_number.

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

## add_frame

```mcp-example
{
  "name": "add_frame",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "duration_ms": 100
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

## duplicate_frame

```mcp-example
{
  "name": "duplicate_frame",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "source_frame": 1,
    "insert_after": 0
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

## create_tag

```mcp-example
{
  "name": "create_tag",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "tag_name": "idle",
    "from_frame": 1,
    "to_frame": 2,
    "direction": "pingpong"
  }
}
```

## delete_tag

```mcp-example
{
  "name": "delete_tag",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "tag_name": "idle"
  }
}
```

## link_cel

```mcp-example
{
  "name": "link_cel",
  "arguments": {
    "sprite_path": "/work/hero.aseprite",
    "layer_name": "Shared",
    "source_frame": 1,
    "target_frame": 2
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
