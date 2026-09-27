# Image sequences and reference analysis

Use the [wire contract](MCP_TOOLS.md) and existing [success warning rules](MCP_WARNINGS.md).

## Exported file lists

`export_sprite` with frame_number=0 and a multi-frame sprite produces a sequence
for PNG/JPG/BMP: `walk007.png` becomes `walk007_0001.png`, `walk007_0002.png`, etc.
The original numeric suffix remains part of the stem. The response's optional
`files` array lists all actual `{path, file_size, frame_number}` entries in source
frame order (frame numbers start at 1).

When a nonempty files array is returned, inspect and report **every entry**, including
its source frame and actual path. The legacy `exported_path` and `file_size` identify
only the first file; they are not the base path and are not an aggregate size. Sum
entry sizes only if reporting a labeled total. Do not infer paths or glob the directory:
existing base files and older sequence files outside this returned list are preserved.

A selected frame, one-frame sprite, or animated GIF returns the original two fields
without files. Accept older responses without files (and nullable schema values),
but verify the returned path instead of inventing a sequence. Existing clients already
preserve the whole result. `output_path` extension must match format; .jpeg is accepted
for jpg. There are still no direct scale/FPS/layer/tag/range/loop options.

Source/output aliases and invalid/read-only destinations are rejected. All new sequence
outputs are staged before publication; ordinary errors/cancellation attempt rollback.
If restoration fails, preserve and report the server's recovery/backup information.
Do not retry blindly, delete retained backups, claim successful rollback without evidence,
or promise undo. Replacement is atomic per file, not for the whole set under a crash
or power loss. Non-cooperating external writers and spritesheet texture+JSON have
separate protection limits. Single-frame images are RGB composites; original indexed
palette/index identity is not an export guarantee.

## Reference formats

`analyze_reference` supports PNG, JPEG, GIF, BMP and native .ase/.aseprite input.
PNG/JPEG/GIF keep the Go decoder path. Recognized BMP/native file signatures are
rendered through the configured supported Aseprite into a private temporary PNG;
the source is read-only and is not saved or converted in place.

Native analysis uses the visible composite of frame 1, including groups, opacity,
layer visibility and cel offsets. No frame-selection argument is exposed. GIF uses
the first decoded image, not full logical-canvas/animation compositing. Do not describe
these results as analysis of every frame. BMP/native require a supported Aseprite
runtime; do not silently relabel an unknown/corrupt file to force a decoder.
