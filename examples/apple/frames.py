"""Build deterministic animation frames from the shared apple geometry."""
import math
from art import base, body_points, leaf, leaf_points, stem_points, vector_rotate, render, line, groups


def connect(body_layer, leaf_layer=None):
    """Bridge only one-pixel sampling gaps; reject larger geometry errors."""
    target = leaf_layer if leaf_layer is not None else body_layer
    merged = body_layer | (leaf_layer or {})
    components = groups(merged)
    while len(components) > 1:
        a, b = min(
            ((a, b) for a in sorted(components[0]) for b in sorted(components[1])),
            key=lambda pair: (max(abs(pair[0][0] - pair[1][0]),
                                  abs(pair[0][1] - pair[1][1])), pair),
        )
        if max(abs(a[0] - b[0]), abs(a[1] - b[1])) > 2:
            raise ValueError("Animation contains a disconnected component")
        line(target, [a, b], merged[b])
        merged = body_layer | (leaf_layer or {})
        components = groups(merged)
    return merged


def make_animation(mode):
    count = 32 if mode == "roll" else 24
    size = 40 if mode == "roll" else 32
    frames, feet = [], []
    for frame in range(count):
        phase = 2 * math.pi * frame / count
        if mode == "roll":
            body_layer, transform = render(base, body_points, phase, "#63313E")
            leaf_layer, _ = render(leaf, leaf_points, phase, "#31553B")
            line(body_layer, [tuple(round(v) for v in transform(p))
                             for p in stem_points + [(18, 6), (19, 6)]], "#75432E")
            merged = body_layer | leaf_layer
            connect(merged)
            # Padding, not resampling: the original 32px artwork rotates in a 40px canvas.
            if not all(0 < x < 39 and 0 < y < 39 for x, y in merged):
                raise ValueError("Rolling sprite clips its padding")
            layers = {"Apple": merged}
        elif mode == "whole":
            angle, dx = .065 * math.sin(phase), round(.7 * math.sin(phase))
            body_layer = vector_rotate(base, body_points, angle, dx=dx)
            leaf_layer = vector_rotate(leaf, leaf_points, angle, dx=dx, outline="#31553B")
            co, si = math.cos(angle), math.sin(angle)
            points = [(round(co * (x - 16) - si * (y - 29) + 16 + dx),
                       round(si * (x - 16) + co * (y - 29) + 29))
                      for x, y in stem_points + [(18, 6), (19, 6)]]
            line(body_layer, points, "#75432E")
            # Repair the moving body only; the leaf keeps its authored palette.
            merged = body_layer | leaf_layer
            repaired = dict(merged)
            connect(repaired)
            body_layer.update({p: c for p, c in repaired.items() if p not in merged})
            layers = {"Body": body_layer, "Leaf": leaf_layer}
            merged = body_layer | leaf_layer
        elif mode == "leaf":
            body_layer = dict(base)
            leaf_layer = vector_rotate(leaf, leaf_points, .17 * math.sin(phase),
                                       pivot=(19, 6), outline="#31553B")
            leaf_layer[19, 6] = "#31553B"
            merged = connect(body_layer, leaf_layer)
            if body_layer != base:
                raise ValueError("Leaf-only animation modified the body")
            layers = {"Body": body_layer, "Leaf": leaf_layer}
        else:
            raise ValueError(f"Unknown animation: {mode}")
        if not all(0 <= x < size and 0 <= y < size for x, y in merged):
            raise ValueError(f"{mode} frame {frame} is outside its canvas")
        if len(groups(merged)) != 1:
            raise ValueError(f"{mode} frame {frame} is disconnected")
        frames.append(layers)
        feet.append(max(y for x, y in merged))
    return {"size": size, "duration_ms": 70 if mode == "roll" else 100,
            "frames": frames, "feet": feet}
