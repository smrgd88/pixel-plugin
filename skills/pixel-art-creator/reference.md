# Creation and editing reference

The [tool contract](../../docs/MCP_TOOLS.md) contains inputs, required fields and response shapes for every creator tool. [Examples](examples.md) show actual payloads.

- `scale_sprite` changes image dimensions in place; `resize_canvas` changes the canvas using a named anchor; `crop_sprite` crops to x/y/width/height. Use a saved copy for export-only transformations.
- `flip_sprite` and `rotate_sprite` accept target `sprite`, `layer` or `cel`, but no layer/frame selector. Prefer `sprite` when a specific layer/cel cannot be selected reliably through this file-based interface.
- Selection operations store row runs in the private `pixel-mcp/selection` extension-property namespace. User `sprite.data` is left byte-for-byte unchanged, including JSON nulls and empty objects. Legacy masks/bounds can be read; clearing a migrated mask will not restore stale legacy state on the next call. Older bounds-only data cannot regain a lost mask.
- `move_selection` moves the selection bounds, not artwork. `copy_selection` has no layer/frame arguments; it always reads the first layer and first frame. Prefer `get_pixels` plus `draw_pixels` for explicitly targeted copies. Clipboard content is a hidden `__mcp_clipboard__` layer in the same sprite, not the system clipboard. Verify copied content and do not assume cross-file paste.
- `cut_selection` has explicit layer/frame parameters; `paste_clipboard` targets a layer/frame and optional x/y. Use on a copy when testing a complex selection workflow.
- Palette index zero and alpha are different concepts: pass explicit hex colors to drawing tools, then inspect indexed output if transparency matters.

## Plan the sprite before choosing primitives

Use dimensions as a design budget, not a hardware promise: 8–16 pixels suit tiny UI symbols; 24–32 pixels allow recognizable item silhouettes; 32–64 pixels give a character room for readable limbs and animation; scenes need a larger canvas. Honor the user's chosen size. RGB with a small explicit palette is useful when alpha editing matters; choose indexed mode when actual indexed output is required.

At native size, establish the silhouette before interior detail. For a sword, separate blade, guard and handle; for a tree, separate trunk and foliage masses. Rectangles establish solid masses, contours outline irregular shapes, and a small batch of pixels supplies distinctive details. A one-pixel highlight should describe the object's shape, not compete with it.

Use Background, Character and Effects layers when those elements will change independently. Avoid adding empty layers without a purpose. Check their real names and keep frame/layer/path explicit in every call. The last layer cannot be deleted.

For a manual circle or diagonal, use symmetric pixel runs and avoid accidental isolated pixels. Check the result at native size as well as an integer zoom. For small icons, strong value contrast and a recognizable outline usually matter more than extra colors.

Read the [heart, sword and layered-character recipes](examples.md#complete-creation-recipes) for concrete starting points. Palette data remains centralized in [presets](../../config/palettes.json); do not duplicate preset arrays here.
