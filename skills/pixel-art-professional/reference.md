# Professional tools reference

Read the [contract](../../docs/MCP_TOOLS.md) for all field names, nested regions and responses; [examples](examples.md) cover each tool.

- Quantization algorithms: `median_cut`, `kmeans`, `octree`. Target size is 2–256. `dither` controls Floyd–Steinberg color remapping. Omit optional preservation/conversion booleans for their true defaults, or supply explicit false to keep RGB. This modifies sprite pixels and may change its color mode.
- `set_palette` and palette edit tools change palette entries; they are not synonyms for quantization. `sort_palette` accepts `hue`, `saturation`, `brightness`, `luminance` and an explicit `ascending` boolean. Inspect indexed artwork after palette edits.
- `apply_shading` uses a supplied darkest-to-lightest ramp and a rectangular region, with `pillow`, `smooth`, `hard` styles. `apply_auto_shading` generates shading with `cell`, `smooth`, `soft` styles and explicit `hue_shift`.
- Both shading tools accept light directions `top_left`, `top`, `top_right`, `left`, `right`, `bottom_left`, `bottom`, `bottom_right` and intensity 0–1.
- Legacy response spelling is significant: `set_palette`, `set_palette_color`, `sort_palette`, `draw_with_dither`, and `apply_shading` return `Success`. Automatic shading and quantization return lowercase `success` plus detailed results.
- `analyze_reference` returns palette entries and brightness/edge/composition analysis, not a sprite. Its schema advertises more extensions than its raster decoder implements; export an Aseprite reference to PNG first.
- Antialiasing suggestions are not automatically applied unless `auto_apply` is true. Inspect `applied`, and read the actual pixel result rather than assuming every detected edge changes.

Known upstream limit: quantization with transparent pixels and `preserve_transparency: true` can fail on `#00000000` color parsing at the pinned revision. Preserve the original and report that error; do not retry with transparency disabled unless losing transparency is explicitly wanted. The live smoke test verifies opaque-image quantization separately. See [known issues](../../docs/KNOWN_ISSUES.md).
