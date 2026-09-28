# Repaired palette, threshold and density controls

The bundled source includes merged MCP #22. Existing JSON numeric inputs and all
output fields/warnings remain compatible; [tools/list](MCP_TOOLS.md) is authoritative.

## Palette editing and extraction

set_palette and add_palette_color preserve the indexed sprite's transparent index
across resize. Removing unused trailing entries no longer makes an existing opaque
color transparent. This does not remap ordinary in-use indices deleted by a palette
replacement, preserve arbitrary recoloring, or remove the need for a native copy.
Inspect affected pixels rather than trusting Success alone.

Reference palette extraction now uses deterministic farthest-point seeds and performs
the first mean update before deciding convergence. The existing requested entry count
is retained: fewer unique sampled colors can still produce duplicate/zero-usage entries.
When reporting color usage, combine duplicate colors or ignore zero-usage entries; do
not equate entry count with unique image colors. Subsampling/approximate clustering
is not a guarantee that every rare color in a large image survives.

## Reference and AA thresholds

- analyze_reference edge_threshold: omitted/null → 30; explicit 0 is a real Sobel
  threshold 0. Valid integer range is 0–255.
- suggest_antialiasing threshold: omitted/null → 128. Existing diagonal candidates
  are retained only when their maximum premultiplied RGBA 8-bit channel difference
  is **greater than** threshold. Empty pixels are transparent; hidden RGB does not
  contribute contrast. This filters candidates, not the entire detection algorithm.
- For an alpha64 white stair edge against transparency, 0/1/63 retains 5 suggestions
  in the recorded fixture; 64/128/255 retains none. Fully opaque/transparent contrast
  is 255, so different lower thresholds may legitimately yield identical results.
- Start with auto_apply=false when reviewing suggestions. No suggestions is a valid
  result, not a reason to retry automatically or claim an edit was applied.

## Dithering

Omitted/null density remains .5, 0 fills color1 and 1 fills color2. Bayer behavior
is unchanged. Floyd interior values bias the horizontal gradient mean; .5 retains
the legacy gradient for width > 1. A one-column region now uses the requested
mixture with one-dimensional error carry instead of the old all-color1 behavior.

Binary textures rank positions within their original 0/1 groups. This gives finer
intermediate coverage while retaining the existing .5 pattern. Density is not a
promise of exact global color2 proportion, especially for dots or clipped pattern tiles.

| 8×8, distinct opaque red/blue | color2 at .25 | at .5 | at .75 |
|---|---:|---:|---:|
| Floyd | 16 | 32 | 49 |
| Checkerboard | 16 | 32 | 48 |
| Dots | 28 | 56 | 60 |
| Bayer 4×4 | 16 | 32 | 48 |

These are measured fixture values, not universal ratios. Image size, palette mapping,
identical colors and alpha/layer compositing affect visible color counts. Explain this
when a user asks for a precise percentage; do not invent an exact-ratio mode.
