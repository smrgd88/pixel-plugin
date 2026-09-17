# Self-review preservation repair

This follow-up closes the self-review of MCP PR #12 and plugin PR #3. The reviewed starting candidates were MCP `27b30fd40d8d3697ac44794df5b6280b0ff4c67d` and plugin `8fdddde50270ce8a03f8dd770827e74c52ce5f25`. Their base commits remain MCP develop `3a20dedb4ae7edce2e0151a210cef2347bf5e9b9` and plugin develop `931f5129940ba201284620debb244cfafb64bdb7`.

Corrected MCP source: `b166b166ddb63af1a0d843f2cf30ec38541529eb`. Local full source validation: **888 test/subtest entries passed** with serial package execution, plus go vet.

## Findings and evidence

| Finding | Repair | Closure evidence |
|---|---|---|
| MCP-R1: grouped cels disappeared from duplicated frames | Native frame cloning covers nested groups; cloned cel objects are moved to the requested destination | Nested groups and source/destination order regression cases; bundled group test |
| MCP-R2: cel data/zIndex lost, changing composite pixels | Retain native cel objects instead of rebuilding only image/position/opacity | User data, zIndex, opacity, timeline color, user and extension properties; red-over-blue composite remains red |
| MCP-R3: selection JSON conversion lost nulls/objects/array entries | Never rewrite user sprite.data; keep mask/version in pixel-mcp/selection extension properties | Byte-exact data checks during repeated select/deselect for objects, arrays, null, text and large integers |
| PLUGIN-R1: defective source commit bundled | Pin and rebuild all five binaries from the corrected MCP commit | Source identity, hashes, actual tools/list and bundled saved-file tests |
| PLUGIN-R2: metadata-preservation description exceeded behavior | Describe the private storage and raw-data guarantee precisely | Actual metadata round-trip tests and updated inspector |

Two repair-discovery cases were also addressed. Temporary native cloning initially changed a tag ending at the insertion boundary; the final algorithm creates the requested insertion first, then clones/moves/deletes the temporary frame. A compatibility guard also prevents unrelated user JSON such as `selection: true` from being mistaken for a legacy mask.

## Storage and duplication design

Selection masks now live in a versioned extension-property namespace. A version marker remains after clearing, so stale legacy state in user data cannot resurrect. Legacy bounds/runs are read only; their original text is not rewritten. Unknown user metadata stays untouched instead of passing through a lossy JSON-to-Lua conversion. The inspector reads this effective selection separately from the original data text.

Frame duplication delegates group and cel attribute copying to the native operation. Frame indices are tracked numerically because intermediate insertions shift positions. After the requested insertion, a temporary native clone supplies complete cels; they move to the destination and the temporary frame is removed. Tests cover both sides of the source frame and tag boundaries.

References checked during implementation: [Sprite/newFrame](https://www.aseprite.org/api/sprite/#spritenewframe), [Cel/frame and attributes](https://www.aseprite.org/api/cel/), [extension properties](https://www.aseprite.org/api/properties/), [JSON representation](https://www.aseprite.org/api/json/). Runtime tests, not documentation assumptions alone, establish the actual saved result.

## Verification commands

In the MCP worktree:

```bash
go test -tags=integration ./pkg/tools -run TestReviewFix
go test -p 1 -count=1 -json -tags=integration ./...
go vet ./...
```

In this plugin:

```bash
./bin/test-plugin.sh
python3 bin/test-mcp-live.py --aseprite /absolute/path/to/aseprite
python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite
python3 bin/test-mcp-behavior.py --aseprite /absolute/path/to/aseprite
```

The behavior suite now includes 105 named scenarios: the previous 102 plus nested-group/cel-attribute, composite-order and metadata-null/empty round-trip cases. The eight complete skill workflows remain separate. No user artwork or user configuration is used as a test fixture.

## Review and scope record

Review-and-repair mode; the previous review supplied the initial ledger. Work was limited to frame duplication, selection storage/compatibility, regression tests and direct plugin consumers (pin/binaries/inspector/docs). No operation-warnings branch, public MCP tool/input schema, unrelated application feature or other session's checkout was changed.

Three bounded mutation passes were used: initial preservation fixes; tag-insertion correction exposed by new tests; defensive legacy-state parsing identified during review. Original R1/R2/R3 findings did not reopen. Repair diffs, closure conditions and a fresh traversal of the scoped aggregate change were reviewed before the final candidate was selected. No independent reviewer is claimed.

Existing full-suite success did not close these findings: the new tests first reproduced the losses, then checked the repaired saved state. One full local run recorded a 30-second timeout in the unchanged CreateTag path. The timeout threshold was not weakened; final full validation was repeated with serial package execution. Execution results and final source identity are recorded in the PR descriptions and build manifest.

Residual limits: GUI client workflows, every file/option combination and all non-local platforms are not exhaustively certified. Existing quantization/export/copy limitations in KNOWN_ISSUES.md still apply. Old metadata already lost by a previous build cannot be reconstructed. No merging or worktree/branch deletion is part of this repair.

## Final verification record

- MCP full source suite: 888 test/subtest entries passed, no failed/skipped tests (packages with no tests are separate).
- Plugin package/contract/wrapper suite: 7/7 passed.
- Corrected bundled server: 105/105 named behavior scenarios, all 50 tool basics included; the added group, composite and metadata cases passed.
- Complete skill recipes: 8/8 passed; smoke workflow: 37 successful actual MCP calls.
- Source go vet, Python syntax, four skill validators and whitespace checks passed.
- All five platform binaries were rebuilt; actual local execution used macOS arm64/Aseprite 1.3.18.2. GitHub CI status is tracked on the two PRs.

The original MCP-R1/R2/R3 and their plugin dependency/documentation findings are VERIFIED. Original P1 blockers decreased from 2 to 0. Repair-discovery tag handling and legacy type-guard cases were also verified. No original finding reopened and no unresolved in-scope P0/P1/P2 remains.

Review metrics for this follow-up: existing initial discovery reused; 3 bounded mutation passes, 3 repair-diff checks, 1 final closure review, 1 fresh full-scope pass. Final certification was selected after the last runtime/test mutation; no later implementation mutation occurred. Reporting/build provenance updates do not substitute for the actual execution evidence above. Independent review and merge authorization remain separate.

Verdict: PASS_WITH_NOTES — the repaired scoped conditions pass; GUI/all-platform/exhaustive-input certification is not claimed.
