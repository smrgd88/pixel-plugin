# Aseprite Pixel Art Plugin for Claude Code

Create, animate, and export pixel art using Aseprite through natural language and commands in Claude Code.

*Powered by [pixel-mcp](https://github.com/willibrandon/pixel-mcp) - a Model Context Protocol server for Aseprite.*

## Features

**Natural Language Pixel Art Creation**
- "Create a 64x64 Game Boy style sprite"
- "Draw a red circle with blue outline"
- "Make a 16x16 tile"

**Animation Support**
- "Add a 4-frame walk cycle"
- "Create an idle animation"
- "Set frame timing to 100ms"

**Advanced Techniques**
- Apply dithering patterns
- Optimize color palettes
- Add shading and antialiasing
- Use retro console palettes (NES, Game Boy, C64, PICO-8)

**Game-Ready Export**
- PNG, GIF, spritesheet formats
- Aseprite JSON metadata for game-engine adaptation
- Pixel-perfect scaling (2x, 4x, 8x)
- Multiple spritesheet layouts

## How It Works

This plugin uses the [pixel-mcp](https://github.com/willibrandon/pixel-mcp) Model Context Protocol server to communicate with Aseprite. The MCP server provides 50 tools for pixel art operations and is bundled with the plugin.

## Quick Start

### 1. Prerequisites

- [Aseprite](https://www.aseprite.org/) v1.3.17.2+ installed
- [Claude Code](https://claude.com/code) installed

### 2. Installation

**Option A: Via Claude Code (recommended)**

In Claude Code, run:
```
/plugin
```
Then:
1. Select "Add marketplace"
2. Enter: `willibrandon/pixel-plugin` (for GitHub) or `./path/to/local/marketplace` (for local)
3. Select "Browse and install plugins"
4. Find and install `pixel-plugin`

**Option B: From command line**

```bash
# Add the GitHub marketplace
claude plugin marketplace add willibrandon/pixel-plugin

# Install the plugin
claude plugin install pixel-plugin
```

**Option C: Local development/testing**

```bash
# Clone the repository
git clone https://github.com/willibrandon/pixel-plugin.git
cd pixel-plugin

# Add as local marketplace (from parent directory)
cd ..
claude plugin marketplace add ./pixel-plugin

# Install from local source
claude plugin install pixel-plugin@pixel-plugin
```

### 3. Setup

Configure Aseprite path (one-time setup):

```bash
/pixel-setup
```

The command will auto-detect your Aseprite installation. If not found, specify the path manually:

```bash
/pixel-setup /Applications/Aseprite.app/Contents/MacOS/aseprite
```

### 4. Create Your First Sprite

```bash
# Using slash commands
/pixel-new 64x64 gameboy
"Draw a character sprite"
/pixel-export png character.png

# Or natural language only
"Create a 32x32 Game Boy sprite of a character"
"Export it as character.png"
```

## Usage

### Slash Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/pixel-new [size] [palette]` | Create new sprite | `/pixel-new icon nes` |
| `/pixel-palette <action> [args]` | Manage palettes | `/pixel-palette set gameboy` |
| `/pixel-export <format> [file]` | Export sprite | `/pixel-export gif anim.gif` |
| `/pixel-setup [path]` | Configure plugin | `/pixel-setup` |
| `/pixel-help [topic]` | Get help | `/pixel-help palettes` |

### Natural Language

The plugin responds to natural language requests:

**Creation:**
```
"Create a 64x64 RGB sprite"
"Make a 16x16 tile with NES palette"
"Start a new 128x128 canvas"
```

**Drawing:**
```
"Draw a red circle in the center"
"Fill the background with blue"
"Draw a pixelated tree"
```

**Animation:**
```
"Add 4 frames for a walk cycle"
"Create a 2-frame idle animation"
"Set all frame durations to 100ms"
```

**Advanced:**
```
"Apply Floyd-Steinberg dithering"
"Reduce to 16 colors"
"Add shading with light from top-left"
"Convert to PICO-8 palette"
```

**Export:**
```
"Export as PNG at 4x scale"
"Export as animated GIF at 12 FPS"
"Create a horizontal spritesheet"
"Export a spritesheet with Aseprite JSON metadata for Unity"
```

## Examples

### Example 1: Game Boy Character

```bash
/pixel-new 48x48 gameboy
"Draw a character sprite - round head, square body, stick limbs"
"Add a 2-frame breathing animation"
/pixel-export gif character-idle.gif fps=2
```

**Result:** Game Boy character with subtle idle animation.

### Example 2: NES Tile

```bash
/pixel-new tile nes
"Draw a brick wall pattern"
"Apply Bayer dithering for texture"
/pixel-export png brick-tile.png scale=4
```

**Result:** Retro NES-style brick tile, scaled 4x for modern displays.

### Example 3: Modern Pixel Art

```bash
/pixel-new 64x64
"Draw a detailed sword with silver blade and gold hilt"
"Add shading from top-left light source"
"Apply soft antialiasing to edges"
/pixel-export png sword.png scale=2
```

**Result:** Modern pixel art with shading and antialiasing.

### Example 4: Animated Sprite for Game

```bash
/pixel-new 32x32 pico8
"Draw a simple character"
"Create an 8-frame run cycle"
"Set frames to 80ms each"
/pixel-export json game-character.json
```

**Result:** `game-character.png` spritesheet + `game-character.json` with Aseprite metadata; adapt it to the target engine.

## Palettes and exports

Read [palette presets](config/palettes.json) for gameboy, nes, pico8, db16, db32, c64, cga and retro (db16). Custom hex palettes are supported. Palette optimization uses the real quantize_palette tool and can preserve transparency or keep RGB mode.

Exports support still PNG, animated GIF and spritesheets with horizontal, vertical, rows, columns or packed layouts. A command-level grid request maps to rows. JSON is Aseprite metadata alongside a sheet, not an engine-specific format. Scale and FPS options create a native copy and transform/retime it before export; the server has no scale, FPS, tag-filter or loop export arguments. See [export details](skills/pixel-art-exporter/export-formats.md).

## Local MCP development

The bundled server and schemas are pinned to MCP behavior-repair commit `b166b166ddb63af1a0d843f2cf30ec38541529eb`. Build a local committed revision and select it through PIXEL_MCP_BINARY; no personal source paths are stored in the distribution. See [reproducible build and validation](docs/LOCAL_MCP.md), [tool contract](docs/MCP_TOOLS.md), and [synchronization audit](docs/MCP_SYNC.md).

## Documentation

- [Skills Reference](skills/) - Detailed Skill documentation
- [Commands Reference](commands/) - Slash command documentation

## Troubleshooting

### "Aseprite not found" Error

Run setup command:
```bash
/pixel-setup /path/to/aseprite
```

Platform-specific paths:
- **macOS**: `/Applications/Aseprite.app/Contents/MacOS/aseprite`
- **Linux**: `/usr/bin/aseprite`
- **Windows**: `C:\Program Files\Aseprite\Aseprite.exe`

### "MCP server not responding"

1. Verify Aseprite is installed and accessible
2. Check configuration: `cat ~/.config/pixel-mcp/config.json`
3. Re-run setup: `/pixel-setup`
4. Check binary permissions: `chmod +x bin/pixel-mcp`

### "Export failed" or "File not found"

- Ensure sprite is created before exporting
- Check output path is writable
- Verify format is supported (png, gif, sheet, json)

See [Known Issues](docs/KNOWN_ISSUES.md) for additional troubleshooting information.

## Platform Support

- macOS (Intel and Apple Silicon)
- Linux (x86_64 and ARM64)
- Windows (x86_64)

## Requirements

- **Aseprite**: v1.3.17.2 or higher
- **Claude Code**: v1.0.0 or higher
- **pixel-mcp**: MCP server (bundled) - [Source](https://github.com/willibrandon/pixel-mcp)

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Start work from the latest develop in a dedicated task branch/worktree. Test and review before integration; merge only when authorized.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
