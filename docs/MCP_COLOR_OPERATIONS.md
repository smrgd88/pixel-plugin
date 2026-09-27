# Quantization and density contracts

The pinned server includes MCP #16 and #17. Use the [generated schema](MCP_TOOLS.md)
and [completed-operation warning rules](MCP_WARNINGS.md) together with these constraints.

Quantization supports **single-frame raster sprites**. Check frame count first;
animation and tilemap inputs are rejected before modifications. Do not silently
remove frames or flatten a tilemap to make an unsupported user request run.

`quantize_palette` remaps actual pixels in every dither/conversion combination.
`convert_to_indexed: false` preserves the input RGB, grayscale or indexed mode;
it does not mean “force RGB” or “only edit the palette”. Non-dithered remapping
preserves editable layers; dithering flattens them. Re-read layer names afterwards.

`target_colors` (2–256) bounds palette entries, not colors introduced by compositing
layers. Indexed images reserve a transparent mask and support at most 255 opaque
entries. Fully transparent pixels stay transparent with either preserve_transparency
setting; true reserves an entry in the quantized palette. Partial alpha is not
preserved as a continuous range by quantization. Keep a native copy when it matters.

Verify actual affected pixels with get_pixels (including pagination) and, when
appropriate, export/reopen the image. A two-entry palette is not proof that both
colors survived. Compare intended features/colors with the source and report an
unexpected collapse instead of calling it a successful visual result. Do not demand
exactly target_colors unique pixels: fewer source colors, transparency and layer
blending make that inference invalid.

`draw_with_dither` accepts omitted/null density as 0.5, 0 fills color1, and 1 fills
color2. Intermediate ordered/texture thresholds are not exact pixel ratios. For
Floyd–Steinberg, intermediate density retains the existing horizontal gradient;
it does not adjust that gradient's density. These fill operations differ from
quantizing an existing image.

The source pin also adds capability checks (Aseprite 1.3.17.2+ / API 39+) and
single-file staging/locking. A capability failure happens before editing. A failed
protected write retains its original, but successful warnings still describe a
completed edit. This is not an undo feature, a backup, protection from every external
GUI writer, or atomic publication of multiple output files. Continue using copies
where the workflow requires original preservation.
