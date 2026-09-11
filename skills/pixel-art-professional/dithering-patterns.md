# Dithering patterns

`draw_with_dither` fills a rectangle using two colors. Supply `sprite_path`, `layer_name`, one-based `frame_number`, `region: {x,y,width,height}`, `color1`, `color2`, and `pattern`. See [examples](examples.md) and the [contract](../../docs/MCP_TOOLS.md).

Supported patterns: `bayer_2x2`, `bayer_4x4`, `bayer_8x8`, `checkerboard`, `floyd_steinberg`, `grass`, `water`, `stone`, `cloud`, `brick`, `dots`, `diagonal`, `cross`, `noise`, `horizontal_lines`, `vertical_lines`.

Use Bayer/checkerboard for ordered transitions, material patterns for textures, and Floyd–Steinberg for error diffusion. `density` is the color ratio in 0–1; omitted or zero currently selects the handler's 0.5 default. For a uniform single color, use `draw_rectangle` through the creator skill.

To reduce an existing image to a palette with dithering, use `quantize_palette` and `dither: true` instead. Atkinson and free-form custom patterns are not exposed by these tools.
