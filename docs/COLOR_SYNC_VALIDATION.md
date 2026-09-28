# MCP color sync validation — 2026-09-27

> Historical execution record for the source/candidate named below. See [current fix and merge status](BUG_STATUS.md) for the present bundle and remaining issues.

Task: **[SHARED][FIX] MCP 감색 및 density 수정 반영**.
This is a new execution record. WARNINGS_VALIDATION.md and REPAIR_VALIDATION.md
remain historical records; their counts are not reused as this run's results.

## Candidate and source

- Worktree: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-fix-mcp-quantization-sync`.
- Branch: `fix/shared-mcp-quantization-sync`.
- Plugin base / initial HEAD / merge-base: `fdbec49b87e812a40c33ad2da880e471bfe75104`
  (latest origin/develop at start and before PR). Initial tree was clean.
- Old MCP pin: `6c9ac5ec211df74aafa9b14a96b132aee0209be8`.
- New MCP pin: `a7ffa0fc61763685b195f41b90ba6d1f07fdeece`, merged PR #17;
  final upstream head `0239a3c780a452e900533cafb7405dff6e8e07fb`, CI test SUCCESS.
- Includes merged #16 quantization, #13 capability probe, #14 file protection and
  #15 documentation. PR #18 PNG-sequence repair was OPEN and is not included.
- Direct old/new source diff inspected, not a merge-base GitHub compare.
- All five binaries built with build-mcp.py from git archive; the MCP checkout was
  not changed. Source, snapshot, --version identity and all SHA-256 hashes agree.
- Actual tools/list: 50 tools, only draw_with_dither and quantize_palette differ.
  Density adds nullable numeric input; quantization descriptions clarify mode,
  pixel remapping and single-frame/raster limits. Existing warnings are unchanged.

## Environment and results

macOS arm64, Aseprite 1.3.18.2-arm64 / API 41, Go 1.25.0, Python 3.14.6,
jsonschema 4.25.1. Tests use this worktree's isolated venv/config and bundled MCP.
Aseprite suites ran sequentially. Generated data and raw logs live under ignored
`test-outputs/sync/`; none are user's source artwork.

| Check | This execution |
|---|---|
| build-mcp.py --release | 5 targets compiled; metadata/hashes verified |
| test-plugin.sh, final candidate | 7/7 groups passed; 50 tools, 68 examples, 8 recipes, 10 rejected regressions, null/numeric density compatibility |
| test-mcp-color-operations.py | 36 mode × algorithm × dither × conversion combinations preserve exact two-color positions in native files AND exported PNGs |
| Additional color checks | RGB pixel remapping with both options false, transparency with preserve false/true, 3 density default forms, 32 pattern endpoints, indexed endpoints, tiny positive threshold and outside-region preservation |
| Rejection/protection | Invalid density, animation/tilemap rejection, PNG-sequence failure with original output unchanged, hardlink refusal and two-process concurrent writers passed |
| Original four-color reproducer | All 4 dither/conversion combinations now have two actual colors; former indexed collapse and RGB no-remap are absent |
| test-mcp-warnings.py --aseprite | 23 success conditions and 3 failures; JSON text/structured content equality and warning conditions pass |
| test-mcp-live.py --aseprite | 37 calls pass, including capability health JSON and exports |
| test-mcp-behavior.py --aseprite | 105/105 pass; independent saved-file inspection |
| test-skill-workflows.py --aseprite | 8/8 recipes pass |
| Apple example | Regenerated all 3 animations through 231 actual MCP calls; pixels, metadata/timing and exports verified; static assets verification and Node engine tests pass |
| Upstream Go integration | Initial full run: 1037 test/subtest passes, 3 path-string failures; corrected environment rerun of entire affected pkg/aseprite: 338/338 pass (details below) |
| go vet ./... | Pass |
| Python syntax / git diff --check | Pass |
| Codex skill → MCP → final user answer | 15 actual tool calls, zero failures; two-color indexed output and density=0 pixels independently verified; all 3 warnings explained |

The final color test also asserts the fixture's expected 64 colored pixels before
quantization, so preserving an already broken input cannot count as a pass. PNG
verification is independent of the MCP response and palette-size claim. Tilemap
setup is fixture-only CLI Lua using the [NewLayer API](https://www.aseprite.org/api/command/NewLayer);
no arbitrary Lua MCP feature is added.

### Failures investigated during implementation

- The existing inspector treated transparent mask index 255 outside a compact
  palette as invalid before considering transparency. It now recognizes the mask
  first on non-background layers, while retaining invalid-index diagnostics for
  opaque pixels. Full behavior and transparent color tests passed afterwards.
- The new negative-input test initially expected isError for a string density.
  SDK type validation instead returns JSON-RPC -32602. The test now distinguishes
  that error from successful results and still checks original bytes unchanged.
- Strengthened fixture assertions exposed an indexed palette setup that put blue
  in Aseprite's clamped mask slot. The fixture now leaves unused slots at both ends;
  it must contain known red/blue pixels before the operation is tested.
- Go's first full integration run failed only in TestFileProtectionReadOnlyAndHardLink,
  TestFileProtectionCommitFailure and TestFileProtectionSymlinkParentTraversal:
  expected /var/... versus canonical /private/var/... on macOS. No source was patched.
  Set TMPDIR to the canonical worktree-local `test-outputs/sync/go-tmp` and reran
  first those three tests, then the entire affected package with integration tags.
  Both passed. All other tested packages passed in the initial full run; together
  these runs validate all 1040 test/subtest identities. Four packages have no tests;
  zero individual tests were skipped. This is not described as a single clean
  first full-suite execution. Logs: go-integration.log, go-path-recheck.log,
  go-aseprite-canonical.log.

## Codex evidence

Used an isolated Codex CLI invocation with the original creator/professional skills
linked into the test workspace and the bundled MCP configured for that invocation.
Only the relevant test tools were allowed. Global Codex settings were not changed.
The prompt requested two-color reduction and a density=0 copy, without requesting
warning reporting explicitly. Quantization ran once and dither fill ran once.

The final answer reported red/blue **32 pixels each** in the indexed image and
**64 red pixels** for density=0, then explained palette information loss, indexed
color/transparency representation changes and editable layer structure loss.
Independent Aseprite reopening confirmed both pixel counts. No warning-triggered
retry, retrospective approval or undo claim occurred. Evidence: codex/events.jsonl
and codex/final.txt. This is actual model/skill/tool behavior, not a scripted mock.
Installed-plugin discovery and desktop GUI rendering remain untested, as deferred
by the user; no such verification is claimed.

## Reproduction

```bash
python3 -m venv test-outputs/venv
. test-outputs/venv/bin/activate
python3 -m pip install -r bin/requirements-test.txt -r examples/apple/requirements.txt
unset PIXEL_MCP_BINARY
./bin/test-plugin.sh
python3 bin/test-mcp-color-operations.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-warnings.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-live.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-behavior.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-skill-workflows.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 examples/apple/generate.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite --output test-outputs/apple
node examples/apple/demo/test-engine.cjs
```

Go was invoked from the pinned archive with `go test -count=1 -json -tags=integration ./...`
and `go vet ./...`, GOMODCACHE at `/Users/keumheesung/Library/Caches/pixel-mcp-go/mod`,
executable `golang.org/toolchain@v0.0.1-go1.25.0.darwin-arm64/bin/go` under that cache,
and PIXEL_MCP_CONFIG pointing at the isolated real-Aseprite config. The package rerun
used the same command with `./pkg/aseprite` and canonical TMPDIR.

## Convergent review

Review-and-repair of the base-to-final candidate, 27 changed files including
5 binary artifacts. Context: upstream final source/helper/wrappers, Client.call,
build/validator/renderer, existing live/behavior/recipe tests and apple generator.
No MCP source edits, other-worktree edits, unrelated features, or PR #18 work.

| ID | Priority | Evidence / correction | Final status |
|---|---|---|---|
| SHARED-P2-001 | P2 | New pixel assertions could accept a broken source or missing output pixels. Require the known 64-pixel source and identical coordinate sets; final native/export/endpoint matrix passes. | VERIFIED |
| SHARED-P2-002 | P2 | New get_pixels guidance was unavailable in exporter/palette allowlists. Added the tool and explicit workflow references; default allowlist/example validation passes. | VERIFIED |
| SHARED-P2-003 | P2 | Stronger checks exposed an indexed fixture's blue color in the transparent mask slot. Reserve unused slots and assert exact source colors; final 36-case matrix passes. | VERIFIED |

Initial discovery 1, mutation cycle 1 (including fixture correction during verification),
repair-diff review 1, closure 1, fresh full-scope discovery 1: total review passes 4.
Initial P2 findings 2; one new fixture finding exposed during verification; reopened 0,
accepted 0, unresolved 0, repair-caused product defects 0. P0/P1 remained 0 throughout.
One preliminary candidate snapshot was replaced after fixture correction; final
candidate had no runtime/contract/test changes after its successful verification.
Reporting-only validation records do not change runtime semantics.

Changed during review: new color test and get_pixels consumer allowlists/guidance.
Closure checked all three findings and affected consumers; fresh discovery traced
source pin → wire schema → examples/allowlists → warnings/pixel evidence → exports
and file-protection errors. Stop reason: no remaining evidenced in-scope defect,
final validation completed. Duration not measured.

Limits: other four target binaries were cross-built, not natively executed. The local
race/coverage suite was not rerun; native integration, static analysis and upstream
PR CI are separately reported. Actual minimum-version installation was not repeated.
BMP/native analysis support and numbered PNG sequence contract remain known upstream
limitations. Single-file protection does not imply undo, backups or multi-file atomic
publish. No develop/main merge or worktree/branch cleanup is performed.

Verdict: **PASS_WITH_NOTES**.
