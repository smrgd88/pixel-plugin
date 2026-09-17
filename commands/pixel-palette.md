---
description: Show, set, edit, analyze or quantize a sprite palette
argument-hint: <action> [args]
allowed-tools: Read, Write, Bash, mcp__aseprite__save_as, mcp__aseprite__get_sprite_info, mcp__aseprite__set_palette, mcp__aseprite__get_palette, mcp__aseprite__quantize_palette, mcp__aseprite__set_palette_color, mcp__aseprite__add_palette_color, mcp__aseprite__sort_palette, mcp__aseprite__analyze_palette_harmonies
---

# /pixel-palette

Parse `$ARGUMENTS` as an action plus its arguments. Resolve the sprite's absolute path from the current conversation or user input; there is no global active sprite. Read [palette presets](../config/palettes.json), [professional guidance](../skills/pixel-art-professional/SKILL.md) and [call examples](../skills/pixel-art-professional/examples.md).

| Action | Operation |
|---|---|
| `show` | `get_palette` with sprite_path; display returned colors and size |
| `set <preset or hex colors>` | `set_palette` with sprite_path and explicit colors array (1–256 colors) |
| `optimize <count> [algorithm=median_cut] [dither=false]` | `quantize_palette` with sprite_path, target_colors (2–256), algorithm (median_cut/kmeans/octree), dither; preserve_transparency and convert_to_indexed default true |
| `edit <index> <hex>` | `set_palette_color` with sprite_path, zero-based index and color |
| `add <hex>` | `add_palette_color`; report color_index |
| `sort <method>` | `sort_palette`, with hue/saturation/brightness/luminance and ascending=true |
| `analyze` | Read get_palette, then pass its colors as palette to analyze_palette_harmonies |
| `export <file>` | Read get_palette and write JSON colors, one-hex-per-line TXT, or GIMP GPL using Write; no palette-export MCP tool |

For GPL write `GIMP Palette`, a Name line, Columns line, `#`, then decimal R G B and a color name per row. Do not silently write GPL content into an unspecified `.pal` dialect; clarify the target format or offer `.gpl`/`.json`/`.txt`.

Quantization modifies artwork and normally converts it to indexed color. Its dither workflow can flatten/replace content; use `save_as` to preserve a native copy when needed and re-read sprite structure afterwards. Explain that effect and report actual quantized_colors, color_mode, palette and algorithm_used. Set optional convert_to_indexed=false when RGB preservation is requested. Palette editing returns mixed response shapes; follow [the contract](../docs/MCP_TOOLS.md), including uppercase Success for set/edit/sort.

Examples: `/pixel-palette set gameboy`, `/pixel-palette optimize 16 dither=true`, `/pixel-palette edit 1 #884422`, `/pixel-palette export palette.gpl`.
