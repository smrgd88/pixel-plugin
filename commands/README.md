---
description: Overview of available pixel-plugin slash commands
argument-hint: [command]
allowed-tools: Read
---

# Commands

| Command | Purpose | Example |
|---|---|---|
| [pixel-new](pixel-new.md) | Create canvas and preset palette | `/pixel-new 32x32 gameboy` |
| [pixel-palette](pixel-palette.md) | Show/set/edit/sort/analyze/quantize/export palette | `/pixel-palette optimize 16 dither=true` |
| [pixel-export](pixel-export.md) | PNG/GIF/sheet, companion JSON, scale/FPS workflows | `/pixel-export sheet hero.png layout=rows` |
| [pixel-setup](pixel-setup.md) | Configure executable and health check | `/pixel-setup` |
| [pixel-help](pixel-help.md) | Topic help | `/pixel-help animation` |

Commands use `$ARGUMENTS`; each file declares the tools its implementation needs. Read [the contract](../docs/MCP_TOOLS.md) for server schemas and [presets](../config/palettes.json) for color arrays. Skills handle natural-language drawing, animation and professional techniques.
