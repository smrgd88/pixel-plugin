# Aseprite Pixel Art for Codex and Claude Code

**English** | [한국어](README.ko.md)

Create, animate, and export pixel art with Aseprite through natural-language requests.
This repository provides four skill workflows, a bundled pixel-mcp server, and client guidance.
Start with the [Codex setup](#quick-start-with-codex); existing Claude Code packaging is
covered [separately](#using-claude-code).

This is the [smrgd88/pixel-plugin](https://github.com/smrgd88/pixel-plugin) development fork of
[willibrandon/pixel-plugin](https://github.com/willibrandon/pixel-plugin).
The bundled [pixel-mcp fork](https://github.com/smrgd88/pixel-mcp) derives from
[willibrandon/pixel-mcp](https://github.com/willibrandon/pixel-mcp).

## Current source status

The bundle provides **56 MCP tools**, pinned to
`65074051f5d3903124ead37367c7fc62d9e7e7f6` in [the source manifest](config/mcp-source.json).
It includes drawing, animation, palette operations, exports, temporary-copy previews,
saved-file snapshots, opt-in recorded undo, and error codes with request IDs.

These capabilities describe this checkout. A merge into `develop` does not publish a
release or update an installed plugin. An upstream marketplace installation can contain
a different bundle. See [latest bundle validation](docs/ERROR_TRACING_VALIDATION.md),
[fix status](docs/BUG_STATUS.md), and [known issues](docs/KNOWN_ISSUES.md).

## Quick start with Codex

### 1. Get the checkout

Requirements: Aseprite v1.3.17.2+, Codex CLI for the commands below, Git, and Bash for
the bundled launcher. The shell examples use macOS/Linux paths. Windows also needs
Bash to use the wrapper; see [configuration](config/README.md) for Windows path rules.
Go is only needed when rebuilding MCP; Python and test dependencies are needed for validation.

```bash
git clone --branch develop --single-branch https://github.com/smrgd88/pixel-plugin.git
cd pixel-plugin
```

For an existing checkout, use its root. `develop` moves; check out a reviewed plugin
commit when you need a reproducible bundle.

### 2. Configure Aseprite

Create or update `~/.config/pixel-mcp/config.json` with the real absolute executable path.
Preserve existing fields if the file already exists. Minimal macOS example:

```json
{
  "aseprite_path": "/Applications/Aseprite.app/Contents/MacOS/aseprite"
}
```

The server selects configuration in this order: `--config`, `PIXEL_MCP_CONFIG`, then the
user-home `.config/pixel-mcp/config.json`. JSON paths do not expand `~` or shell variables.
See [configuration](config/README.md) for the template, detection helper, and platform paths.

From the checkout root, verify the selected bundle and Aseprite:

```bash
bin/pixel-mcp --version
bin/pixel-mcp --health
```

Health checks runtime availability, not drawing. A `PIXEL_MCP_BINARY` override can select
a different server; inspect it when the reported source version differs from this checkout.

### 3. Connect the MCP server

Inspect existing Codex connections first:

```bash
codex mcp list
```

If `aseprite` is already registered or supplied by an installed plugin, verify that
connection before adding another. For a new CLI registration, run from this checkout:

```bash
codex mcp add aseprite -- "$PWD/bin/pixel-mcp"
codex mcp get aseprite
```

This registers an absolute launcher path in your Codex configuration. Keep the checkout
at that location while using the connection. If the server uses a non-default config,
include it explicitly when registering:

```bash
codex mcp add aseprite -- "$PWD/bin/pixel-mcp" --config /absolute/path/pixel-mcp-config.json
```

Choose the registration command that matches your configuration; do not run both.
For project-scoped configuration, Codex also supports `.codex/config.toml` in trusted
projects. See [the official MCP guide](https://developers.openai.com/codex/mcp).
Restart/reconnect the Codex session after changing MCP configuration.

### 4. Use the repository guidance

Start Codex from this repository's root:

```bash
codex
```

[AGENTS.md](AGENTS.md) gives Codex the project instructions and routes pixel-art tasks
to the appropriate `skills/*/SKILL.md`. It does not install skills or start an MCP server.
Codex's [instruction discovery](https://developers.openai.com/codex/guides/agents-md)
uses `AGENTS.md`; `CLAUDE.md` remains the Claude Code entrypoint.

The root `skills/` directory is retained for plugin packaging. A bare checkout does not
make those folders automatically discoverable as standalone Codex skills. This setup
uses AGENTS.md routing and explicit file reads. To use automatic discovery outside this
repository, follow [Codex skill discovery](https://developers.openai.com/codex/skills)
for `.agents/skills` or your installed plugin's setup, preserving supporting references.

Ask in natural language, for example:

```text
Create a 32x32 Game Boy-style sprite and save it as hero.aseprite.
Add four walk-cycle frames, each 100 ms long.
Export an animated GIF and a PNG spritesheet with Aseprite JSON metadata.
```

Prior isolated Codex CLI skill/MCP execution is recorded in the project validation docs.
Installed CLI discovery and the selected model workflow are covered separately in
[Codex installation validation](docs/CODEX_INSTALL_VALIDATION.md); app GUI behavior is not. The manual connection above does not rely on the
Claude-specific `.mcp.json` launcher variable.

### Install the local Codex plugin (CLI 0.160.0)

This checkout now includes a Codex compatibility manifest and a local marketplace.
To install the bundled skills and MCP connection together, run from a clean checkout:

```bash
codex plugin marketplace add "$PWD"
codex plugin add pixel-plugin@pixel-plugin-local
codex plugin list --marketplace pixel-plugin-local --json
```

These commands register/install the plugin in your Codex user configuration. The local
marketplace name is `pixel-plugin-local`, separate from the Claude marketplace. Restart
Codex after installation. The installed skills are `pixel-plugin:pixel-art-*`; the
server name remains `aseprite`. Check an existing `aseprite` registration before installing
so that a manual connection does not collide with the plugin's server.

[.codex-plugin/plugin.json](.codex-plugin/plugin.json) uses
[config/codex-mcp.json](config/codex-mcp.json): the server runs from the installed plugin
root and forwards `PIXEL_MCP_CONFIG` / `PIXEL_MCP_BINARY` when provided. The Claude
`.mcp.json` is still used by Claude Code. No personal executable or config path is bundled.

Installed CLI workflows on macOS ARM were verified using a separate test marketplace,
process-local settings, real Aseprite, and an installed cache. See
[Codex installation validation](docs/CODEX_INSTALL_VALIDATION.md) for exact scope.
App GUI installation and the other native platforms remain unverified.

## Features and workflows

| Workflow | Examples | Guide |
|---|---|---|
| Creation and editing | Canvases, layers, pixels, shapes, selections, transforms | [Creator](skills/pixel-art-creator/SKILL.md) |
| Animation | Frame timing, tags, native linked cels | [Animator](skills/pixel-art-animator/SKILL.md) |
| Color and refinement | Retro palettes, quantization, dithering, shading, antialiasing, reference analysis | [Professional](skills/pixel-art-professional/SKILL.md) |
| Export | PNG/GIF/JPG/BMP, frame sequences, spritesheets and Aseprite JSON | [Exporter](skills/pixel-art-exporter/SKILL.md) |

Operations use explicit sprite file paths, not the Aseprite GUI's active or unsaved document.
Save new canvases to a permanent native path when you want to keep them; creation initially
uses the server temporary directory.

Palette presets include gameboy, nes, pico8, db16, db32, c64, cga and retro (db16).
Use `draw_with_dither` for a two-color rectangular pattern; use `quantize_palette` to
reduce an existing single-frame raster sprite's colors, optionally with dithering.
See [palette presets](config/palettes.json) and [color-operation limits](docs/MCP_COLOR_OPERATIONS.md).

Exports support still images, numbered image sequences, animated GIFs and horizontal,
vertical, rows, columns or packed spritesheets. Scaling and FPS changes use a saved
copy; they are not direct export arguments. JSON metadata uses the Aseprite format and
needs adaptation for a game engine. See [export workflows](skills/pixel-art-exporter/export-formats.md)
and [sequence output handling](docs/MCP_EXPORT_ANALYSIS.md).

## Preview and recovery

| Request | Behavior and limits |
|---|---|
| Preview quantization, automatic shading, or flattening | Only these three operations support `dry_run`; the original stays unchanged and no permanent preview image is returned |
| Snapshot a saved sprite | Saves file bytes; snapshots expire after 7 days and share a 100-entry / 512 MiB store limit |
| Restore a snapshot | Replaces the existing original path and creates a backup snapshot first; cannot recreate a deleted source |
| Undo a recorded edit | Requires a retained history entry; `enable_history` defaults to `false`, with no redo or GUI undo integration |

Example: “Preview reducing this single-frame sprite to 16 colors without changing it.”
Enabling history is an explicit configuration choice and adds storage cost. It does not
record exports, new canvases, or every operation. Read [the recovery rules](docs/MCP_SAFETY.md).

## Using Claude Code

The existing `.claude-plugin/` manifests, `commands/`, `.mcp.json`, and [CLAUDE.md](CLAUDE.md)
remain available for Claude Code. From the checkout root:

```bash
claude --plugin-dir "$PWD"
```

For a persistent installation, register the local checkout and install its manifest name:

```bash
claude plugin marketplace add "$PWD"
claude plugin install pixel-plugin@pixel-plugin
```

The upstream and fork use the same marketplace name. Inspect the source in `/plugin`
if `pixel-plugin` is already registered. Installed plugins use a cache; pulling this
checkout does not update that copy. See [Claude Code's plugin guide](https://code.claude.com/docs/en/plugins)
and [installation guide](https://code.claude.com/docs/en/discover-plugins).

Enter these plugin commands inside Claude Code, not the shell or Codex:

| Command | Example |
|---|---|
| Setup | `/pixel-plugin:pixel-setup /absolute/path/to/aseprite` |
| New sprite | `/pixel-plugin:pixel-new 32x32 gameboy` |
| Palette | `/pixel-plugin:pixel-palette set pico8` |
| Export | `/pixel-plugin:pixel-export png hero.png scale=4` |
| Help | `/pixel-plugin:pixel-help palettes` |

These are Claude plugin commands. In Codex, use natural-language requests and the skill
guides instead; the files in `commands/` are workflow references, not registered Codex commands.

## Troubleshooting

- **Aseprite unavailable:** verify `aseprite_path` in the selected server configuration,
  then run `bin/pixel-mcp --health` from the checkout. See [configuration](config/README.md).
- **MCP unavailable in Codex:** inspect `codex mcp list` and `codex mcp get aseprite`,
  verify the absolute launcher path, and restart/reconnect after changes. A configured
  server entry alone does not prove a live MCP connection.
- **Unexpected server behavior:** compare `bin/pixel-mcp --version` with the source pin;
  check `PIXEL_MCP_BINARY` and the actual installed/registered path.
- **Operation failed:** report the returned error code and request ID when available.
  For `file_rollback_failed`, preserve all recovery references and backups and inspect
  them before retrying; some outputs may have changed. See [error handling](docs/MCP_ERRORS.md).

See [known issues](docs/KNOWN_ISSUES.md) for algorithm and validation limits.

## Examples and development

The [apple example](examples/apple/README.md) includes reproducible MCP generation,
checked-in assets, and an offline browser demo.

- [AGENTS.md](AGENTS.md): Codex project instructions, Git workflow, and skill routing
- [Local MCP development](docs/LOCAL_MCP.md): Reproducible builds and test commands
- [MCP tools](docs/MCP_TOOLS.md): Exact schemas for all 56 tools
- [Latest validation](docs/ERROR_TRACING_VALIDATION.md): Bundle checks and untested areas
- [Plugin roadmap](docs/ROADMAP.md): Milestones, ownership, and completion criteria
- [Next work](docs/NEXT_STEPS.md): Remaining integration and release work
- [Contributing](CONTRIBUTING.md): Development guidelines
- [Historical comparison](docs/reports/mcp22/REPORT.md): Palette/shading before and after

Bundled targets: macOS Intel/Apple Silicon, Linux x86_64/ARM64, and Windows x86_64.
The latest recorded native verification ran on macOS Apple Silicon; other targets were
cross-built and checksum-checked. Cross-builds are not native runtime tests.

## License

MIT. See [LICENSE](LICENSE).
