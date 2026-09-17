# Testing checklist

## Automated default suite

Install `bin/requirements-test.txt`, then run `./bin/test-plugin.sh`.

- Plugin structure, skill/command frontmatter, documentation and MCP package files.
- Exact tool names in allowlists and coverage of every pinned tool.
- All documented mcp-example inputs validated against the real tools/list snapshot, including nested fields, required fields and unsupported arguments.
- Representative handler constraints and negative regressions for wrong export options, frame numbering, shading styles, missing paths and malformed pixels.
- Generated reference matches the snapshot; local documentation links resolve.
- All five bundled SHA-256 values and source pin match.
- Actual bundled MCP initialize/tools/list matches all input/output schemas. A temporary placeholder executable satisfies config loading; this is **not** an Aseprite integration test.
- Wrapper overrides, argument forwarding with spaces, invalid overrides, self-link recursion guard, source identity and explicit/config-environment precedence.

## Real Aseprite integration

Run `python3 bin/test-mcp-live.py --aseprite /absolute/path/to/aseprite`. It uses a temporary config and temporary artwork without changing user settings. PIXEL_MCP_BINARY selects a local server; otherwise the bundled server is tested.

- Health and real protocol initialization/tools list.
- Canvas/layer/frame creation and pixel round-trip.
- Forward/backward linked cels serialized as native Aseprite links; editing a source changes the linked target.
- Frame timing/tags, native save copies and nearest-neighbor scaling.
- PNG header/dimensions, GIF header, spritesheet and parsed metadata timing.
- Original sprite remains unchanged by copy-based export scaling.
- Indexed auto shading produces changed pixels and multiple real palette colors.
- Separate dithering and transparent/opaque-image quantization operations, palette-size bounds, and antialiasing analysis.
- Inputs and structured outputs checked against each live tool's schema.

## Manual client/platform verification

Before release, verify plugin installation/loading in the target client, environment propagation, skill selection and slash command execution. Run actual Aseprite workflows on each supported operating system/architecture; cross-compilation alone is insufficient. Inspect rendered artwork for artistic quality. Test other individual drawing/selection/transform operations when their workflows change.

Record the source commit, plugin commit, Go/Aseprite versions, platform and each skipped check with its reason. Never count absent Aseprite or protocol calls as a passing integration run. The reproducible commands are in [LOCAL_MCP.md](LOCAL_MCP.md).

## Full behavior and restored recipes

- `python3 bin/test-mcp-behavior.py --aseprite /absolute/path/to/aseprite`: all 50 tool basics plus named option/offset scenarios; independently reopen saved files with Aseprite. Failures are retained and produce a nonzero exit code.
- `python3 bin/test-skill-workflows.py --aseprite /absolute/path/to/aseprite`: run the eight skill-owned workflows.json recipes, checking actual pixels, timing and original-source preservation.
- Both tests use isolated generated files and caller-selected output directories. They do not mutate the user's artwork/configuration. The broad behavior test preserves its requests/responses and scenario ledger.
