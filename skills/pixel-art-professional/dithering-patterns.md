# Dithering patterns

`draw_with_dither` fills a rectangle using two colors. Supply `sprite_path`, `layer_name`, one-based `frame_number`, `region: {x,y,width,height}`, `color1`, `color2`, and `pattern`. See [examples](examples.md) and the [contract](../../docs/MCP_TOOLS.md).

Supported patterns: `bayer_2x2`, `bayer_4x4`, `bayer_8x8`, `checkerboard`, `floyd_steinberg`, `grass`, `water`, `stone`, `cloud`, `brick`, `dots`, `diagonal`, `cross`, `noise`, `horizontal_lines`, `vertical_lines`.

Use Bayer/checkerboard for ordered transitions, material patterns for textures, and Floyd–Steinberg for error diffusion. `density` is the color ratio in 0–1; omitted or zero currently selects the handler's 0.5 default. For a uniform single color, use `draw_rectangle` through the creator skill.

To reduce an existing image to a palette with dithering, use `quantize_palette` and `dither: true` instead. Atkinson and free-form custom patterns are not exposed by these tools.

## Manual pattern library

These small design patterns are independent of an automatic dithering algorithm. Tile them with `draw_pixels`, mapping A/B/C to explicit hex colors on a known layer and frame. Use this route for a custom three-color weave or precise placement around a silhouette.

```text
Checker (50% A / 50% B)    Sparse accent (75% A / 25% B)
ABAB                     BABA
BABA                     AAAA
ABAB                     BABA
BABA                     AAAA

Three-color weave        Diagonal hatch
ABCA                     BAAA
BCAB                     ABAA
CABC                     AABA
ABCA                     AAAB
```

The three-color tile deliberately has unequal counts; do not describe it as a 50/50 mix. Tile boundaries and phase affect the appearance. Rotating or swapping colors gives variants, but inspect the seam where the pattern repeats.

Use Bayer transitions for ordered gradients; reserve coarse checker/diagonal marks for intentional texture. Stone may benefit from irregular clusters, cloth from restrained woven or directional patterns, and brushed metal from subtle directional marks. These are artistic starting points, not hard material-to-pattern rules.

See the [manual checker recipe](examples.md#complete-refinement-recipes), whose two-color counts and output pixels are checked by the live recipe test.
