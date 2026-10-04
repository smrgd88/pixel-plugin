# Changelog

All notable changes to the Pixel Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

These entries describe cumulative develop changes, not a newly published release.
The active bundled source is `65074051f5d3903124ead37367c7fc62d9e7e7f6`; earlier pin
entries below record their respective updates. See [current fix status](docs/BUG_STATUS.md).

### Fork publisher metadata
- Identify smrgd88 as the Codex/Claude package publisher and marketplace owner, and link to the fork repository/website.
- Retain Brandon Williams's original-author credit in both README languages and preserve the original MIT copyright/license notice.

### Codex CLI plugin installation
- Add a Codex compatibility manifest, local marketplace, and separate MCP configuration with installed-root cwd and explicit environment forwarding.
- Add real CLI cache/discovery/connection, error/warning, restart, source/cache-boundary, and optional natural-language workflow validation. Preserve Claude packaging and user configuration.
- Verify explicit same-ID installation/removal/reinstallation/upgrades and manual MCP precedence in an isolated Linux amd64 Docker user environment with real Aseprite.
- Document the tested CLI installation path and remaining app/platform limits; the bundled MCP pin and plugin version are unchanged.

### Plugin roadmap and current integration status
- Record plugin #11/#12/#13 as merged into develop and add scoped M0–M3 planning stages for Codex installation, release preparation, and native platform validation.
- Keep Codex app GUI validation on hold, distinguish MCP-owned fixes/extensions from plugin integration, and exclude the separately backed-up Godot game from the plugin backlog.
- Link both README languages to the roadmap; no runtime, binary, version, or deployment change.

### Error codes and request tracing
- Bundle merged MCP #25 at 6507405 with five rebuilt executables; retain all 56 tool schemas and success payloads.
- Preserve request IDs, typed errors and partial rollback recovery in client exceptions, skills and commands; no automatic rollback retry.
- Add error-envelope/client and real Aseprite tracing regressions. See [validation](docs/ERROR_TRACING_VALIDATION.md).

### Preview, snapshots and recorded undo
- Bundle merged MCP #21/#23/#24 at 7f439a0 with five rebuilt executables and56-tool live contract.
- Document dry_run warnings as potential apply effects, persistent saved-file snapshot recovery and opt-in history with guarded undo. Keep enable_history false by default.
- Add real preview/apply, restart/restore and history conflict regressions plus legacy client/schema checks. See [validation](docs/SAFETY_SYNC_VALIDATION.md).

### Merge status and comparison evidence
- Record plugin #9 merged into develop at `55c5697`, identical to verified candidate `8066c09`.
- Archive the additional 112-call before/after comparison with pixel images, portable evidence and standalone HTML. See [report](docs/reports/mcp22/REPORT.md).
- Track merged MCP #21 dry-run as pending plugin integration; no runtime/source pin change in this documentation update. See [next work](docs/NEXT_STEPS.md).

### MCP review repairs bundled
- Pin merged MCP #22 `bd13cdb` and refresh all five binaries, hashes and exact 50-tool reference.
- Consume indexed mask preservation, explicit zero/null threshold handling, effective AA contrast filtering, intermediate Floyd/texture density and deterministic reference palette initialization.
- Update professional/palette guidance and mark the audited issues as included in this bundle. Historical audit evidence remains available.
- Add nullable-threshold contract and real Aseprite regression gates; record numeric comparisons and verification in [the sync report](docs/REVIEW_SYNC_VALIDATION.md).

### Documentation and remaining-issue audit
- Record merged fixes for the original five bugs and distinguish remaining implementation limits from unverified platforms/client installation.
- Reproduce indexed palette-shrink transparency loss, reference edge-threshold zero defaulting, and the inactive AA threshold in the then-current `8d9bdde` bundle; document safe usage and MCP ownership without claiming runtime repairs.
- Correct the stale README source pin and consolidate the Unreleased heading. See [audit evidence](docs/BUG_AUDIT.md).

### MCP export and reference analysis repairs
- Pin MCP #20 `8d9bdde`, including #18 numbered PNG/JPG/BMP export with optional ordered files and BMP/native reference analysis.
- Rebuild five bundles and update the exact 50-tool snapshot, generated reference, exporter/professional guidance and examples.
- Verify all returned sequence paths, sizes and frame pixels; preserve legacy single-file responses and document first-frame analysis and rollback boundaries. See [validation and before/after results](docs/EXPORT_ANALYSIS_VALIDATION.md).


### MCP color-operation repairs
- Pin MCP #17 `a7ffa0f`, including #16 quantization, #13 capability and #14 file-protection changes; refresh all five bundles and exact tool contracts.
- Preserve explicit density endpoints and document pattern-dependent intermediate values, input-mode-preserving quantization and single-frame limits.
- Verify actual saved pixel colors, exported pixels, rejection/original preservation and existing warnings instead of relying only on palette size; see [color-update validation](docs/COLOR_SYNC_VALIDATION.md).


