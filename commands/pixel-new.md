---
description: Create a sprite with a size and optional palette preset
argument-hint: [size] [palette]
allowed-tools: Read, Bash, mcp__aseprite__create_canvas, mcp__aseprite__set_palette, mcp__aseprite__get_sprite_info, mcp__aseprite__save_as
---

# /pixel-new

Parse `$ARGUMENTS` as `[size] [palette]`. Default size is medium (64x64); optional presets are icon=32x32, small=48x48, medium=64x64, large=128x128, tile=16x16, gameboy=160x144, nes=256x240. Explicit WIDTHxHEIGHT accepts positive dimensions up to 65535. Choose practical dimensions for available resources.

Read [palette definitions](../config/palettes.json). Supported palette names are gameboy, nes, pico8, db16, db32, c64, cga and retro (db16). The NES table has 64 entries including duplicates, not 54 unique colors. There is no single fixed SNES palette: request the desired colors when that label alone is ambiguous.

1. Call `create_canvas` with width, height and explicit `color_mode: rgb` unless the user asks for indexed/grayscale.
2. Store returned `file_path`; there is no output path input to canvas creation.
3. If a palette was requested, call `set_palette` with `sprite_path` equal to that path and `colors` equal to the preset's hex array. Inspect uppercase `Success`.
4. Verify with `get_sprite_info`. Report dimensions, mode, path and palette. If the user supplied a permanent native destination, call `save_as` with `sprite_path` and `output_path` and continue with returned `file_path`.

Read [creator examples](../skills/pixel-art-creator/examples.md) for validated payloads and [the contract](../docs/MCP_TOOLS.md) for exact schemas.

Examples: `/pixel-new`, `/pixel-new icon`, `/pixel-new 32x32 gameboy`, `/pixel-new tile pico8`.
