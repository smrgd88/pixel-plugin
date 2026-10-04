# Preview, snapshots and recorded undo

Bundled MCP 6507405 includes merged #21/#23/#24. Read the exact [tool schemas](MCP_TOOLS.md)
and [configuration](../config/README.md). These operations concern saved files, not unsaved GUI state.

## Dry-run: execute on a temporary copy

Only quantize_palette, apply_auto_shading and flatten_layers accept optional boolean `dry_run`.
Omitted/false edits normally. True executes the same operation on a private temporary copy,
returns the usual results plus `dry_run:true` and `preview.before/after/would_change_file`, then
removes the copy. No permanent preview image/path, snapshot ID or apply token is returned.
`would_change_file` compares serialized bytes, not visual loss or pixel similarity.

Report a dry-run as a completed preview with the original unchanged. Its warnings describe
potential effects if applied, not completed changes to the original. Follow [warning handling](MCP_WARNINGS.md)
for all messages including unknown codes. Do not automatically apply because a preview succeeded.
For a preview-only request stop after reporting. If the user already requested application,
continue within that authorization using the same operation with dry_run omitted/false; do not
add a redundant approval step. This is a new operation on the then-current source, not committing
an old preview. Read-only preview success does not guarantee write permission for actual apply.

## Manual saved-file recovery

Use create_snapshot before an authorized risky edit when recovery is wanted, retain the actual
snapshot_id, and list_snapshots with sprite_path to find existing copies. A snapshot stores exact
saved-file bytes, including layers/frames/metadata. It persists across server restarts, but has a
7-day TTL. Snapshots share a store-wide limit of100 entries /512MiB; unexpired entries are not evicted.
List/create/restore can lazily remove expired entries. This is not a permanent backup service.

restore_snapshot takes sprite_path and the actual returned snapshot_id. It only replaces the
existing original canonical path; it cannot restore to another path or recreate a deleted source.
It first makes backup_snapshot of the current file, consuming the same storage quota, then verifies
and replaces the file. Report success and the backup ID only after success. If capacity, permission,
source mismatch or integrity checks fail, report the error; do not claim restoration or blindly retry.
A response interruption may leave a backup: inspect current state/list before deciding a next action.
Current permission bits survive, not historical owner/mtime/ACL or unsaved editor buffers.

Use delete_snapshot only for the user's intended cleanup. It permanently removes that recovery
copy and its linked history; do not silently delete unrelated snapshots to make room.

## Recorded edit history and undo

Automatic recording requires config `enable_history:true`; default false stays unchanged.
Do not turn it on silently. It adds storage/time cost and can reject edits when backup quota is full.
The two history tools remain available when recording is false, including for earlier stored records.

For a requested undo, call list_operation_history(sprite_path), read recording_enabled, and select
the newest entry with state=applied (list order is descending sequence). Pass that exact operation_id
as expected_operation_id to undo_last_operation with the same sprite_path. Never guess IDs or undo
merely because a warning was returned. An empty list is valid: report that no recorded edit is available.

On success verify operation.state=undone and report backup_snapshot. For another requested undo,
read the list again. Reusing an ID must not undo a different older edit. Stale IDs, external edits,
missing/expired snapshots or history_recovery_required are errors: inspect and report; do not bypass
by automatically restoring a snapshot or deleting history. Manual restore needs the user's intended
recovery scope; existing authorization still applies without repeated confirmation.

Only successful byte-changing edits to existing sprites are recorded (including saved selection/
clipboard edits). Dry-run, failed/no-op calls, reads, exports, save_as, downsample outputs, new canvas
creation and manual snapshot operations are excluded. History expires/deletes with its snapshot;
no redo, arbitrary older-operation rollback, unlimited history or native GUI undo is promised.
Stores shared by servers require compatible versions; history-enabled edits on one store serialize.

## Storage

Optional absolute snapshot_dir selects a durable private store, separate from temp_dir. Default is
os.UserConfigDir()/pixel-mcp/snapshots (on macOS, ~/Library/Application Support/pixel-mcp/snapshots),
not necessarily the config file directory. Unix directories/files are private; incompatible public
permissions can be rejected instead of silently changed. Metadata includes canonical source paths.
Checksums validate integrity, not authenticity against same-user tampering. Cleanup/expiry and a
pre-restore backup do not imply a multi-file transaction or crash-proof filesystem durability.

## Failed edits and request tracing

Follow [the error contract](MCP_ERRORS.md) for tool and JSON-RPC failures. Preserve request IDs and
all error.recovery entries. file_rollback_failed outranks cancellation/timeout: some outputs can
remain changed. Stop automatic retries, keep recovery folders/backups and inspect the original
canonical output location. Do not equate file staging rollback with snapshot restore or history undo.