### MCP completed-operation warnings
- Pin merged MCP #11 (`6c9ac5e`), regenerate the 50-tool contract/reference and rebuild all five bundles with source/checksum metadata.
- Document optional success warnings and connect creator, professional, exporter and related commands to shared handling rules; retain legacy responses and unknown codes.
- Add schema/client and real-Aseprite warning regressions; see [warnings-update validation](docs/WARNINGS_VALIDATION.md).

### Self-review preservation follow-up
- Consume the MCP fixes for nested-group frame duplication, complete cel attributes and byte-exact preservation of user metadata during selection operations.
- Read the versioned selection-property namespace in the independent inspector and add three bundled regression scenarios (105 total).
- Retain legacy mask read compatibility without resurrecting stale state after clear.


### Follow-up restoration and verified behavior
- Restore reusable creation, animation timing, material shading, manual patterns and export guidance from the original skills while retaining corrected MCP contracts.
- Add eight executable end-to-end skill recipes, ownership/argument validation and real output checks.
- Add a 50-tool behavior sweep with selected option/offset cases; consume the separate MCP fixes for indexed pixels, dithering, selection masks, clipboard offsets, transparent quantization and frame duplication.


### Fixed
- Synchronize all four skills, five commands, examples, allowlists and exact input/output reference with MCP develop `1076166edf99f60e92bfd7fc4def261264930dcb` (50 tools).
- Correct tool aliases, one-based frames, path handling, export options and response casing; document native linked-cel construction, indexed auto shading and upstream behavior limits.
- Rebuild all five bundled targets at the same pinned commit; add portable PIXEL_MCP_BINARY selection and preserve config environment overrides.

### Added
- Reproducible committed-source host/release builds, source/schema snapshots and binary SHA-256 provenance.
- Live MCP contract comparison, 68 documented payload checks, negative regressions and wrapper/config tests in CI.
- Isolated real-Aseprite smoke tests for native links, indexed shading, PNG/GIF/sheet exports and opaque quantization. Transparent quantization and selection/pixel/dithering regressions are covered by the follow-up repaired MCP build.

## [0.5.0] - 2025-10-18

### Changed
- Updated pixel-mcp dependency to v0.5.0
- Fixed pixel-art-professional skill tool names:
  - `mcp__aseprite__quantize_colors` → `mcp__aseprite__quantize_palette`
  - `mcp__aseprite__apply_dithering` → `mcp__aseprite__draw_with_dither`

### Added
- New MCP tools from pixel-mcp v0.4.0+:
  - `quantize_palette` - Reduce sprite colors using median_cut, k-means, or octree algorithms with optional dithering
  - `apply_auto_shading` - Automatically add geometry-based shading to sprites
- New MCP tool from pixel-mcp v0.5.0:
  - `flatten_layers` - Flatten all layers into a single layer

## [0.3.0] - 2025-10-17

### Changed
- Updated pixel-mcp dependency to v0.3.0
- Refreshed all platform binaries (macOS Intel/ARM, Linux x86_64/ARM64, Windows x86_64)

## [0.1.0] - 2025-01-16

### Added

#### Core Skills
- **pixel-art-creator** - Canvas creation, layers, and basic drawing
- **pixel-art-animator** - Frame management and animation
- **pixel-art-professional** - Dithering, palettes, shading, and antialiasing
- **pixel-art-exporter** - PNG, GIF, spritesheet, and JSON export

#### Slash Commands
- `/pixel-new` - Quick sprite creation with size and palette presets
- `/pixel-palette` - Palette management (set, optimize, show, export)
- `/pixel-export` - Multi-format export with options
- `/pixel-setup` - One-time plugin configuration
- `/pixel-help` - Help system

#### Features
- Natural language sprite creation and editing
- 12+ retro palette presets (NES, Game Boy, C64, PICO-8, etc.)
- Dithering support (Floyd-Steinberg, Bayer matrices)
- Animation with frame management, tags, and timing
- Spritesheet layouts (horizontal, vertical, grid, packed)
- JSON metadata export for Unity, Godot, Phaser, TexturePacker
- Pixel-perfect scaling (1x, 2x, 4x, 8x)
- Cross-platform support (macOS, Linux, Windows)

#### Infrastructure
- MCP server integration with pixel-mcp
- Pre-compiled binaries for all platforms
- Automated test suite with validation scripts
- Testing checklist with 45+ tests
- Known issues documentation

[Unreleased]: https://github.com/willibrandon/pixel-plugin/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/willibrandon/pixel-plugin/compare/v0.3.0...v0.5.0
[0.3.0]: https://github.com/willibrandon/pixel-plugin/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/willibrandon/pixel-plugin/releases/tag/v0.1.0
