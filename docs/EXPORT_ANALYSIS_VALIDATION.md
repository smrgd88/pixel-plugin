# Export/reference sync validation — 2026-09-27

> Historical execution record for the source/candidate named below. See [current fix and merge status](BUG_STATUS.md) for the present bundle and remaining issues.

Task: **[SHARED][FIX] MCP 시퀀스 출력 및 참조 분석 반영**.
This record contains new executions. Prior color/warnings validation documents
remain historical and are not presented as runs of this candidate.

## Source and candidate

- Worktree: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-fix-mcp-export-analysis`.
- Branch: `fix/shared-mcp-export-analysis`.
- Plugin base, initial HEAD and merge-base: `acf2ff702181a8e3b71d758dd1e79a726c4e3f3b`
  (merged plugin PR #6). Initial tree clean; remote develop rechecked unchanged.
- Old MCP pin: `a7ffa0fc61763685b195f41b90ba6d1f07fdeece`.
- New pin: `8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966` (merged MCP #20), including
  #18 (`363d6fa0960ebd7d339fc1edca6beb538f44e8c4`). Both upstream CI test jobs pass.
  Closed documentation PR #19 is superseded by #20.
- Direct old/new source tree diff inspected. Build helper uses git archive; no MCP
  checkout or other task worktree was edited. Old binary was read-only during comparison.
- Five platform binaries rebuilt with Go 1.25.0; all hashes, source pin, snapshot and
  --version agree. Tool count remains 50. Only export_sprite and analyze_reference
  changed in tools/list. Optional files preserves the two legacy export fields.

## Same-input before/after comparison

Both committed binaries ran on the same two-frame, 8×8 native input, with grouped,
hidden and offset layers. All files/configs/output for both runs were isolated in
this worktree. This is a **direct MCP comparison, not a skill execution**.

| Operation | Old bundled MCP | New bundled MCP |
|---|---|---|
| All-frame `sequence.png` | Error: requested staged output missing; no final PNGs | sequence_0001.png + sequence_0002.png; both returned in files |
| All-frame `walk007.png` | Success response but only walk007.png remained (100 bytes); second frame absent | walk007_0001.png (87 bytes) + walk007_0002.png (79 bytes) |
| Analyze BMP | `image: unknown format` | Success; brightness/edge maps match first-frame PNG |
| Analyze native .aseprite | `image: unknown format` | Success; visible frame 1 analyzed, source unchanged |

The new first output contains **63 red pixels + 1 green pixel at (2,3)**;
second output contains **64 blue pixels**. Hidden white content is excluded.
Legacy file_size is 87 bytes (first file), while the explicitly summed total is
166 bytes. Existing base/stale files outside the returned list are preserved.
Comparison evidence: ignored `test-outputs/sync/comparison/results.json` and its
before/after output directories. No old result was inferred from PR prose alone.

## New execution results

Environment: macOS arm64, Aseprite 1.3.18.2-arm64 / API 41, Go 1.25.0,
Python 3.14.6, jsonschema 4.25.1. Isolated venv/config and canonical worktree-local
TMPDIR; Aseprite suites ran sequentially. Raw evidence is under `test-outputs/sync/`.

| Check | Result |
|---|---|
| Five release builds / source identity / SHA-256 | Pass |
| test-plugin.sh | 7/7 groups; 50 tools, 71 documented examples, 8 recipes, 10 rejected regressions |
| test-mcp-export-analysis.py (offline, also in default suite) | Optional files/nullable/legacy schema, JSON text and structured decoding, missing frame field rejection, isError precedence pass |
| test-mcp-export-analysis.py --aseprite | 28 calls including negative cases; PNG/BMP/JPG ordered file paths, frame numbers, actual sizes; exact lossless frame pixels; jpeg alias; GIF and one-frame compatibility |
| Export failure/protection | Bad extension/frame, source alias, read-only sequence destination rejected; source/base/stale/old outputs preserved |
| Reference formats | PNG/JPEG/GIF/BMP/native success; BMP/native first-frame brightness/edge comparison; indexed/grayscale read-only .ase unchanged; corrupt input rejected and private temp data cleaned |
| test-mcp-color-operations.py | 36 exact-color mode/algorithm/dither/conversion cases; density, transparency and source protection pass; old PNG rejection expectation updated to successful sequence/base preservation |
| test-mcp-warnings.py --aseprite | 23 success conditions + 3 error paths; existing warning contract preserved |
| test-mcp-live.py --aseprite | 37 real calls pass |
| test-mcp-behavior.py --aseprite | 105/105 pass |
| test-skill-workflows.py --aseprite | 8/8 recipes pass |
| Apple regeneration / engine | Three animations regenerated through 231 MCP calls; pixels/exports/timing and Node engine pass |
| go test -count=1 -json -tags=integration ./... | 1094 test/subtest passes, zero failures/skipped tests; 5 tested packages pass, 4 packages have no tests |
| go vet ./... / Python compile / git diff --check | Pass |

The first targeted test attempt failed in its verification step: Aseprite's CLI
implicitly opened neighboring numbered images and encountered the deliberately
invalid stale-file sentinel. The exported PNG bytes were valid. The independent
single-image inspector now uses --oneframe for PNG/JPG/BMP to avoid sequence
coalescing, and the entire targeted test passed afterwards. This was a test-harness
correction before formal review; no exported file or source behavior was bypassed.

## Actual Codex skill execution

Used **pixel-art-exporter** and **pixel-art-professional**, with both SKILL.md reads
recorded. The unmodified user-style prompt asked to export all scene.aseprite frames
using base walk007.png, then analyze reference.bmp and scene.aseprite at 8×8.
It did not dictate the returned file list or instruct the model to repeat a result.

Codex made **4 actual MCP calls**: get_sprite_info, export_sprite and two
analyze_reference calls. All succeeded. The final Korean answer listed both actual
PNG paths, source frame numbers, 8×8 dimensions, sizes **87/79 bytes**, and the
explicit total **166 bytes**. It stated that walk007.png is a naming base, and native
analysis uses only the visible composite of frame 1. Independent PNG reopening
confirmed the 63 red + 1 green / 64 blue counts, and byte comparison confirmed both
reference files were unchanged.

The agent also disclosed that extracted palette entries are not an exact inventory
of every input color: BMP/native palette extraction differed, while brightness/edge
maps matched. This update changes format loading, not k-means quality/determinism.
No full-animation analysis or identical palette extraction is claimed.

Evidence: codex/events.jsonl and codex/final.txt. This was an isolated Codex CLI using
real skills and MCP, without changes to global settings. Installed-plugin discovery
and desktop GUI rendering remain deferred at the user's request.

## Reproduction

```bash
python3 -m venv test-outputs/venv
. test-outputs/venv/bin/activate
python3 -m pip install -r bin/requirements-test.txt -r examples/apple/requirements.txt
unset PIXEL_MCP_BINARY
./bin/test-plugin.sh
python3 bin/test-mcp-export-analysis.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-color-operations.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-warnings.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-live.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-behavior.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-skill-workflows.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 examples/apple/generate.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite --output test-outputs/apple
node examples/apple/demo/test-engine.cjs
```

Go tests ran in the pinned git archive under test-outputs/sync/mcp-source, with
PIXEL_MCP_CONFIG pointing to the isolated config and TMPDIR to test-outputs/sync/go-tmp.
Go executable: `/Users/keumheesung/Library/Caches/pixel-mcp-go/mod/golang.org/toolchain@v0.0.1-go1.25.0.darwin-arm64/bin/go`;
GOMODCACHE is the parent module cache. `--output` may retain live-test evidence in a
fresh directory; the default uses temporary output and cleans it afterwards.

## Scoped convergent review

Mode: review-and-repair. Reviewed base-to-final change: 26 files including five
binary artifacts, source/snapshot metadata, example/allowlist consumers, tests,
reference generator output and active guidance. Context: upstream export planning,
output staging/rollback, reference loader/rendering, Client.call, build/validator,
existing behavior/recipe scripts and apple generator.

Initial discovery 1, fresh-discovery full-scope review 1, total review passes 2.
Repair cycles, repair-diff review, closure and final-candidate invalidations: 0.
Findings P0/P1/P2/P3: 0/0/0/0; new/reopened/accepted/verified/unresolved findings: 0.
No review repair was required; closure is not applicable. Stop reason: complete
contract/consumer/error-path review and successful final checks with no evidenced
in-scope defect. Runtime/schema/skill/test hashes remained unchanged after candidate
selection; reporting-only records do not alter those semantics. Duration not measured.

Excluded: MCP source edits, other worktrees, analysis algorithm redesign, whole-GIF
logical canvas analysis, dry-run/undo/crash recovery and unrelated features.
Other four target binaries were cross-built and hashed, not natively executed.
Local race/coverage and minimum-version installation tests were not repeated;
upstream CI and local native integration are separately identified. Sequence
replacement is per-file atomic and ordinary failures attempt rollback; this is not
whole-set crash atomicity or guaranteed recovery against external writers.
No develop/main merge or worktree/branch cleanup is performed.

Verdict: **PASS_WITH_NOTES**.
