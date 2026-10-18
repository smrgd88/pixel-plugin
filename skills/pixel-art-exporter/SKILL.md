---
name: pixel-art-exporter
description: Export pixel art to PNG, animated GIF or selected spritesheets with trim/extrude, padding and Aseprite JSON metadata. Use for game assets, native save copies and scaled exports.
allowed-tools: Read, Bash, mcp__aseprite__get_sprite_structure, mcp__aseprite__get_sprite_tags, mcp__aseprite__get_sprite_info, mcp__aseprite__get_pixels, mcp__aseprite__export_sprite, mcp__aseprite__export_spritesheet, mcp__aseprite__save_as, mcp__aseprite__scale_sprite, mcp__aseprite__set_frame_duration, mcp__aseprite__delete_frame, mcp__aseprite__delete_layer, mcp__aseprite__get_palette, mcp__aseprite__quantize_palette, mcp__aseprite__create_snapshot, mcp__aseprite__list_snapshots, mcp__aseprite__restore_snapshot, mcp__aseprite__delete_snapshot, mcp__aseprite__list_operation_history, mcp__aseprite__undo_last_operation
---

# Pixel Art Exporter

Read [the shared MCP contract](../../docs/MCP_TOOLS.md) for exact inputs and output fields, then [examples.md](examples.md) for validated calls. Use the actual connected tool schema if it differs and report the server mismatch; never guess an unsupported tool or option.

Operations act on files, not the Aseprite GUI's current document. Keep the absolute `file_path` returned by canvas creation or save-as and pass it as `sprite_path`. Verify existing files with `get_sprite_info`; it returns dimensions, color mode, frame/layer counts and layer names, **not** frame durations or tags. Drawing coordinates are zero-based canvas coordinates. MCP frame numbers are one-based; only export's `frame_number: 0` means all frames. Include every required field, even when its description mentions a default.

Check MCP `isError` before reading `structuredContent` (or JSON text content). Responses are tool-specific: some legacy palette/shading tools return uppercase `Success`. Report actual returned values and inspect the affected pixels or output file before claiming success.

Follow [error and request-tracing rules](../../docs/MCP_ERRORS.md) for failures. Report the returned code and request ID; retain every error.recovery entry. On file_rollback_failed, stop automatic retries and preserve backups for manual inspection.

Read and apply [operation warning handling](../../docs/MCP_WARNINGS.md): report every returned `warnings` message, including unknown codes, with the successful result. For `dry_run:true`, describe potential apply effects and say the original is unchanged. Warnings do not request approval, retry or undo; absent warnings do not guarantee lossless processing.

Read [preview, snapshot and recorded undo rules](../../docs/MCP_SAFETY.md) before preview or recovery. Use actual returned IDs. History recording is opt-in and must not be enabled silently; a preview-only request must not become an applied edit.

Read [structure/revision editing](../../docs/MCP_STRUCTURE_EDITING.md) before addressing layers, cels or tags. Query → select actual IDs/revision → authorized mutation → requery; names are not structural IDs.

Read [output-specific export options](../../docs/MCP_EXPORT_OPTIONS.md) before selection, trim/extrude/padding or overwrite decisions. GIF rejects the new selectors. A sheet always creates/protects its JSON sidecar even when include_json=false.

## Workflow

1. Inspect the source path and frame count. Use `export_sprite` with distinct `sprite_path` and `output_path`, matching `format` (`png`, `gif`, `jpg`, `bmp`) and extension. Use a one-based frame for a still PNG, or `frame_number: 0` for all frames. PNG/JPG/BMP animations produce numbered files; GIF remains one animated file.
2. Use `export_spritesheet` with `layout` (`horizontal`, `vertical`, `rows`, `columns`, `packed`), `padding` 0–100 and explicit `include_json`. A requested grid maps to `rows`; fixed row/column counts are not exposed. Read `spritesheet_path`, `metadata_path`, `frame_count` from the response.
3. For scaled exports, `save_as` to a separate native copy, then `scale_sprite` with equal integer `scale_x`/`scale_y` and `algorithm: nearest`, then export that copy. No export tool accepts a `scale` argument.
4. For an FPS override, retime a saved native copy. No direct fps/scale/loop override exists. PNG/JPG/BMP and sheets accept mutually exclusive tag or frame_start/frame_end selectors; positive frame_number cannot combine with either. Use get_sprite_tags to disambiguate names; directions do not expand export order. For layer_id export, use get_sprite_structure and its expected_revision; refresh both on any working copy. GIF rejects new selectors/include_hidden/trim=true.
5. Sheets support trim/extrude and independent padding overrides. Omitted/null padding falls back; 0 remains 0. Native visible backgrounds retain canvas; some indexed-background textures become RGBA while source bytes stay unchanged. Read source_frame_number and output-relative frameTags in actual JSON. include_json controls metadata_path visibility; texture+JSON are always a protected set, including overwrite=false. Report recovery on failure; never promise crash atomicity.
6. If palette reduction is requested, follow [the color-operation contract](../../docs/MCP_COLOR_OPERATIONS.md). Inspect the affected pixels with `get_pixels`. Do not quantize a multi-frame animation; report the unsupported request without silently dropping frames.
7. Follow [sequence output handling](../../docs/MCP_EXPORT_ANALYSIS.md): read every returned `files` entry when present, verify each actual path and size, and report the full ordered list. `exported_path` and `file_size` describe only the first file, not the requested base path or total size. For older/single-file responses without `files`, verify the returned `exported_path`.

Read [export-formats.md](export-formats.md) for format limits and copy-based option handling. Use actual dimensions and file size in the result.
