# Behavior repairs and skill restoration

This records the earlier candidate. The subsequent self-review preservation fixes are documented in [SELF_REVIEW_REPAIR.md](SELF_REVIEW_REPAIR.md).

The original synchronization corrected tool contracts but removed useful creative guidance. A subsequent real-output sweep found server behavior failures that the original schema/smoke checks did not catch. This follow-up restores the useful skill material, repairs the reproducible server defects in a separate MCP branch, and verifies complete workflows.

## Candidate and scope

- Plugin task: `[SHARED][FIX] MCP 기능과 플러그인 동기화`, `fix/shared-mcp-sync`, based on plugin develop `931f5129940ba201284620debb244cfafb64bdb7`; follow-up starts at `82a8f08368e5b5c2e62549c4ab4513a91a33f2a9`.
- Separate MCP task: `[SHARED][FIX] MCP 도구 동작 회귀 수정`, `fix/shared-tool-behavior`, based on MCP develop `3a20dedb4ae7edce2e0151a210cef2347bf5e9b9`.
- Repaired MCP commit: `27b30fd40d8d3697ac44794df5b6280b0ff4c67d`. All bundled platforms and the contract snapshot are pinned to this exact commit.
- The operation-warnings feature under development in another MCP worktree is not merged into this repair. No other session's checkout was modified.
- No develop/main merge is authorized or performed. Keep both task branches/worktrees until review and integration complete.

## Findings and closure evidence

| ID | Failure / loss | Repair | Status and evidence |
|---|---|---|---|
| MCP-P1-001 | Indexed default pixel writes could store out-of-palette values | Resolve indexed writes against the sprite palette without changing unsnapped RGB behavior | VERIFIED: real saved indexed colors; default and explicit palette cases |
| MCP-P1-002 | Binary dithering patterns became a solid color | Use actual matrix value range for threshold normalization | VERIFIED: 16 pattern variants in behavior sweep, plus Go pixel-count regressions |
| MCP-P1-003 | SelectAll invalid persistence, lost ellipse masks and incorrect combination behavior | Persist row runs; restore legacy rectangles; preserve/move/combine the actual mask | VERIFIED: select/copy, ellipse/cut, subtraction/intersection/empty selection/negative move, metadata preservation |
| MCP-P1-004 | Positioned cels copied empty clipboard pixels; small targets clipped pasted content | Translate canvas/cel coordinates, apply exact selection mask and expand destination | VERIFIED: positioned copy/cut/paste and original pixel checks |
| MCP-P1-005 | Transparent quantization failed, exceeded requested color count, or reported nil mode | RGBA parsing, transparent-slot budget, reducible octree root, explicit mode naming | VERIFIED: three algorithms, RGB/indexed outputs, alpha and target-size assertions |
| MCP-P1-006 | Repeated duplicate_frame append shifted the existing action pose | Capture independent source images and insert an empty frame at the requested index | VERIFIED: repeated-append regression and complete attack recipe |
| SHARED-P2-001 | Creative guidance replaced by API-only reference material | Restore dimensions/composition, pose timing, material ramps, AA/pattern and delivery choices | VERIFIED by original/current content comparison and recipe references |
| SHARED-P2-002 | Complete examples replaced by independent calls | Add eight skill-owned executable workflow recipes, with required state and real result checks | VERIFIED: 8/8 recipes executed |
| SHARED-P2-003 | Animator's linked-layer workflow lacked add_layer allowance | Include required layer/canvas tools in the animator allowlist | VERIFIED by allowlist checks and linked-cel workflow |
| SHARED-P2-004 | Copy source described as active cel instead of first layer/frame | Correct the source-target limitation and selection persistence documentation | VERIFIED against MCP implementation and clipboard tests |

The original baseline sweep was **79 passing / 23 failing scenarios**. The repaired implementation completed **102 passing / 0 failing scenarios across all 50 registered tools**, with 362 actual tools/call requests including setup and inspection. Scenario counts are not unique tool counts or a percentage of all possible input combinations.

## Restored material

