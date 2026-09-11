# Creation and editing reference

The [tool contract](../../docs/MCP_TOOLS.md) contains inputs, required fields and response shapes for every creator tool. [Examples](examples.md) show actual payloads.

- `scale_sprite` changes image dimensions in place; `resize_canvas` changes the canvas using a named anchor; `crop_sprite` crops to x/y/width/height. Use a saved copy for export-only transformations.
- `flip_sprite` and `rotate_sprite` accept target `sprite`, `layer` or `cel`, but no layer/frame selector. Prefer `sprite` when a specific layer/cel cannot be selected reliably through this file-based interface.
- Selection operations persist bounds in sprite metadata. Ellipse and compound masks are reduced to rectangular bounds across calls; do not promise exact multi-call masks. Selection persistence may replace existing `sprite.data`.
- `move_selection` moves the selection bounds, not artwork. `copy_selection` has no layer/frame arguments; it uses the batch process's active cel. Prefer `get_pixels` plus `draw_pixels` for explicitly targeted copies. Clipboard content is a hidden `__mcp_clipboard__` layer in the same sprite, not the system clipboard. Verify copied content and do not assume cross-file paste.
- `cut_selection` has explicit layer/frame parameters; `paste_clipboard` targets a layer/frame and optional x/y. Use on a copy when testing a complex selection workflow.
- Palette index zero and alpha are different concepts: pass explicit hex colors to drawing tools, then inspect indexed output if transparency matters.
