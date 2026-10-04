---
description: Export PNG, GIF or a spritesheet, with copy-based scaling and timing
argument-hint: <png|gif|sheet|json> [file] [options]
allowed-tools: Read, Bash, mcp__aseprite__get_sprite_info, mcp__aseprite__export_sprite, mcp__aseprite__export_spritesheet, mcp__aseprite__save_as, mcp__aseprite__scale_sprite, mcp__aseprite__set_frame_duration, mcp__aseprite__delete_frame, mcp__aseprite__delete_layer
---

# /pixel-export

Parse `$ARGUMENTS`, resolve the actual sprite_path, and read [exporter guidance](../skills/pixel-art-exporter/SKILL.md), [formats](../skills/pixel-art-exporter/export-formats.md) and [examples](../skills/pixel-art-exporter/examples.md).

| Request | Translation |
|---|---|
| `png [file] [frame=N]` | export_sprite with format=png, output_path, frame_number=N (default 1); frame=0 exports all PNG frames as a numbered sequence |
| `gif [file]` | export_sprite with format=gif, output_path, frame_number=0 (all) |
| `sheet [file] [layout=horizontal] [padding=0]` | export_spritesheet with layout, padding, include_json=true |
| `json [file.json]` | Export a companion PNG sheet with include_json=true and report both paths; no standalone JSON tool |
| `scale=N` | Save a native copy and scale_sprite with scale_x=N, scale_y=N, algorithm=nearest before export |
| `fps=N` | Save a native copy and set_frame_duration on each frame to round(1000/N) before export |

Default output names are sprite.png, animation.gif or spritesheet.png in the requested output directory (resolve absolute paths). Validate positive integer scale; positive FPS must produce a duration within 1–65535 ms. Validate frame selection against frame_count. Reject unsupported or malformed options instead of passing them to MCP.

A `grid` layout request maps to `rows`; MCP accepts horizontal, vertical, rows, columns, packed. Padding is 0–100 and affects border, shape and inner padding. There is no fixed grid-column parameter.

Never send scale, fps, loop, animation_tag, layer or an engine format to an export tool. For a requested known frame range or layer, work on a saved copy and remove other frames (descending indices) or layers. get_sprite_info does not list tags; obtain an unknown tag range from the user or real exported metadata. No loop override is exposed. Aseprite JSON is the only metadata format; engine adaptation requires reading the actual output.

When both scaling and timing changes are requested, create one separate native copy and apply both there. Reuse the original source for each independent resolution export, avoiding cumulative scaling. Do not overwrite the original with the working copy. Inspect output files; file_size=0 alone does not prove an export succeeded.

Examples: `/pixel-export png hero.png frame=1 scale=4`, `/pixel-export png walk007.png frame=0`, `/pixel-export gif idle.gif fps=12`, `/pixel-export sheet hero.png layout=rows padding=1`.

Report returned success `warnings` according to [the shared warning rules](../docs/MCP_WARNINGS.md), including unknown codes. For dry_run:true these describe potential apply effects with the original unchanged; otherwise they describe completed edit effects; do not retry or request approval because of a warning.

For an all-frame PNG sequence use `frame=0`. Follow [sequence output handling](../docs/MCP_EXPORT_ANALYSIS.md): report all actual `files[].path`, `files[].frame_number` and sizes, not only the first `exported_path`. Do not claim the requested base file was created. Keep single-file/older responses without `files` compatible.

Use [preview and recovery rules](../docs/MCP_SAFETY.md) for requested previews or undo; do not invent dry_run support on other tools.

Follow [error and request-tracing rules](../docs/MCP_ERRORS.md): report error.code and request_id, preserve error.recovery, and never automatically retry file_rollback_failed or delete its retained backups.