- Creator: silhouette/layer planning and original heart/sword/layered-character ideas. Incorrect color objects, implicit sprite state and undocumented canvas parameters were not restored.
- Animator: anticipation, follow-through, arcs, holds and varied timing; idle and attack recipes clear displaced pixels and preserve distinct poses.
- Professional: steel/fabric/skin ramps, directional light, selective AA/contact shading, and manual checker/hatch/weave patterns. Artistic choices are examples, not universal prohibitions on black/white or fixed hue shifts.
- Exporter: format decisions, integer nearest-neighbor scaling, metadata/timing consumption and engine filtering considerations. Unverified engine-version code and fictional engine-specific MCP formats were not restored.

Original Git content remains available at the plugin base commit. Recipes reside in each skill's workflows.json, and the owning examples.md describes their prerequisites and output checks.

## Validation

Environment: macOS arm64, Aseprite 1.3.18.2-arm64, Go 1.25.0, MCP SDK 1.4.1.

- MCP `go test -json -tags=integration ./...`: **861 test/subtest entries passed**, no failed/skipped tests. Five packages have no tests. `go vet ./...` and whitespace checks passed.
- Broad real behavior test: all 50 tools and 102 named scenarios, with independent read-only Aseprite inspection of saved files.
- Complete workflows: heart silhouette, sword parts, separate character/background, two-frame idle without trails, three-stage attack timing, steel palette shading, exact manual checker, and copy-only scaled animation export.
- Bundled smoke: 37 successful calls, including transparent quantization and re-inspection of layer structure after its destructive dither step.
- Default plugin validation: original structure/frontmatter/docs/package checks plus schema, recipe references/allowlists, wrapper/config precedence, exact live tools/list and all five binary hashes.
- Release builds cover darwin amd64/arm64, linux amd64/arm64 and windows amd64 from the same committed source. Execution validation here covers the macOS arm64 binary only.

One earlier full run while multiple Aseprite suites ran simultaneously timed out in an existing downsampling test after 30 seconds. The final source suite ran separately and passed. The timeout limit was not weakened. Initial fixture assumptions about GIF background transparency and native link targets were corrected before final counts; these were test-fixture issues, not claimed server repairs.

The transparent palette budget and repeated-append defects were discovered while strengthening the validation. They were fixed with regression evidence, not waived to achieve a green result.

## Reproduce

```bash
python3 -m pip install -r bin/requirements-test.txt
./bin/test-plugin.sh
python3 bin/test-mcp-live.py --aseprite /absolute/path/to/aseprite
python3 bin/test-mcp-behavior.py --aseprite /absolute/path/to/aseprite
python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite
```

The latter three commands use actual Aseprite and temporary/generated sprites. Set PIXEL_MCP_BINARY to explicitly choose another build; default execution uses the bundled candidate. The behavior runner preserves a scenario ledger, requests/responses, version and fixtures under test-outputs/mcp-behavior. It exits nonzero on any failed scenario. The recipe runner preserves native/PNG/GIF/sheet results under test-outputs/skill-workflows.

## Review record and limits

Review-and-repair mode: one grouped repair cycle with regression-driven implementation refinements, followed by a repair-diff review, closure review and fresh-discovery pass. The initial discovery is documented in the preceding task's local review ledger. Final snapshot selection occurs after repaired source pin, generated reference and binaries are updated; no further runtime mutation is certified by this record.

Initial scoped risks: five MCP root-cause groups and four skill P2 findings. One additional existing frame-duplication defect was exposed by a restored recipe. Final unresolved scoped P0/P1/P2: zero; no accepted/reopened findings. No independent agent reviewer is claimed.

Reviewed: repaired MCP paths and regression tests; plugin skills, recipes, contract/build linkage and validation scripts. Inspected for context: source schemas and direct callers/Lua generators. Excluded: unrelated MCP feature branches, GUI client installation/skill-selection behavior, other-platform Aseprite execution, and exhaustive concurrency/performance/all-option coverage.

Residual boundaries remain documented in KNOWN_ISSUES.md: batch file semantics, copy's fixed source, export input limits, and the quantizer's existing destructive dither workflow. Use native copies for experimentation. Full source tests and the named behavior/recipe conditions pass; that is not a claim that every possible file and option combination has been tested.

Verdict: PASS_WITH_NOTES for this scoped repair, subject to normal external review and separate authorization before merging.
