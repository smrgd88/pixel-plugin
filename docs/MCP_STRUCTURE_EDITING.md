# Structure, revisions, layers, cels and tags

This checkout bundles MCP `99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8` (64 tools).
Use [exact schemas](MCP_TOOLS.md). Authoritative server contracts at this pin:
[structure](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/SPRITE_STRUCTURE.md),
[cel properties](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/CEL_PROPERTIES.md),
[unlink](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/CEL_UNLINK.md),
[layer/group](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/LAYER_PROPERTIES.md),
[tags](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/TAG_EDITING.md).

## Query, identify, edit, query again

1. Query get_sprite_structure for layers/cels or get_sprite_tags for tags.
2. Select the exact returned structural ID and frame/tag. Read visibility, locks, native sharing and scope.
3. Pass the actual returned revision as expected_revision to the requested mutation.
4. Requery after every edit, including legacy edits such as drawing or adding frames. Re-resolve all
   affected IDs after insertion/move/reordering or tag range changes. Never automatically retry stale edits.

revision is the SHA-256 of saved file bytes, not a sequence, permanent identity, authentication token or
server snapshot. Byte-exact restoration produces the same revision. Pages are not a frozen snapshot:
compare revisions across layer/frame pages and restart the query if they differ. Non-cooperating writers,
ABA and the final check/rename race remain server limits. Finish GUI saves before querying/editing.

get_sprite_structure uses bottom-to-top sibling indices joined by `/`, e.g. `2/1`, with root parent_id="".
Its depth-first layers include hidden/locked/internal clipboard layers. Names/name_path are not unique IDs.
layer_id filters one layer, not its descendants. layer_offset is zero-based; page_size defaults 50, max 100.
Frame windows are one-based inclusive, at most 100 frames; use next_layer_offset/next_frame_start.
An offset equal to matching_layer_count is an empty page; absent cels have exists=false, not a fake image.
Read local visible/editable and ancestor-combined effective_visible/effective_editable separately.
image_ref and linked_cel_count describe native sharing over the entire document, including outside pages.
Equal pixels do not prove shared images. Tilemap dimensions are not raster-pixel dimensions.

## Layer/group operations

| Tool | Required selection | Important policy |
|---|---|---|
| set_layer_properties | layer_id + expected_revision | name/visible/editable/opacity/blend_mode, at least one actual change |
| move_layer | layer_id + parent_id + stack_index + expected_revision | final bottom-to-top sibling index; both IDs refer to the same pre-edit revision |
| create_layer_group | name + parent_id + stack_index + expected_revision | empty group only; move existing children explicitly |

Use raster/groups only; tilemap/reference/background/internal clipboard targets are rejected.
Hidden targets/ancestors are allowed. Locked ancestors reject edits. A locally locked layer permits only
editable=true by itself; query again before another edit. Moving requires the subtree and destination/
ancestors to be unlocked; self/descendant/raster-parent and insertion below native background reject.
Group opacity/blend are unsupported: do not flatten or convert to bypass this restriction.
Omitted/null properties stay unchanged; false, opacity=0 and empty layer/group names are real values.
NUL/reserved clipboard names reject. No-op edits reject. Blend names are the 19 native names in the schema
reference; arbitrary numeric modes/aliases are unsupported. Layer moves preserve native image sharing.

## Linked cel properties versus unlink

set_cel_properties requires native saved sprite, layer_id, frame_number, expected_revision, and at least
one real change to x/y/opacity. Omitted/null retains a value; 0 means zero. x/y are sprite coordinates in
-32768..32767, opacity 0..255. No clipping or automatic layer/frame/cel creation occurs.
Hidden raster cels are allowed; locked target/ancestors and group/tilemap/reference/background reject.

By default shared cels reject. Position/opacity setters affect the **whole native shared set**, not just
the selected cel. Inspect the full sharing scope and obtain authorization for that shared-set change
before sending allow_linked=true. Existing explicit authorization suffices; a success warning is not a
new consent request. Report all affected_cels and linked_cel_properties warnings, including off-page peers.
Do not use allow_linked merely to make a single-cel request succeed.

For a single-cel change, use unlink_cel with fresh structure/revision, then query and edit the independent
cel. This native unlink preserves pixels, position/opacity/z-index and metadata; it does not move the cel.
Already-independent cels reject. remaining_linked_cels lists the old peers; with one peer left, both cels
are now independent. Verify post-save/reopen sharing, not only matching pixels or old native chunk flags.
Native saved links are within the same layer across frames; do not promise cross-layer sharing.

RM-FIX-01 now lets draw_pixels find a unique exact raster name at any group depth. Duplicate names reject;
it still accepts layer_name, not layer_id. Other legacy drawing tools and link_cel do not gain ID addressing or the
same recursive lookup by implication. Construct new links on a root layer before moving the layer into a group when the legacy link tool cannot address that nested target. Use the specific tool contract.

## Tag operations

get_sprite_tags returns revision, frame_count and tags (empty array is valid). tag_id is the current
one-based native array order, sorted by range, not creation/name order or a persistent UUID. Names may
already be empty/duplicated. Query and use IDs rather than guessing a name; range edits can reorder IDs.
set_tag_properties requires tag_id+expected_revision and an actual change. Omission/null retains values.
New names must be nonempty/non-whitespace, valid UTF-8 without NUL, at most 65535 UTF-8 bytes, and unique
when changed. Existing empty/duplicate names can be retained by omission while editing other properties.
Directions: forward/reverse/pingpong/pingpong_reverse. repeats=0 is a real native unspecified value,
not omission; 0..65535 is supported. Endpoints are inclusive source frames, 1..65535 and within the file.
Overlapping ranges are allowed. Requery before another edit/export. Color/data/properties are preserved.
Legacy create_tag still accepts its original three directions and delete_tag remains name-based.

All mutations use existing error/request-ID and optional history rules. Stale revision gives file_changed;
invalid types/required inputs can be JSON-RPC errors, Go validation invalid_arguments, native semantic
rejections lua_error. Preserve [diagnostics](MCP_ERRORS.md); do not guess a reason from a fixed public message.
