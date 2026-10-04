# Codex project instructions

This is the Codex entrypoint for pixel-plugin, adapted from [CLAUDE.md](CLAUDE.md).
Use [README.md](README.md) for setup. This file provides repository instructions;
it does not register MCP servers or install skills. Explicit user instructions take precedence.

## Project and source of truth

pixel-plugin bundles Aseprite pixel-art workflows and the pixel-mcp stdio server.
Codex uses natural-language requests plus the skill guides below. The existing Claude
Code packaging is a separate client integration; do not assume its slash commands,
`$ARGUMENTS`, `allowed-tools`, or `${CLAUDE_PLUGIN_ROOT}` configure Codex.

- `skills/`: four shared workflows, each with SKILL.md and supporting references/examples.
- `commands/`: Claude slash-command files; use as workflow references in Codex.
- `bin/pixel-mcp`: platform launcher, selecting a bundled binary or `PIXEL_MCP_BINARY`.
- `config/mcp-source.json`: authoritative MCP repository/ref/commit pin.
- `config/mcp-contract.json` and [MCP_TOOLS.md](docs/MCP_TOOLS.md): tool schemas.
- `bin/mcp-build.json`: source/build provenance and five binary checksums.
- `config/README.md`: server configuration; `bin/`: builds and validation scripts.
- `.claude-plugin/`, `.mcp.json`, `CLAUDE.md`: Claude integration; keep components at
  the repository root, not inside `.claude-plugin/`.

Read version/tool counts from manifests and the contract rather than assuming cached
values. No sibling MCP checkout or installed plugin cache is automatically the running server.

## Git and workspace rules

Before editing, run these in the intended working directory:

```sh
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git worktree list --porcelain
```

Use terminal state, not the UI branch label. If the path, branch, or worktree differs from
what the task expects, report expected/actual values before editing.

- `main` is the production baseline; `develop` is the integration baseline. Start normal
  work from latest `develop`; never add feature commits directly to either branch.
- Use one dedicated branch and app-managed worktree per task. Do not share them across
  sessions. Use the session-connected Codex worktree by default, not an ad hoc temporary
  checkout created from an original-project session.
- When the user explicitly asks for an Orca worktree while retaining the current session,
  use `orca-cli` to create only the worktree, then set every command's working directory
  to that path. This is an explicit exception to session attachment, not permission to
  create another agent. Start a new agent/session only when the user requests a handoff.
- Order: determine area/type, inspect Git/worktrees, verify base, create the task branch
  and dedicated app-managed worktree, recheck actual path/branch, then implement.
- Task/session names: `[AREA][TYPE] description`. Areas: FE, BE, SHARED, OPS. Types:
  FEATURE, FIX, HOTFIX, REFACTOR, TEST, DOCS, CHORE, REVIEW, SPIKE, RELEASE.
- New branch names: `<type>/<area>-<task>` in lowercase with hyphens, e.g.
  `docs/shared-readme-refresh`. Worktree names: `<area>-<type>-<task>`.
  Do not rename an existing in-progress task branch.
- Keep FE and BE tasks separate. Large shared changes belong in a SHARED task.
  Modify only the assigned scope and worktree.
- Preserve unrelated uncommitted changes. If found, report them; do not switch branches,
  stash, reset, clean, delete files, or remove worktrees to get around them.
- Normal flow: `develop → task → tests/review → develop`. Release flow:
  `develop → release verification → main`. Hotfixes branch from `main` and must be
  reflected in both `main` and `develop` after completion.
- Merge into `develop` or `main` only when requested or separately approved. Review may
  use a separate review worktree; do not create an unnecessary review-only branch.
- Commit only task-related changes, preferably Conventional Commits such as
  `docs(shared): document Codex setup` or `fix(be): prevent refresh token replay`.
- Delete a task branch/worktree only after merge, a clean tree, and confirmation that
  no other session uses it. Preserve ignored validation evidence before cleanup.

## Skill routing in Codex

