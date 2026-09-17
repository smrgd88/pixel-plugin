# Professional tools reference

Read the [contract](../../docs/MCP_TOOLS.md) for all field names, nested regions and responses; [examples](examples.md) cover each tool.

- Quantization algorithms: `median_cut`, `kmeans`, `octree`. Target size is 2–256. `dither` controls Floyd–Steinberg color remapping. Omit optional preservation/conversion booleans for their true defaults, or supply explicit false to keep RGB. This modifies sprite pixels and may change its color mode. Dithered quantization currently flattens/replaces content; use a native copy when preserving layers/frames matters, and re-read get_sprite_info afterwards before targeting a layer.
- `set_palette` and palette edit tools change palette entries; they are not synonyms for quantization. `sort_palette` accepts `hue`, `saturation`, `brightness`, `luminance` and an explicit `ascending` boolean. Inspect indexed artwork after palette edits.
- `apply_shading` uses a supplied darkest-to-lightest ramp and a rectangular region, with `pillow`, `smooth`, `hard` styles. `apply_auto_shading` generates shading with `cell`, `smooth`, `soft` styles and explicit `hue_shift`.
- Both shading tools accept light directions `top_left`, `top`, `top_right`, `left`, `right`, `bottom_left`, `bottom`, `bottom_right` and intensity 0–1.
- Legacy response spelling is significant: `set_palette`, `set_palette_color`, `sort_palette`, `draw_with_dither`, and `apply_shading` return `Success`. Automatic shading and quantization return lowercase `success` plus detailed results.
- `analyze_reference` returns palette entries and brightness/edge/composition analysis, not a sprite. Its schema advertises more extensions than its raster decoder implements; export an Aseprite reference to PNG first.
- Antialiasing suggestions are not automatically applied unless `auto_apply` is true. Inspect `applied`, and read the actual pixel result rather than assuming every detected edge changes.


## Choose a treatment for the material

Start with the intended light direction and a readable silhouette. Choose flat color for a tiny icon, two or three distinct tones for a bold character, or more gradual ramps for a larger surface. Automatic shading is a draft to inspect; manual pixel clusters give more control over the shape.

| Material | Starting ramp (dark → light) | Placement |
|---|---|---|
| Steel | #1A1A24, #3A3A4A, #6A6A7A, #AAAABB, #FFFFFF | Narrow, high-contrast reflection bands and a few sharp glints |
| Red fabric | #5A1A1A, #8A2A2A, #C43A3A, #E66A6A, #FF9A9A | Broader midtones and restrained highlights following folds |
| Warm skin | #3A2419, #5C3A28, #8D5A3E, #B8825C, #E6B896 | Broad form shadow with sparse highlights; adapt to character and lighting |

These are example palettes, not physically correct or universally appropriate colors. Cool shadows and warm highlights are useful choices under some lighting; the light source and material can reverse that relationship. Hue-wheel plus/minus signs do not always mean warmer/cooler. Black and white are valid accents when the design calls for them.

A practical refinement pass is: organize the palette → decide light direction → place major shadows/highlights → refine contact shadows → use limited dithering for selected transitions → add selective antialiasing. Preview at native size between stages and retain the original when experimenting.

## Diagnose common visual problems

- **Pillow shading:** highlights centered everywhere can obscure directional form. Use one coherent light source unless a soft frontal-light effect is intended. The supported `pillow` option is not a default quality recommendation.
- **Unclear materials:** use tighter highlights and higher contrast on metal; broader transitions on fabric. Avoid giving every surface the same ramp and highlight width.
- **Banding/noisy gradients:** adjust the ramp or place a small dither transition; do not cover the whole sprite in texture simply because a pattern tool is available.
- **Over-antialiasing:** try a single intermediate pixel at selected stair steps. Preserve intentional sharp edges and small silhouettes. Automatic AA only detects certain jagged transparent-edge patterns; `threshold` currently does not tune the underlying detector.
- **Floating objects:** a few carefully placed darker contact pixels under a chin, foot or overlapping part can help. There is no dedicated ambient-occlusion tool; use explicit pixels.

For manual AA, sample the actual edge/background colors and place intermediate colors only where useful. `suggest_antialiasing` is a preview/apply option, not a substitute for a visual quality check. See [material and manual-pattern recipes](examples.md#complete-refinement-recipes).
