# MCP errors and request tracing

Bundled source `65074051f5d3903124ead37367c7fc62d9e7e7f6` includes merged MCP #25.
The authoritative contract is [ERRORS.md at this exact pin](https://github.com/smrgd88/pixel-mcp/blob/65074051f5d3903124ead37367c7fc62d9e7e7f6/docs/ERRORS.md).
Its introductory “implementation branch” status is historical; PR #25 is merged upstream.
All 56 tools, successful payloads, warnings and input/output schemas remain unchanged.

## Read the envelope first

Every processed tools/call gets a server-generated UUID in
`_meta["io.github.smrgd88.pixel-mcp/request_id"]`, independently of enable_timing.
Client-supplied IDs are ignored. This is separate from the JSON-RPC id, snapshot_id and
operation_id; it correlates one request and is **not an idempotency key**.
Successful structuredContent/text stays tool-specific; do not require a new success/details wrapper.

Tool failures retain `isError:true`, have no structuredContent and contain JSON text:

```json
{"request_id":"UUID","error":{"code":"history_conflict","message":"The file has changed since the recorded operation."}}
```

The same error object is in `_meta["io.github.smrgd88.pixel-mcp/error"]`.
Check failure before decoding a successful payload. Branch on error.code, not message substrings.
Report the returned code, message and request ID when available. Preserve unknown codes and extra
error fields; do not infer success or retryability from an unfamiliar code.

SDK missing/type/schema arguments and unknown tools remain JSON-RPC errors with code -32602;
`error.data` contains request_id and the diagnostic error object (invalid_arguments for -32602).
Other protocol failures retain their wire code. Transport JSON/envelope decoding failures and
non-tools/call methods are outside this tracing boundary. Cancellation/disconnection can prevent
an entire response from arriving; do not invent a request ID or assume the edit did not happen.

## Codes and decisions

| Codes | Handling |
|---|---|
| invalid_arguments | Correct the supplied arguments within the user's task; distinguish SDK and tool failure envelopes |
| not_found, permission_denied | Inspect the intended resource/access; do not guess a replacement source |
| lua_error | Lua syntax/runtime rejection, including some invalid layers/frames; not necessarily invalid_arguments |
| aseprite_execution_failed, unsupported_aseprite, capability_probe_failed | Report process/runtime failure; inspect setup and health as appropriate |
| timeout, cancelled | Inspect affected state before deciding on another edit; a missing response is not proof of rollback |
| file_rollback_failed | Stop automatic retries and preserve recovery references; see below |
| file_changed, file_commit_failed, file_lock_scope | Inspect file state and intended operation before retrying |
| snapshot_invalid, snapshot_capacity, snapshot_expired, snapshot_source_mismatch | Follow [saved-file recovery rules](MCP_SAFETY.md); never delete unrelated backups to make room |
| history_invalid, history_scope, history_conflict, history_operation_mismatch, history_recovery_required | Inspect current history/file; do not bypass guarded undo with an automatic restore |
| operation_failed, protocol_error, unknown future code | Report the actual diagnostic without guessing a finer classification |

Lazy snapshot cleanup may return not_found instead of snapshot_expired. Codes come from typed
errors, not text matching. Rollback failure takes precedence over timeout/cancel and commit errors.

## Preserve partial rollback recovery information

For file_rollback_failed, some outputs may already have changed. The text diagnostic and namespaced
error metadata both retain error.recovery, for example:

```json
{"output_index":1,"directory":".pixel-mcp-stage-opaque","backup_file":".original-backup","rollback_failed":true}
```

Each entry refers to the **canonical output parent at operation start**. directory is a relative
recovery folder name, not a complete path. output_index is 1-based (sequence export frame output
order). backup_file is optional; absence does not prove that no backup exists. Some retained entries
can have rollback_failed:false. Report all supplied entries exactly, including these distinctions.
If a symlink alias changed, inspect the original canonical location rather than the current alias.
Do not retry the export/edit automatically, overwrite/delete retained backups, or promise all outputs
were restored. Manual recovery requires inspecting actual files within the user's recovery scope;
there is no new automatic recovery tool. Existing snapshot/history authorization still applies.

## Client and logs

`bin/mcp-client.py` keeps call() success results compatible. Use request('tools/call', …) to inspect
successful result metadata. ToolError (a RuntimeError) retains result, diagnostic, request_id, code
and recovery. ProtocolError retains the full JSON-RPC error plus code and data. Neither path retries.
Legacy non-JSON tool errors remain accessible through result and the exception message.

Non-debug bundled CLI logs redact raw paths, arguments, Lua and process output. Completion/timing
logs use the same request ID and respect configured log levels. Explicit debug logging can include
sensitive detail; review it before sharing. Startup config errors and externally supplied Go loggers
are outside this guarantee. MCP stdout remains separate from diagnostic stderr.

Run `python3 bin/test-mcp-errors.py` for client regressions; add
`--aseprite /absolute/path/to/aseprite` for real request IDs, failures, warnings and log checks.
Rollback filesystem failure injection and SDK serialization are verified separately using the pinned
upstream tests; the client fixture does not claim to trigger a real Aseprite rollback failure.
