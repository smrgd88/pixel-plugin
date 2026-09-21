# Completed-operation warnings

After checking MCP `isError`, read the successful result's optional `warnings`
array from `structuredContent`, or from JSON TextContent when structured content
is unavailable. Each item has a stable `code` and a human-readable `message`.
Report returned warnings alongside the completed operation and its actual output
path/results. For example: “Palette optimization completed in indexed mode.
The server reported palette replacement and indexed color conversion; these may
change color or transparency representation.” Only report effects actually returned.

Warnings describe potential effects of an operation that has already completed.
They are not errors or requests for pre-execution approval. Do not retry the tool,
ask for retrospective approval, or claim cancellation/undo because a warning was
returned. Existing copy/backup guidance still applies before a requested edit;
a warning does not restore a lost original.

Use `code` for any programmatic classification, never branch on `message` text.
Display/explain the message for unknown codes too; do not drop them or reject the
successful response. Accept older responses without `warnings`. Missing warnings
are not a guarantee of safety or lossless processing. Never parse stderr for warnings.

| Tool | Returned code | Condition and potential effect |
|---|---|---|
| `quantize_palette` | `palette_quantization` | Always on success; replaces palette and may discard color information |
| `quantize_palette` | `color_mode_conversion` | `convert_to_indexed: true` (also the omitted/default value); may change color/transparency representation |
| `quantize_palette` | `layer_flattening` | `dither: true`, with either conversion setting; merges layers and may discard editable structure |
| `flatten_layers` | `layer_flattening` | Always on success; merges layers and may discard editable structure |
| `scale_sprite` | `resampling` | `bilinear` or `rotsprite`, with either scale axis different from 1; may change colors/edge patterns |

Scaling with `nearest` or an empty algorithm, and identity scaling (`scale_x: 1`,
`scale_y: 1`) omit the field. An empty algorithm is a supplied empty string, not
permission to omit a schema-required input. Warning codes are not a closed enum.
Failure responses retain MCP error handling and do not become successful warnings.

See [the generated wire contract](MCP_TOOLS.md), [creator examples](../skills/pixel-art-creator/examples.md),
[professional examples](../skills/pixel-art-professional/examples.md), and
[exporter examples](../skills/pixel-art-exporter/examples.md). The plugin test client
already preserves the whole result; user-facing reporting is the consuming skill's responsibility.
