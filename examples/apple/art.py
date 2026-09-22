"""Pixel geometry for the selected apple. No file or MCP operations on import."""

import math
from PIL import Image, ImageDraw

def bezier(start, segments):
    points = [start]
    a = start
    for b, c, d in segments:
        for i in range(1, 33):
            t = i / 32
            u = 1 - t
            points.append((u ** 3 * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t ** 3 * d[0], u ** 3 * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t ** 3 * d[1]))
        a = d
    return points

def mask(points, size):
    im = Image.new('1', (size, size))
    ImageDraw.Draw(im).polygon([(x * size / 32, y * size / 32) for x, y in points], fill=1)
    return {(x, y) for y in range(size) for x in range(size) if im.getpixel((x, y))}
pal = ['#63313E', '#C52F48', '#F04C55', '#FF7970', '#FFE9B9']
body_points = bezier((16, 8), [((10, 8), (5, 11), (4, 17)), ((3, 23), (8, 28), (14, 29)), ((20, 30), (26, 26), (28, 22)), ((30, 17), (27, 11), (23, 9)), ((21, 8), (18, 8), (16, 8))])
body = mask(body_points, 32)
base = {}
for x, y in body:
    edge = any(((x + dx, y + dy) not in body for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]))
    bright = ((x - 11) / 10) ** 2 + ((y - 14) / 11) ** 2 < 1
    shade = x > 23 - (y - 15) * 0.18 or y > 26 + 0.12 * (x - 16)
    base[x, y] = pal[0] if edge else pal[1] if shade else pal[3] if bright else pal[2]
for xy in mask(bezier((8, 14), [((8, 12), (10, 11), (11, 11)), ((12, 11), (11, 13), (10, 14)), ((9, 15), (8, 16), (8, 14))]), 32):
    if xy in base:
        base[xy] = pal[4]
stem_points = [(16, 9), (16, 8), (16, 7), (17, 6), (17, 5), (17, 4)]
for xy in stem_points:
    base[xy] = '#75432E'
base[18, 6] = '#75432E'
base[19, 6] = '#31553B'
for xy in [(15, 10), (16, 10), (17, 10)]:
    if xy in body:
        base[xy] = pal[3]
leaf_points = bezier((19, 6), [((24, 4), (29, 8), (28, 15)), ((24, 15), (19, 11), (19, 6))])
leafmask = mask(leaf_points, 32)
leaf = {}
for x, y in leafmask:
    edge = any(((x + dx, y + dy) not in leafmask for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]))
    leaf[x, y] = '#31553B' if edge else '#83B952' if x > 19 + (y - 6) * 0.9 else '#529146'
for xy in [(20, 7), (21, 8), (22, 9), (23, 10), (24, 11), (25, 12), (26, 13)]:
    if xy in leaf:
        leaf[xy] = '#C4DB7B'

def vector_rotate(data, points, angle, pivot=(16, 29), dx=0, outline='#63313E'):
    co, si = (math.cos(angle), math.sin(angle))
    px, py = pivot
    rotated = [(co * (x - px) - si * (y - py) + px + dx, si * (x - px) + co * (y - py) + py) for x, y in points]
    desired = mask(rotated, 32)
    out = {}
    for x, y in desired:
        X = x - dx - px
        Y = y - py
        source = (round(co * X + si * Y + px), round(-si * X + co * Y + py))
        edge = any(((x + a, y + b) not in desired for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)]))
        out[x, y] = outline if edge else data.get(source, outline)
    return out

def line(data, points, col):
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(n + 1):
            data[round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n)] = col

def groups(data):
    todo = set(data)
    out = []
    while todo:
        seed = min(todo)
        todo.remove(seed)
        found = {seed}
        stack = [seed]
        while stack:
            x, y = stack.pop()
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                q = (x + dx, y + dy)
                if q in todo:
                    todo.remove(q)
                    found.add(q)
                    stack.append(q)
        out.append(found)
    return sorted(out, key=lambda g: (-len(g), min(g)))


def raster(points):
    im = Image.new('1', (40, 40))
    ImageDraw.Draw(im).polygon(points, fill=1)
    return {(x, y) for y in range(40) for x in range(40) if im.getpixel((x, y))}

def render(data, points, a, outline):
    co, si = (math.cos(a), math.sin(a))
    transform = lambda q: (co * (q[0] - 16) - si * (q[1] - 18) + 20, si * (q[0] - 16) + co * (q[1] - 18) + 20)
    shape = raster([transform(q) for q in points])
    out = {}
    for x, y in shape:
        X = x - 20
        Y = y - 20
        src = (round(co * X + si * Y + 16), round(-si * X + co * Y + 18))
        edge = any(((x + dx, y + dy) not in shape for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]))
        out[x, y] = outline if edge else data.get(src, outline)
    return (out, transform)
