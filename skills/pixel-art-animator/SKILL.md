---
name: pixel-art-animator
description: Create sprite animations with frames, timing, tags and native linked cels. Use for walk cycles, idle animations, frame duplication or shared cel content.
allowed-tools: Read, Bash, mcp__aseprite__get_sprite_info, mcp__aseprite__add_frame, mcp__aseprite__delete_frame, mcp__aseprite__duplicate_frame, mcp__aseprite__set_frame_duration, mcp__aseprite__create_tag, mcp__aseprite__delete_tag, mcp__aseprite__link_cel, mcp__aseprite__draw_pixels, mcp__aseprite__get_pixels, mcp__aseprite__save_as
---

# Pixel Art Animator

Read [the shared MCP contract](../../docs/MCP_TOOLS.md) for exact inputs and output fields, then [examples.md](examples.md) for validated calls. Use the actual connected tool schema if it differs and report the server mismatch; never guess an unsupported tool or option.

Operations act on files, not the Aseprite GUI's current document. Keep the absolute `file_path` returned by canvas creation or save-as and pass it as `sprite_path`. Verify existing files with `get_sprite_info`; it returns dimensions, color mode, frame/layer counts and layer names, **not** frame durations or tags. Drawing coordinates are zero-based canvas coordinates. MCP frame numbers are one-based; only export's `frame_number: 0` means all frames. Include every required field, even when its description mentions a default.

Check MCP `isError` before reading `structuredContent` (or JSON text content). Responses are tool-specific: some legacy palette/shading tools return uppercase `Success`. Report actual returned values and inspect the affected pixels or output file before claiming success.

## Workflow

1. Inspect the sprite and preserve its absolute path. `add_frame` requires `duration_ms` and returns `frame_number`; it may copy existing cel content. `duplicate_frame` requires `source_frame` and `insert_after` (0 appends), and returns `new_frame_number`.
2. Draw only in the intended layer/frame. Set each required frame duration explicitly with `set_frame_duration`; convert FPS to rounded `1000 / FPS` milliseconds within 1–65535.
3. Group known inclusive frame ranges with `create_tag`, supplying `tag_name`, `from_frame`, `to_frame`, and `direction` (`forward`, `reverse`, `pingpong`). Remove by `delete_tag`. There is no tag-list or frame-info tool: use known creation results or inspect the exported Aseprite metadata when needed.
4. Use `link_cel` for genuinely shared image data. The source cel must exist and the target cel must be absent. Duplicating or adding a populated frame is not a way to obtain an empty target cel. To construct a fresh shared layer, create the frames first, add the new layer, draw only its source cel, then link it into the other frame. Links can go forward or backward. Editing shared pixels affects the linked group; use independent duplicates for distinct poses.
5. Verify the rendered frames with `get_pixels` and save the native file. Read [reference.md](reference.md) for link checks and export boundaries. The exporter handles GIF and spritesheet output.

For a walk cycle, distinguish contact, passing and opposite-contact poses; duplicate as a starting point then edit the new frame. For idle cycles, vary only the intended details. Do not claim GUI playback or onion-skin control through this MCP.
