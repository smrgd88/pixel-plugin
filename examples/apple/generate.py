#!/usr/bin/env python3
"""Recreate the apple samples through the plugin's actual stdio MCP server."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from frames import make_animation
from verify import verify
from build_preview import build

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aseprite", type=Path, required=True, help="Path to the Aseprite executable")
    parser.add_argument("--binary", type=Path, help="Optional MCP executable; defaults to bin/pixel-mcp")
    parser.add_argument("--output", type=Path, default=HERE / "generated")
    args = parser.parse_args()
    aseprite = args.aseprite.expanduser().resolve(strict=True)
    binary = (args.binary or ROOT / "bin/pixel-mcp").expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("apple_mcp_client", ROOT / "bin/mcp-client.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    logs = []
    with tempfile.TemporaryDirectory(prefix="pixel-apple-") as temp:
        config = Path(temp) / "config.json"
        config.write_text(json.dumps({"aseprite_path": str(aseprite), "temp_dir": temp,
                                      "log_level": "error"}))
        # An explicit executable wins over a pre-existing wrapper override.
        env = dict(os.environ, PIXEL_MCP_CONFIG=str(config))
        if args.binary:
            env.pop("PIXEL_MCP_BINARY", None)

        def normalize(value):
            if isinstance(value, dict):
                return {key: normalize(item) for key, item in value.items()}
            if isinstance(value, list):
                return [normalize(item) for item in value]
            if isinstance(value, str):
                return value.replace(str(output), "${OUTPUT}").replace(temp, "${TEMP}")
            return value

        client = module.Client([str(binary)], env)
        try:
            for mode in ("whole", "leaf", "roll"):
                animation = make_animation(mode)
                frames, size = animation["frames"], animation["size"]

                def call(name, **arguments):
                    try:
                        result = client.call(name, arguments)
                    except Exception as error:
                        logs.append(normalize({"animation": mode, "name": name,
                                               "arguments": arguments, "error": str(error)}))
                        raise
                    logs.append(normalize({"animation": mode, "name": name,
                                           "arguments": arguments, "result": result}))
                    return result

                path = call("create_canvas", width=size, height=size, color_mode="rgb")["file_path"]
                # Allocate frames before drawing so add_frame cannot copy existing cels.
                for _ in frames[1:]:
                    call("add_frame", sprite_path=path, duration_ms=animation["duration_ms"])
                for name in frames[0]:
                    call("add_layer", sprite_path=path, layer_name=name)
                for i, layers in enumerate(frames, 1):
                    for name, pixels in layers.items():
                        if mode == "leaf" and name == "Body" and i > 1:
                            call("link_cel", sprite_path=path, layer_name=name,
                                 source_frame=1, target_frame=i)
                        else:
                            call("draw_pixels", sprite_path=path, layer_name=name, frame_number=i,
                                 pixels=[{"x": x, "y": y, "color": color}
                                         for (x, y), color in sorted(pixels.items())])
                call("set_frame_duration", sprite_path=path, frame_number=1,
                     duration_ms=animation["duration_ms"])
                call("create_tag", sprite_path=path, tag_name=mode, from_frame=1,
                     to_frame=len(frames), direction="forward")
                native = output / f"{mode}.aseprite"
                call("save_as", sprite_path=path, output_path=str(native))
                for extension, frame in (("png", 1), ("gif", 0)):
                    call("export_sprite", sprite_path=str(native),
                         output_path=str(output / f"{mode}.{extension}"),
                         format=extension, frame_number=frame)
                sheet = call("export_spritesheet", sprite_path=str(native),
                             output_path=str(output / f"{mode}-sheet.png"),
                             layout="horizontal", padding=0, include_json=True)
                metadata_path = Path(sheet["metadata_path"])
                metadata = json.loads(metadata_path.read_text())
                # Portable metadata: Godot/importers resolve the adjacent image filename.
                metadata["meta"]["image"] = f"{mode}-sheet.png"
                (output / f"{mode}-sheet.json").write_text(json.dumps(metadata, indent=2) + "\n")
                if mode == "roll":
                    (output / "sprite-data.json").write_text(json.dumps({
                        "frameSize": 40, "frames": 32, "feet": animation["feet"],
                        "radius": 12, "sourceBodySize": 32}, indent=2) + "\n")
                print(f"Generated {mode}: {len(frames)} frames at {size}x{size}", flush=True)
        finally:
            client.close()
            (output / "calls.json").write_text(json.dumps(logs, indent=2) + "\n")
    report = {"animations": verify(output), "mcp_calls": len(logs),
              "mcp_version": subprocess.check_output([str(binary), "--version"],
                                                      env=env, text=True).strip()}
    (output / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    build(output)
    print(f"Verified all exports. Open {output / 'index.html'}")


if __name__ == "__main__":
    main()