For a pixel-art task, read the relevant guide and only the supporting documents it calls
for. These are repository file reads; do not assume root `skills/` is a standalone Codex
skill-discovery directory. Installed skill discovery is separate from this routing.

| Task | Read first |
|---|---|
| Canvas, layers, shapes, pixels, selection, transforms | [Creator](skills/pixel-art-creator/SKILL.md) |
| Frames, timing, tags, linked cels | [Animator](skills/pixel-art-animator/SKILL.md) |
| Palettes, quantization, dithering, shading, AA, reference analysis | [Professional](skills/pixel-art-professional/SKILL.md) |
| PNG/GIF, image sequences, spritesheets, native copies | [Exporter](skills/pixel-art-exporter/SKILL.md) |

Use the actual connected tool names and schemas. An `aseprite` connection commonly
exposes `mcp__aseprite__*`; do not invent tools when a host uses another prefix.
Skill allowlists describe intended tools, not Codex permission grants. If MCP is missing,
report the missing connection and follow README setup within the user's authorization.

## MCP operation contracts

- Operations act on saved files, not unsaved GUI state. Keep the returned absolute
  file_path and use it as sprite_path. Frames are one-based; export frame_number=0
  means all frames. Coordinates are zero-based.
- Check `isError` before decoding success. Some tools use uppercase `Success`.
  Inspect pixels/output files before claiming success; get_sprite_info does not list
  frame durations or tags.
- Follow [warning rules](docs/MCP_WARNINGS.md) and [error rules](docs/MCP_ERRORS.md).
  Report all returned warnings, actual error codes/request IDs, and all error.recovery
  entries. Do not infer retryability from message text or unknown codes.
- On file_rollback_failed, stop automatic retries and preserve recovery folders/backups.
  Some outputs may remain changed; inspect the original canonical output location.
- Follow [preview/recovery rules](docs/MCP_SAFETY.md). Only quantization, auto-shading,
  and flattening support dry_run. Preview-only requests must not apply an edit.
  History is opt-in; do not silently enable it, invent IDs, or bypass a refused undo
  with automatic snapshot restore.
- Follow [export/analysis rules](docs/MCP_EXPORT_ANALYSIS.md). Report every returned
  sequence file. Scale/FPS/layer filtering require a native copy, not invented export
  parameters. Keep the original source intact.
- Server config precedence: `--config` > `PIXEL_MCP_CONFIG` > user-home
  `.config/pixel-mcp/config.json`. Use absolute executable/config paths; preserve
  existing settings. Reconnect after changes. Health is not a drawing test.

## Implementation and validation

Read [local MCP development](docs/LOCAL_MCP.md) before builds or bundle updates.
Build from an exported committed revision without modifying other MCP worktrees.
When changing the bundled MCP, keep source pin, five binaries, checksums, schemas,
skills/examples, and affected docs consistent. Keep user paths out of distribution files.

Run checks appropriate to the change. For the default plugin validation:

```sh
python3 -m venv test-outputs/venv
test-outputs/venv/bin/python -m pip install -r bin/requirements-test.txt
PATH="$PWD/test-outputs/venv/bin:$PATH" ./bin/test-plugin.sh
```

The default suite covers packaging, docs, skill/command structure, contracts, checksums,
and wrapper/client regressions. It does not substitute for real Aseprite behavior tests.
For affected workflows, run the relevant `bin/test-mcp-*.py` or skill workflow tests
with a real Aseprite executable and isolated config/temp/snapshot stores. Do not alter
user history/config to run tests. Add compilation, unit/PBT, integration, lint/type/build
checks when relevant to changed source. Report skips, reasons, and unverified behavior.
A cross-build is not native execution on that platform.

For Markdown-only changes, check links, documented commands/contracts, and repository
doc validation. Do not claim GUI installation, automatic skill selection, or release
verification based only on schemas and CLI checks.

## Completion report

Report the task name, actual worktree path, task branch, base branch/commit, main changes,
commit hash (or explicitly no commit), tests and skipped checks, remaining uncommitted
changes, review/merge state, and whether branch/worktree cleanup is permitted.
