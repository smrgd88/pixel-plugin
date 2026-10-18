# Export selection, trimming and output-set protection

MCP pin `99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8` includes PR #35.
[Exact schemas](MCP_TOOLS.md) · [server contract at this pin](https://github.com/smrgd88/pixel-mcp/blob/99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8/docs/EXPORT_OPTIONS.md).

| Option | export_sprite PNG/JPG/BMP | export_sprite GIF | export_spritesheet |
|---|---|---|---|
| tag or frame_start/frame_end | Supported | Rejected; use existing frame_number only | Supported |
| layer_id, include_hidden | Supported | Rejected | Supported |
| expected_revision | Supported | Supported | Supported |
| trim | Per-frame transparent bounds | true rejected | Native cel trim, with background exception below |
| extrude | Not an input | Not an input | Boolean, native one-pixel edge extrusion |
| border/shape/inner_padding | Not inputs | Not inputs | Integers 0..100 |
| overwrite | All actual outputs | Single GIF | Texture AND JSON |

Still supply original required fields, including export_sprite.frame_number and sheet layout/padding/
include_json. Use frame_number=0 when adding tag/range selection. tag, explicit frame range and positive
frame_number are mutually exclusive. frame_start/end omission/null means first/last; explicit 0 is invalid.
tag is an exact nonempty unique stored native name. Reject missing/duplicate names, not wildcard-match them.
If the user identifies one duplicate tag by its current tag_id, resolve that query's range and use frame_start/frame_end plus its revision; export has no tag_id argument. Do not rename source tags merely to make export succeed.
A reverse/pingpong tag selects its inclusive source frames **once in ascending source order**. It does not
expand playback direction/repeats. Query tags to disambiguate before selecting a name; export does not use tag_id.

For layer selection, query get_sprite_structure and send both layer_id and expected_revision. Group selection
includes its subtree while preserving parent composition. Saved target/ancestor visibility applies unless
include_hidden=true, which requires layer_id and reveals only the selected subtree/ancestors temporarily.
Locked layers can be exported. expected_revision is optional for other selections and guards saved source bytes.
Requery after an edit. All export preparation is in memory; source bytes/metadata, native mode and links remain.

## Images, sheets and JSON

Multi-file range 3..4 returns actual stem_0003.png/stem_0004.png and source frame_number 3/4, not 1/2.
One selected frame uses the requested single path and omits files. Report every returned actual output path.
Single-frame trim has no offset response; use sheet JSON for reconstruction. New selection/trim with all
transparent results rejects; partially empty selections keep an empty frame as 1x1 when trimmed, preserving timing.
Legacy empty-canvas export without new selection/trim remains supported.

Sheet padding is the fallback for border_padding/shape_padding/inner_padding. Omission/null uses fallback;
explicit 0 overrides it. Do not replace `0` with the fallback using truthiness. Border is the outer margin,
shape separates frames, inner is transparent inset. JSON frame bounds include inner but exclude extrusion.
With inner>0 the extruded edge can be transparent. Fixed grid column/row counts are not exposed.

A visible selected **native background** makes sheet trim retain the canvas. Exclude that background for
foreground-only trimming. For a single-palette indexed visible background, the in-memory texture may become
RGB/RGBA to preserve opaque mask-index pixels. Source indexed bytes/palette/links are unchanged. Multi-palette
native rendering keeps per-frame palette colors. Do not promise indexed PNG identity or a new keep-indexed option.

Sheet textures accept .png/.jpg/.jpeg/.gif/.bmp, with encoder-specific alpha/color limitations; PNG is the lossless
pixel-verification path. There is no standalone JSON, engine-specific metadata format or new GIF animation contract.
The JSON sidecar is **always generated/protected**, even with include_json=false. That flag controls whether
metadata_path is returned, not whether the file exists. Account for the sidecar on overwrite checks.

Read actual JSON: frames may be an object, object serialization order is not a contract. Each frame adds
source_frame_number (one-based). Use native frame, spriteSourceSize, sourceSize, duration, trimmed and rotated.
meta.image is the final texture basename. meta.frameTags intersects the selection and uses zero-based OUTPUT
indices; preserve native direction/color, but do not replay direction as additional exported frames. Newline/control
characters are JSON-escaped without changing their values. Do not infer offsets or frame names from output numbering.

## Overwrite, failure and recovery

overwrite omission/null defaults true. false rejects the whole planned output set if any member exists, including
a sheet's unreturned JSON. No partial publication is success. A sequence's requested base and unrelated old numbered
files outside files[] are preserved, not implicitly deleted. Source/output aliases, hard links and invalid destinations reject.
Texture and JSON use the existing output-files protection and rollback for ordinary errors/cancellation. On
file_rollback_failed, preserve all error.recovery entries: sheet output_index 1 is texture and 2 is JSON. Follow
[error handling](MCP_ERRORS.md). Source history/undo does not undo exports. Never retry blindly or delete backups.

This is not set-wide crash atomicity. External readers can observe an intermediate set; non-cooperating writers,
ABA/final-check races, crash recovery and orphan staging cleanup remain limitations. Canvas/extent limits are
conservative (32767 per axis, 64 Mi pixels); rows/columns/packed can reject a set that tighter packing might fit.
Split a request rather than increasing timeout or bypassing guards. Exact indexed PNG preservation, more precise
size budgeting, crash recovery and slice/pivot/nine-slice are server follow-ups, not plugin features.

No direct scale/FPS/loop override is added. Scale/retime a separate native copy when requested, query IDs/revision
again on that copy, then select/export. For filtered GIF, explain the unsupported options; only prepare a separate
copy within the user's authorized transformation, rather than silently substituting PNG semantics.
