#!/usr/bin/env python3
"""Check sprite exports against authored geometry, frame timing and palette pixels."""
import argparse
import json
from pathlib import Path
from PIL import Image
from frames import make_animation


def verify(output):
    results = []
    for mode in ("whole", "leaf", "roll"):
        animation = make_animation(mode)
        size, frames = animation["size"], animation["frames"]
        with Image.open(output / f"{mode}-sheet.png") as image:
            sheet = image.convert("RGBA")
        if sheet.size != (size * len(frames), size):
            raise ValueError(f"{mode}: unexpected sheet dimensions {sheet.size}")
        for frame, layers in enumerate(frames):
            expected = {}
            for layer in layers.values():
                expected.update(layer)
            actual = {(x, y): sheet.getpixel((frame * size + x, y))
                      for y in range(size) for x in range(size)
                      if sheet.getpixel((frame * size + x, y))[3]}
            wanted = {xy: tuple(bytes.fromhex(color[1:])) + (255,)
                      for xy, color in expected.items()}
            if actual != wanted:
                raise ValueError(f"{mode}: exported frame {frame + 1} pixels differ")
        metadata = json.loads((output / f"{mode}-sheet.json").read_text())
        items = metadata["frames"]
        items = list(items.values()) if isinstance(items, dict) else items
        if len(items) != len(frames) or any(f["duration"] != animation["duration_ms"] for f in items):
            raise ValueError(f"{mode}: incorrect frame count/durations")
        with Image.open(output / f"{mode}.gif") as gif:
            duration, unique = 0, set()
            for frame in range(gif.n_frames):
                gif.seek(frame)
                duration += gif.info.get("duration", 0)
                unique.add(gif.convert("RGBA").tobytes())
            if gif.size != (size, size) or duration != len(frames) * animation["duration_ms"]:
                raise ValueError(f"{mode}: GIF dimensions or duration differ")
            if gif.info.get("loop") != 0 or len(unique) < 4:
                raise ValueError(f"{mode}: GIF is not a varied looping animation")
        with Image.open(output / f"{mode}.png") as image:
            if image.convert("RGBA").tobytes() != sheet.crop((0, 0, size, size)).tobytes():
                raise ValueError(f"{mode}: still image differs from the first frame")
        if mode == "leaf":
            if any(frame["Body"] != frames[0]["Body"] for frame in frames):
                raise ValueError("Leaf-only animation changes the body layer")
            fixed = sheet.crop((0, 17, 32, 32)).tobytes()
            if any(sheet.crop((i * 32, 17, (i + 1) * 32, 32)).tobytes() != fixed
                   for i in range(len(frames))):
                raise ValueError("Leaf-only export changes the lower body")
        results.append({"animation": mode, "size": size, "frames": len(frames),
                        "duration_ms": duration, "unique_gif_frames": len(unique),
                        "pixels_verified": True})
    rotation = json.loads((output / "sprite-data.json").read_text())
    expected = make_animation("roll")
    if rotation != {"frameSize": 40, "frames": 32, "feet": expected["feet"],
                    "radius": 12, "sourceBodySize": 32}:
        raise ValueError("Game rotation metadata differs from sprite geometry")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=Path(__file__).parent / "assets")
    args = parser.parse_args()
    print(json.dumps(verify(args.output), ensure_ascii=False, indent=2))
