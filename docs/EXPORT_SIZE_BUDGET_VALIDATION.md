# Export size-budget synchronization validation

Task: `[SHARED][CHORE] Plugin export 크기 예산 개선 동기화` (2026-10-18).
Base/initial HEAD/merge-base: plugin `develop@e856582ee6ef50cf32d5ae12143cf3f858891428`
(documentation PR #17, commit `2f3abdc`). Branch: `chore/shared-export-size-budget-sync`.
This is an Unreleased develop PR candidate. No develop/main merge, release, marketplace
publication or personal installation replacement is part of this work.

## Source and contract

The [source pin](../config/mcp-source.json) advances from
`99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8` to
`fcb83861df08b4ee897f162d9a175bd9d149ed96`.
[MCP PR #37](https://github.com/smrgd88/pixel-mcp/pull/37) is merged; GitHub reports its
final test job SUCCESS (publish-ci-image SKIPPED). Its exact committed
[export contract](https://github.com/smrgd88/pixel-mcp/blob/fcb83861df08b4ee897f162d9a175bd9d149ed96/docs/EXPORT_OPTIONS.md)
and changed handlers/tests were read from a Git archive, without modifying the MCP checkout.
The source document's earlier candidate/unmerged prose is historical; the PR merge commit
identifies the runtime source.

All 64 complete live tool definitions (descriptions, input and output schemas) are identical
to the prior snapshot. The snapshot/reference source identity changes. This does not imply
unchanged behavior: measurement, allocation, scratch lifetime, plan recheck and texture/JSON
validation change. Five binaries were rebuilt with Go 1.25.0 darwin/arm64, CGO=0,
trimpath and source-commit version flags; [provenance and hashes](../bin/mcp-build.json)
identify each artifact. The allocator's retained LAF notice is in
[third-party notices](../THIRD_PARTY_NOTICES.md); the original MIT notice is unchanged.

## Changed behavior and preserved contracts

- Actual trim/layout/padding/extrusion and packed duplicate measurement replace the
  former strip-envelope overestimate on modern runtimes. Rows/columns remain strips.
- Aseprite 1.3.18.2+ uses stable packed ordering; older supported runtimes retain the
  conservative trimmed/deduplicated packed envelope and can reject otherwise valid sets.
- Canvas/final sheet limits remain 32767 per axis and 64 Mi pixels. Unique packed samples,
  geometry work (8,000,000) and allocation planning (30 seconds) are bounded. Scratch
  buffers are reused/released; these are working-memory controls, not a total RSS cap.
- Revision guards, omitted/null versus explicit zero, background rendering, indexed
  source/palettes/links, frame order/duration, JSON and ordinary-error rollback remain.
- The crash-recovery SPIKE has no production recovery tool or automatic retry. External
  writer races, crash set atomicity, older-runtime exact packing and total RSS control
  remain outside the implementation.

Exporter skill, format guide, examples and Claude export command now explain those limits
and actual output checks. The prior grid→rows wording was corrected: public rows/columns
have no fixed grid dimensions. No new tool or public export option is invented. Manifest
versions, publisher, wrapper and configuration precedence remain unchanged.

## Execution evidence

Local evidence is retained under `test-outputs/export-size-budget/` in the task worktree.
It includes the committed source export, prior native bundle, build log, isolated configs,
raw MCP calls (including request IDs), native fixtures, PNG/JSON, and each attempt's logs.
Test configs set timeout=30, isolated temp/snapshot stores and history=false; upstream
history tests enable history only in their own temporary configs. No user config is written.

Final commands/results are recorded below. Cross-builds are not native
execution. Historical [Top4](TOP4_SYNC_VALIDATION.md) and
[Codex installation](CODEX_INSTALL_VALIDATION.md) reports are preserved byte-for-byte,
including their pins, review and timeout/failure records.

### Failed attempts retained

1. `native-budget.log`: test expected prior wide-canvas vertical trim to reject. Actual
   prior vertical export succeeded. Corrected the before/after oracle to verify that legacy
   success, with the other four layouts still demonstrating prior rejection.
2. `native-budget-rerun.log`: test expected padding+extrusion to leave just one opaque pixel
   inside inner padding. Actual native PNG contains a 3x3 extrusion around the one-pixel
   content inside the padded allocation. Corrected the independent pixel expectation and
   clarified the consumer guidance; dimensions/JSON expectations already matched.
3. `native-budget-final.log`: work-limit rejection and file preservation passed, but the test
   incorrectly searched the public sanitized error for internal `planning budget` text.
   Retained the public `invalid_arguments`/request-ID checks; the pinned Go allocator test
   separately isolates the exact geometry-work limit. No timeout/limit was raised.

These were test-oracle assumptions, not hidden successful runs or production repairs.
4. `macos-source-focused.log`: Go could not start because the configured temporary directory
   had not yet been created at its intended absolute path. Created the isolated directory and
   reran the unchanged command (`macos-source-focused-rerun.log`); this was an environment
   setup failure, not a test failure or a timeout.
5. Docker preflight found no Python pip/Pillow. The disposable image's Python 3.10 then
   could not install pinned Pillow 13 (`docker-dependencies.log`). Installed an isolated
   Python 3.12 environment inside that container (`docker-python312.log`), keeping the exact
   repository dependencies. No host/user installation or requirement pin was changed.

### Verified macOS execution

- Host: macOS arm64, Aseprite 1.3.18.2-arm64. Full Access native drawing/export succeeded;
  no `_RegisterApplication` abort occurred in this task.
- `bin/test-mcp-top4.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite`:
  92 requests / 10 grouped checks PASS (`top4/run-cdd5ce99`, `top4.log`). Covers real
  drawing, revision/IDs/explicit zero, source/native metadata/palette/links, exact pixels,
  source frame order/duration/tag metadata, hidden selection, background RGB/grayscale/indexed,
  indexed-background RGBA output, include_json=false sidecar and overwrite protection.
  The expected warning is `linked_cel_properties`: position/opacity changes affect every
  cel sharing the native image; affected_cels contains the complete result. Expected tool
  errors: 9 lua_error, 3 file_changed, 9 invalid_arguments; the missing-input case uses
  JSON-RPC -32602. Raw calls retain all request IDs. Two pre-existing Pillow getdata
  deprecation warnings remain; they are not test failures.
- Pinned source focused unit/PBT: four `TestExportBudget{Bounds,PackingProperties,
  PlanningWorkLimit,RuntimePackingPolicy}` tests PASS, including 500 deterministic
  occupancy-grid cases, overflow/endpoint/area/padding and cancellation boundaries.
- Pinned source focused native integration (non-race):
  `go test -mod=readonly -p 1 -count=1 -tags=integration ./pkg/aseprite ./pkg/tools -run
  'TestExportBudget|TestExportOptionsBackground|TestOutputFiles|TestOutputRollback|TestOutputSuccessfulRollback' -v`
  PASS (aseprite 0.926s, tools 70.895s; no FAIL/SKIP). Includes independent native
  3-mode × 5-layout × trim on/off oracle, wide trim PNG/JPG/GIF/BMP, 24 equal-area shapes,
  pre-allocation changed-plan rejection, 12 scratch-retention cases and ordinary-error
  publication/rollback/cancellation/recovery. `GOMAXPROCS=2`, Go 1.25.0, isolated canonical TMPDIR.

### Final bundle and older-runtime results

- Final `bin/test-mcp-export-budget.py --aseprite <native-aseprite> --previous-binary
  <preserved-99f193a-darwin-arm64>`: PASS, 26 export calls / 6 groups,
  `native-reviewed/run-b1e66403`, `native-reviewed.log`. Seven previous rejections now
  succeed, one prior vertical success remains, 12 current successful sheets and six current
  intentional rejections are checked. Full PNG bytes plus per-frame pixels, known bounds,
  strip order, JSON duration/source/trim metadata and source/output byte/stat preservation
  are verified. Before the review repair, `native-budget-pass.log` also passed; only the
  final reviewed run certifies the strengthened oracle.
- Linux amd64 bundled launcher/MCP → Aseprite 1.3.18.3-dev: same final export-budget test
  PASS, 18 calls / 6 groups, `linux-bundle/run-dfc28e02`, `linux-bundle.log`. No previous
  binary comparison is claimed for this run. Docker server 28.3.2 on the ARM host uses
  amd64 emulation, not physical Linux x86_64. Image `pixel-mcp-ci:latest` ID
  `sha256:b0b99e1a1e3420411f8efe341da1fbc0f9b5df5fc6852df2e5f1d31f37ce3b1a`;
  isolated Python 3.12.15 with jsonschema 4.25.1 / Pillow 13.0.0. Repository mount is
  read-only; test outputs use a separate evidence mount.
- Older-runtime pinned-source tests: Aseprite 1.3.17.2 / Go 1.25.14 / Linux amd64 emulation,
  image `pixel-mcp-ci:aseprite-1.3.17.2-verified` ID
  `sha256:50683dba47b4611e556e21db1e7fe00ab2a821e6d6882022d6370148527b6b73`.
  `go test -mod=readonly -p 1 -count=1 -tags=integration ./pkg/tools -run
  'TestExportBudget(FormerStripRejection|NativeEqualAreaOrder|ScratchRetention|TrimAndFormats)$' -v`
  PASS in 29.089s (`linux-min-source.log`; no FAIL/SKIP). Confirms rows/columns acceptance,
  the intentional 65-frame conservative packed rejection, 24 equal-area frames, all five
  trimmed layouts × four formats, and 12 scratch-retention cases. This is source-level
  integration, distinct from the modern Linux bundled-MCP execution above.
- Final default plugin suite: **7/7 PASS** (`package-final.log`). Full live schemas match;
  64 tools / 91 documented examples / 11 schema-validated recipes / 19 rejected contract
  regressions / five binary hashes. Wrapper selection, spaces/argv, error exit, recursion
  guard and configuration precedence pass. Recipe validation here is static, not a new
  complete recipe/model/installation execution.
- Native health: Aseprite 1.3.18.2-arm64 / API 41, required minimum 1.3.17.2 / API 39.
  Python syntax, Git whitespace and document link/reference checks pass. All five bundles
  retain executable modes. Original LICENSE, manifests/marketplaces, launcher, Codex
  configuration and both historical validation reports are byte-identical to the base.
- No timed-out test occurred in this task. Earlier reports' timeout failures remain intact.

## Scoped self-review

Used `convergent-code-review` in review-and-repair mode with the backend lens. Baseline,
initial HEAD and merge-base are `e856582ee6ef50cf32d5ae12143cf3f858891428`; the reviewed
scope is the 25-file working-tree candidate (five binaries, provenance/pin/schema/reference,
new regression, third-party notice, exporter/command guidance and current-status/report docs).

| ID | Priority / final status | Evidence, bounded repair and verification |
|---|---|---|
| SHARED-P2-001 | P2 / VERIFIED | The new aggregate image oracle could accept two distinct frames incorrectly sharing one rectangle because expected pixels were painted using returned bounds. `review-oracle-repro.log` demonstrates that false pass. Added independent known frame sizes/strip positions and per-frame pixel comparisons before the aggregate image check; retained legitimate identical-sample sharing. Final macOS 26-call and Linux 18-call runs pass. |

Repair-diff review checked callback/layout binding, legitimate duplicate bounds, padding
and extrusion, rejection source/output snapshots and the before/after label when comparison
is not requested. Closure rechecked the reproduction and final real runs. Fresh-discovery
review independently traversed pin → build/provenance → wrapper/live contract → export
consumer instructions and tests, then current versus historical status and publication limits.
No new blocker or secondary regression was found.

Metrics: initial discovery 1; repair cycle 1; repair-diff review 1; closure 1; fresh-discovery
full-scope review 1; total review passes 4. Initial findings P0=0/P1=0/P2=1/P3=0; new findings
after repair/closure/fresh=0; repair-caused/reopened=0; VERIFIED=1; unresolved/accepted/
out-of-scope findings=0. Open P0/P1 remained 0 throughout. Stop reason: the scoped verification
gap is closed and no merge blocker remains. Pre-review fixture corrections listed above
are implementation/test-development attempts, not additional review repair cycles.

Final-candidate manifest (before this reporting-only addition) SHA-256:
`78e45ac1650becfb31119d1b5b4f513f9c1cfecb9908e343c17d5759599610f2`.
The manifest records every reviewed file hash in local evidence. No relevant runtime,
contract, test or guidance mutation occurred after that candidate selection; final-candidate
invalidations=0. Subsequent changes only record results/review. Duration was not measured.

Reviewed: all 25 changed files and live schema/provenance. Inspected for context: pinned
MCP measurement/allocation/export handlers and their native tests, output-file/diagnostics
contracts, existing Top4 client and package validation, wrapper, manifests and historical
reports. Changed during repair: the new export-budget test and reporting-only evidence.
Excluded: MCP production changes, unrelated features, installation/lifecycle changes,
other worktrees, personal settings, merging/releasing/publishing.

Notes:

1. macOS amd64, Linux arm64 and Windows amd64 have cross-build/checksum evidence only.
   Physical Linux x86_64 execution is not claimed. Platform release validation remains M3.
2. Full MCP suite/race, full plugin behavior/recipe matrix and every format/blend/mode
   combination were not repeated; the changed export path, preserved Top4 contracts,
   native oracle/scratch/rollback and default package checks were exercised. GUI, model
   workflow and personal install/lifecycle tests were not rerun because packaging did not change.
3. Older-runtime exact packed planning, total process RSS bounds, crash recovery and
   non-cooperating writer protection remain unimplemented; native algorithm changes require
   revalidation. None is represented as a new completed feature.
4. Historical Top4 getdata deprecation warnings remain outside this synchronization; the
   pinned Pillow 13 still executes them successfully. Update those tests before moving to Pillow 14.

Verdict: **PASS_WITH_NOTES**. Ready for review as a develop PR; no merge or release is performed.
Keep the branch/worktree and ignored evidence until an authorized merge and cleanup check.

## Requested follow-up self-review and repair

This follow-up starts at `a36567ff26736f0bc05ad149979c367643644392` with a clean
`chore/shared-export-size-budget-sync` worktree. Base/merge-base remains
`develop@e856582ee6ef50cf32d5ae12143cf3f858891428`. The initial 25-file PR scope and
its direct build/client/export consumers were reviewed again in review-and-repair mode
using `convergent-code-review` and its backend lens. Earlier results above remain historical
execution evidence; they are not replaced by this narrower repair.

| ID | Priority / final status | Trigger, impact, correction and evidence |
|---|---|---|
| SHARED-P2-002 | P2 / VERIFIED | `bin/test-mcp-export-budget.py` interpolated `json.dumps(path)` as Lua source in `fixture`. A Korean output directory produces JSON `\uXXXX` escapes that Lua rejects before any export call. Reproduced with real Aseprite (`unicode-red.log`, zero export calls). Pass the path through `--script-param fixture_path=...` and `app.params.fixture_path` instead. The default many-frame fixture now includes Korean characters and a space so future native runs exercise the regression. |

Evidence retained under `test-outputs/export-size-budget-rereview/`:

- Red: `--output 'test-outputs/export-size-budget-rereview/한글 경로'` failed with
  native Lua `missing '{'` at the generated JSON Unicode escape (`run-97b29f94`). This
  was a reproducible test-runner defect, not an MCP export error or timeout.
- Green: the same Unicode output root with the repaired runner and the preserved prior
  binary passed all 26 calls / 6 groups (`unicode-green.log`, `run-42c07d99`). It retains
  exact full/per-frame pixels, known bounds/strip order, duration, source metadata/bytes,
  padding/explicit zero and source/output preservation checks. The earlier SHARED-P2-001
  repair remains intact and is not reopened.
- Native parameter round trips: 4/4 each on macOS Aseprite 1.3.18.2 and the Linux amd64
  emulated supported floor 1.3.17.2. Exact values include ASCII, Korean/CJK/emoji, spaces,
  quotes, backslash, equals, newline and injection-like text (`param-roundtrip.log`).
  Paths travel as one argv value and are never interpreted as Lua code. The floor check
  validates this runner interface, not another execution of the entire floor export matrix.
- Final default package suite 7/7 PASS (`package.log`), Python syntax and Git whitespace
  PASS. Native calls retain timeout=30. No fixture bypass, timeout increase or dependency
  downgrade was used. Pin, all five binary bytes/checksums, live schema and guidance are
  unchanged; no rebuild is necessary for this test-only correction.

Repair-diff and closure review checked CLI option ordering (`--script-param` precedes
`--script`), argument boundaries, native return-code handling, saved path identity and
all callers of `fixture`; the per-frame oracle and failure snapshots remain unchanged.
The subsequent fresh-discovery pass traversed the full base-to-candidate scope again:
source/build/provenance and launcher selection, schema and handler constraints, generated
reference and exporter consumers, source/output guarantees and current/historical status.
No further finding or merge blocker was found.

Metrics for this follow-up only: initial discovery 1, mutation cycle 1, repair-diff review 1,
closure 1, full-scope fresh-discovery 1, total review passes 4. Initial P0/P1/P3=0 and P2=1;
new findings after repair/closure/fresh=0; repair-caused/reopened=0; VERIFIED=1;
ACCEPTED/OUT_OF_SCOPE/unresolved=0. Open P0/P1 remained zero. Stop reason: the reproduced
path failure is fixed, relevant native checks pass and no blocker remains. Duration not measured.

Final candidate is initial HEAD plus the runner diff, with 25 PR files fingerprinted before
this reporting-only addition. Manifest SHA-256:
`45bab63bf83610b5772cee579d245c8dbee3d904b30e1216886c690436b31b70`.
Relevant mutations after selection and candidate invalidations: 0. Changed during repair:
only the test runner; this section records results. Inspected for context: the native CLI,
MCP client, build/validation helpers and pinned export planner. Excluded: backend production
changes, unrelated tests/features, other worktrees, installations, merge/release operations.

Notes:

1. This narrow test-runner repair does not repeat the unchanged binaries' full Linux export,
   scratch/rollback/PBT, full source suite/race or GUI/install matrices. Their earlier results
   and unexecuted scopes above remain distinct; three platforms still have cross-build evidence only.
2. Older-runtime exact packed planning, total RSS control, crash recovery and external-writer
   protection remain unimplemented. Existing Top4 Pillow deprecation warnings remain a separate follow-up.

Follow-up verdict: **PASS_WITH_NOTES**. Commit/push updates the existing develop PR #18;
merging, release/publication, personal installation and worktree cleanup remain excluded.
