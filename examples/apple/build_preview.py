#!/usr/bin/env python3
"""Build offline previews from exported assets; no MCP or Aseprite is needed."""
import argparse
import base64
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def data_url(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def build(output):
    assets = {"roll": data_url(output / "roll-sheet.png", "image/png"),
              "idle": data_url(output / "leaf-sheet.png", "image/png"),
              "feet": json.loads((output / "sprite-data.json").read_text())["feet"]}
    demo = HERE / "demo"
    page = (demo / "template.html").read_text()
    replacements = {"ROLL_GIF": data_url(output / "roll.gif", "image/gif"),
                    "ASSET_DATA": json.dumps(assets),
                    "ENGINE": (demo / "engine.js").read_text(),
                    "GAME": (demo / "game.js").read_text()}
    for marker, value in replacements.items():
        page = page.replace(marker, value)
    (output / "game.html").write_text(page)
    cards = []
    for mode, title, size in (("whole", "전체 흔들림", 32),
                              ("leaf", "잎만 흔들림", 32), ("roll", "구르기", 40)):
        uri = data_url(output / f"{mode}.gif", "image/gif")
        cards.append(f'<article><h2>{title}</h2><img width="320" height="320" '
                     f'alt="{title}" src="{uri}"><p>원본 {size}×{size}</p>'
                     f'<img width="{size}" height="{size}" alt="원본 크기" src="{uri}"></article>')
    validation = html.escape((output / "validation.json").read_text())
    gallery = '''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Apple MCP example</title>
<style>body{background:#19252c;color:#f6efe2;font:16px/1.6 system-ui;max-width:1160px;margin:32px auto;padding:20px}
.grid{display:flex;gap:20px;flex-wrap:wrap}article{padding:16px;background:#29383f;border-radius:12px}
h2{font-size:19px}img{display:block;image-rendering:pixelated;background:#f6edd9}a{color:#b7ddbf}
pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer}</style>
<h1>사과 MCP 예제</h1><p>전체 흔들림 · 잎만 흔들림 · 한 바퀴 회전</p>
<p><a href="game.html">브라우저 게임 데모 열기</a> · Godot 프로젝트는 포함하지 않습니다.</p>
<div class="grid">'''
    gallery += "".join(cards)
    gallery += ('</div><p>구르기는 32px 그림을 회전 여백이 있는 40px 캔버스에 담았습니다. '
                '게임 데모의 높이 보정은 잎·가지를 포함해 약간의 덜컥거림이 남아 있습니다.</p>'
                '<details><summary>생성·검증 기록</summary><pre>' + validation + '</pre></details></html>')
    (output / "index.html").write_text(gallery)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?", default=HERE / "assets")
    build(parser.parse_args().output.resolve())
