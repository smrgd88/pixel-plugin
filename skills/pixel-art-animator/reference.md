# Animation reference

See the [exact contract](../../docs/MCP_TOOLS.md) and [call examples](examples.md).

All edit frame numbers start at 1. Duplicate insertion uses 0 only to mean append. Frame durations are milliseconds, 1–65535. Tags use inclusive ranges and `forward`, `reverse`, `pingpong` directions.

`get_sprite_info` exposes no durations, tags or cel-link identities. The MCP tools cannot create an arbitrary empty cel or delete an individual cel. Build a linked layer by creating frames before the layer, then draw one source cel. `link_cel` rejects an occupied target. It creates native Aseprite shared cel data, preserves positions, and supports backward links at the pinned develop revision.

Verify a link by editing source pixels and reading the same coordinates in the target. The integration test additionally checks serialized Aseprite linked-cel chunks. Drawing identical pictures alone does not prove native linking.

Use `save_as` to keep the editable animation. See [exporter](../pixel-art-exporter/SKILL.md) for GIF/sheet exports, copy-based FPS changes and known frame-range export. There is no dedicated preview/playback, reorder-frame or list-tags tool.

## Pose and timing decisions

Frame counts below are starting points, not limits or frame-rate guarantees:

| Motion | Useful poses | Timing idea |
|---|---|---|
| Idle | Normal stance, slightly raised/lowered chest; optional blink | 2–4 poses, about 300–500 ms each for slow breathing |
| Walk | Contact, down, passing, up, mirrored for the other foot | 4–8 poses; around 100 ms each for a simple cycle |
| Run | Exaggerated contact and airborne poses, longer stride | 6–8 poses; around 60–80 ms each |
| Attack | Anticipation, strike, follow-through/recovery | 150 ms windup, 30 ms strike, 100 ms recovery as one example |
| Jump | Crouch, launch, ascent, peak, descent, landing | Short launch, optional hold at peak, then settling |

Anticipation tells the viewer what is about to move. Follow-through lets hair, cloth or a weapon settle after the body stops. Move swinging limbs along an arc; a one- or two-pixel squash/stretch can make an impact readable at low resolution. Apply these selectively to the requested style.

For acceleration, vary pose spacing as well as duration; merely adding frames does not automatically make a motion smoother. Use longer holds for anticipation/landing and short durations for fast action. Integer millisecond rounding means e.g. 33 ms is approximately, not exactly, 30 FPS.

When duplicating a pose and shifting it, clear the old pixels before drawing the new position. Otherwise the duplicate retains a trail. Keep static elements on their own layer; native linked cels are for shared content, not distinct poses.

Keep tags named for actions (`idle`, `walk`, `attack`) and maintain known inclusive ranges as frames are inserted/deleted. Inspect exported timings rather than assuming a tag changes the frame rate. See [complete motion recipes](examples.md#complete-animation-recipes).
