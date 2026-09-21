# MCP warnings validation — 2026-09-21

These results were executed for this update. Earlier REPAIR_VALIDATION.md results
refer to the previous source and are not evidence of this run.

## Baseline and scope

- Task: [SHARED][FIX] MCP warnings 계약 및 스킬 대응.
- Worktree: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-fix-mcp-warnings`.
- Branch: `fix/shared-mcp-warnings`; base, initial HEAD and merge-base:
  `origin/develop` at `59075767d8627194d825bb9e869b3be518731077`. Initial tree clean.
- [MCP PR #11](https://github.com/smrgd88/pixel-mcp/pull/11) rechecked via GitHub:
  MERGED, head `133b9ab68475f1ac88ab34db6270dbd94c80e6a1`, merge/source pin
  `6c9ac5ec211df74aafa9b14a96b132aee0209be8`.
- Direct old-to-new tree diff from `b166b166ddb63af1a0d843f2cf30ec38541529eb`
  contains warnings additions in three handlers and the warning helper/tests, plus
  documentation. Existing behavioral repair code is retained; merge-base compare
  was not used as proof of preservation.
- Remote MCP develop subsequently observed at `897c2f1d218b712e0a5387bb3806671dce302ddf`
  (PR #13 capability checks, parent #11 merge). That separate feature is excluded;
  this update deliberately pins the requested #11 merge, not a moving remote ref.
- Exact snapshot comparison: 50 tools retained; all input schemas and existing
  fields identical. Only optional output `warnings` on flatten_layers,
  quantize_palette and scale_sprite added. Renderer regenerated the reference.
- Five release bundles built together with build-mcp.py; source identity and
  SHA-256 metadata validated. The MCP checkout was only read/archive-exported.

## Executed validation

Environment: macOS arm64, Python 3.14.6, isolated `test-outputs/venv`,
jsonschema 4.25.1, Go 1.25.0, Aseprite 1.3.18.2-arm64.
All commands ran from this worktree, with stale PIXEL_MCP_BINARY overrides removed.
Aseprite/config/temp data were isolated from user configuration.

| Check | Result |
|---|---|
| build-mcp.py --release | All 5 targets compiled; checksums and source commit match |
| bin/test-plugin.sh | 7/7 groups passed, including warning compatibility tests |
| validate-mcp-contract.py --live | 50 tools, 68 examples, 8 recipes, 9 rejected historical regressions; live schema match |
| test-mcp-warnings.py | Schema optionality, unknown code, malformed warnings, old responses, actual Client.call structured/text decoding and isError precedence passed |
| test-mcp-warnings.py --aseprite | 23 success conditions and 3 failure paths passed; text/structured equality, mode/layer count/dimensions verified |
| test-mcp-live.py --aseprite | 37 real calls passed; indexed shading, linked cels, PNG/GIF/sheet metadata |
| test-skill-workflows.py --aseprite | All 8 recipes passed |
| test-mcp-behavior.py --aseprite | 105/105 scenarios passed; 50 tools and existing pixel/selection/metadata regressions |
| go test -count=1 -json -tags=integration ./... | 916 test/subtest passes, zero failed/skipped tests; 4 tested packages pass, 5 packages have no tests |
| go vet ./... | Passed |
| git diff --check | Passed |

The warning matrix covers conversion omitted/false/true crossed with dither
false/true; flatten; empty/nearest/bilinear/rotsprite crossed with 2×2, 1×2, 2×1
and identity scales. Failure cases use missing sprites and remain MCP errors.

First attempts are not hidden: the warning matrix timed out once applying a
quantized palette, and the first behavior sweep was 104/105 with a timeout in
create_canvas before the cut-selection fixture. Both reported Aseprite's 30-second
command timeout while multiple suites were running. Full unchanged reruns passed;
concurrency is a suspected cause, not proven. No automatic operation retry was
added to the client or skills. Initial and rerun logs remain under ignored
`test-outputs/warnings/`; behavior artifacts are `run-ebaa6508` (initial) and
`run-7d38bfb5` (passing) under `test-outputs/mcp-behavior/`.

## Reproduction

```bash
python3 -m venv test-outputs/venv
. test-outputs/venv/bin/activate
python3 -m pip install -r bin/requirements-test.txt
unset PIXEL_MCP_BINARY
python3 bin/build-mcp.py /path/to/pixel-mcp --release --go /path/to/go1.25/bin/go
./bin/test-plugin.sh
# Set PIXEL_MCP_CONFIG to an isolated config with the real Aseprite path.
python3 bin/validate-mcp-contract.py --live
python3 bin/test-mcp-warnings.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-live.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-skill-workflows.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
python3 bin/test-mcp-behavior.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite
```

Go used the existing executable at
`/Users/keumheesung/Library/Caches/pixel-mcp-go/mod/golang.org/toolchain@v0.0.1-go1.25.0.darwin-arm64/bin/go`,
with GOMODCACHE at `/Users/keumheesung/Library/Caches/pixel-mcp-go/mod`.
Go test/vet ran in the pinned git archive exported to ignored
`test-outputs/warnings/mcp-source`, with the isolated PIXEL_MCP_CONFIG.

## Convergent review

Mode: review-and-repair, locked to the baseline-to-final worktree change (24 files,
including 5 binaries), plus direct consumers. Initial full-scope discovery 1;
fresh-discovery full-scope pass 1; total review passes 2. Repair cycles, repair-diff
passes, closure passes, final-candidate invalidations and post-snapshot relevant
mutations: 0. Closure is not applicable because review required no repair.

Finding ledger: P0/P1/P2/P3 = 0/0/0/0; new findings after review, repair-caused,
reopened, verified, accepted and unresolved findings = 0. Open blocker trend
remained 0 throughout. Stop reason: no evidenced in-scope defect after complete
contract/consumer/failure-path review and successful final validation.

Reviewed: source pin, snapshot, binary metadata/artifacts, reference renderer,
warning tests and runner wiring, shared warning guidance, three skills/examples,
two commands, local build guidance and changelog. Inspected for context:
Client.call, build/validator scripts, existing behavior/live/recipe tests and CI;
upstream handlers/helper and direct old/new source diff. Changed during repair:
none. Excluded: other worktrees, MCP #13, new UI/approval mechanisms, unrelated
features. Final candidate is the committed tree containing this report; the report
itself records evidence only. No merge or branch/worktree deletion performed.

Limits: protocol and real batch-Aseprite behavior were verified, not a host app's
rendered warning UI or an LLM's execution of the prose instructions. The host UI
was not exercised by these tests. Other four platforms were cross-compiled and
hashed but not executed because this session has a macOS arm64 host. Race/coverage
runs were not repeated; no Go production changes are made in this plugin. The two
transient timeouts remain disclosed as an environmental reliability risk.

Verdict: **PASS_WITH_NOTES** (UI/platform execution gaps and transient timeouts).
