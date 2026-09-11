# Animation reference

See the [exact contract](../../docs/MCP_TOOLS.md) and [call examples](examples.md).

All edit frame numbers start at 1. Duplicate insertion uses 0 only to mean append. Frame durations are milliseconds, 1–65535. Tags use inclusive ranges and `forward`, `reverse`, `pingpong` directions.

`get_sprite_info` exposes no durations, tags or cel-link identities. The MCP tools cannot create an arbitrary empty cel or delete an individual cel. Build a linked layer by creating frames before the layer, then draw one source cel. `link_cel` rejects an occupied target. It creates native Aseprite shared cel data, preserves positions, and supports backward links at the pinned develop revision.

Verify a link by editing source pixels and reading the same coordinates in the target. The integration test additionally checks serialized Aseprite linked-cel chunks. Drawing identical pictures alone does not prove native linking.

Use `save_as` to keep the editable animation. See [exporter](../pixel-art-exporter/SKILL.md) for GIF/sheet exports, copy-based FPS changes and known frame-range export. There is no dedicated preview/playback, reorder-frame or list-tags tool.
