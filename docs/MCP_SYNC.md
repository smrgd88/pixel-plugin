# Original MCP develop synchronization audit

This records the first synchronization. The later behavior repair, restored workflows and current pinned build are documented in [REPAIR_VALIDATION.md](REPAIR_VALIDATION.md).

## Source baseline

Plugin base: origin/develop `931f5129940ba201284620debb244cfafb64bdb7`.

MCP source baseline: origin/develop `1076166edf99f60e92bfd7fc4def261264930dcb`. At synchronization, the fetched remote and local develop were identical (0 commits ahead/behind). The inspected MCP worktree had moved to a documentation branch; its code was unchanged from develop. Builds use an archive of the pinned commit, not uncommitted files or that branch's moving HEAD.

The live server registers **50 tools**. This sync does not claim 50 newly added tools: many were already in source but absent from skills or incorrectly documented. Develop includes the Go 1.25/MCP SDK 1.4.1 migration, explicit/environment config support, native linked-cel fixes and indexed auto-shading color preservation. The protocol version string alone does not identify these fixes.

## Mapping and corrections

| Area | Prior mismatch/omission | Current mapping |
|---|---|---|
| Canvas and drawing | Implicit active sprite; inconsistent paths and defaults | Carry create_canvas.file_path as sprite_path; explicit layer/frame and required shape fields; inspect pixels |
| Animation | Fictional frame/tag-list and linked-cel aliases; zero-based frames | add_frame/duplicate_frame/set_frame_duration/create_tag/delete_tag/link_cel; one-based frames and distinct returned indices |
| Native links | Linking after copying a populated target | Create frames before a new shared layer, draw one source cel, link only into absent target cels; forward/backward links verified |
| Dithering | apply_dithering and unsupported algorithm options | draw_with_dither region + two colors + supported pattern; separate from image quantization |
| Palette | quantize_colors and incomplete preset/edit support | quantize_palette, set/get/edit/add/sort/harmony tools; explicit algorithms and preservation flags |
| Shading/AA | Missing or vague generated shading and smoothing workflows | apply_auto_shading vs apply_shading styles/inputs distinguished; suggest_antialiasing preview/apply behavior |
| Image tools | Unmapped analysis/import/downsample/transform/selection capabilities | Creator and professional skills cover every remaining registered tool, with batch-process and selection limitations |
| Export | export_png/export_gif aliases; output file_path; unsupported scale/tag/loop/layout options | export_sprite + format/output_path/frame_number; export_spritesheet supported layouts; copy-based scaling/FPS/filtering |
| Responses | Assumed generic success and invented sprite metadata | Exact input/output schemas, uppercase Success where required, file-size and metadata verification |
| Runtime | Bundled executable disconnected from local source | PIXEL_MCP_BINARY override, non-mutating pinned-source build, updated five-platform bundles and SHA-256 provenance |
| Configuration | Inconsistent hardcoded config env and Windows path | --config > PIXEL_MCP_CONFIG > user-home .config path; environment inherited by plugin |

See [skill routing](../skills/README.md), [command routing](../commands/README.md), [all tool inputs/outputs](MCP_TOOLS.md), and [validated examples](../skills/pixel-art-creator/examples.md). Every tool appears in an explicit skill allowlist and a schema-checked example. Preset color arrays are maintained in [palettes.json](../config/palettes.json).

## Validation and remaining scope

The default suite adds actual MCP initialization/tools-list comparison, documented JSON Schema examples, allowlist coverage, response schema drift, negative contract regression cases, wrapper/config tests and binary checksum verification. The original five file/structure checks remain.

Real Aseprite testing covers linked-cel serialization and edits, indexed auto-shading colors, export copy/scaling, PNG/GIF/sheet outputs and frame timing, dithering, opaque palette quantization and antialiasing inspection. Commands and distinctions are in [the testing checklist](TESTING_CHECKLIST.md).

A separate upstream defect was reproduced: transparent-image quantization emits `#00000000`, which the MCP palette color parser rejects. It is documented in [known issues](KNOWN_ISSUES.md), explicitly detected by the integration test, and not represented as successful quantization. No MCP checkout was modified. An alpha color parsing/transparent-palette fix needs its own MCP task.

Cross-builds do not prove runtime compatibility on other operating systems or architectures. Interactive client installation, natural-language skill selection and slash-command execution still require manual client verification. These tests verify the plugin's instructions/contracts and direct MCP process, not that client UI.

## Recorded results (2026-09-11)

- macOS arm64, Aseprite 1.3.18.2-arm64, Go 1.25.0, MCP SDK 1.4.1.
- Default plugin suite: 7/7 passed (the original 5 checks plus contract and wrapper suites).
- Contract: 50 tools, 68 documented examples, 9 negative regression cases; selected local and bundled tools/list matched the pinned snapshot.
- Real local-build workflow: 34 successful schema-checked calls. Bundled workflow: 35 after additionally reopening the GIF to assert its two frames. Both separately reproduced the transparent-quantization error; that failed operation is excluded from successful call counts.
- All five target binaries cross-built. Rebuilding the host binary produced the same SHA-256 as the bundled darwin-arm64 executable.
- Four skill entrypoints passed skill-creator quick validation. Python syntax compilation, shell syntax checks and git diff whitespace validation passed.
- Final local review checked process/config selection, snapshot provenance, path/argument handling, output schemas and example preconditions. No independent reviewer or remote CI run is claimed.
- Full MCP repository unit/PBT suites were not run: this change does not modify its source. Real execution on macOS amd64, Linux and Windows, and interactive plugin-host flows were not run in this macOS arm64 session.

This is a plugin-only synchronization. MCP source worktrees and the original plugin checkout were left clean. No develop/main merge or remote publication is part of this task; retain this branch/worktree for review.
