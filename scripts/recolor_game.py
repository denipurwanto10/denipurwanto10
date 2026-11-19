#!/usr/bin/env python3
"""Recolor the space shooter GIF: green blocks -> yellow, blue ship -> red.

Usage: python scripts/recolor_game.py game.gif
"""
import sys
import numpy as np
from PIL import Image, ImageSequence

PATH = sys.argv[1] if len(sys.argv) > 1 else "game.gif"

YELLOW_HUE = 48.0   # degrees
RED_HUE = 0.0


def recolor(rgb):
    a = rgb.astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=-1)
    mn = a.min(axis=-1)
    d = mx - mn
    safe = np.where(d == 0, 1, d)

    h = np.zeros_like(mx)
    h = np.where(mx == r, ((g - b) / safe) % 6, h)
    h = np.where(mx == g, (b - r) / safe + 2, h)
    h = np.where(mx == b, (r - g) / safe + 4, h)
    h = np.where(d == 0, 0, h) * 60.0
    s = np.where(mx == 0, 0, d / np.where(mx == 0, 1, mx))
    v = mx

    colored = (s > 0.35) & (v > 0.2)
    green = colored & (h >= 80) & (h <= 170)
    blue = colored & (h >= 190) & (h <= 260)

    h2 = h.copy()
    h2[green] = YELLOW_HUE
    h2[blue] = RED_HUE
    changed = green | blue

    # HSV -> RGB
    c = v * s
    hp = (h2 / 60.0) % 6
    x = c * (1 - np.abs(hp % 2 - 1))
    m = v - c
    z = np.zeros_like(c)
    conds = [hp < 1, hp < 2, hp < 3, hp < 4, hp < 5, hp >= 5]
    rr = np.select(conds, [c, x, z, z, x, c])
    gg = np.select(conds, [x, c, c, x, z, z])
    bb = np.select(conds, [z, z, x, c, c, x])
    out = np.stack([rr + m, gg + m, bb + m], axis=-1)
    out = np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)

    result = rgb.copy()
    result[changed] = out[changed]
    return result, int(green.sum()), int(blue.sum())


src = Image.open(PATH)
loop = src.info.get("loop", 0)
frames, durations = [], []
total_g = total_b = 0
for frame in ImageSequence.Iterator(src):
    durations.append(frame.info.get("duration", 40))
    rgb = np.array(frame.convert("RGB"))
    new, g, b = recolor(rgb)
    total_g += g
    total_b += b
    frames.append(Image.fromarray(new))

frames[0].save(
    PATH,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=loop,
    optimize=False,
    disposal=1,
)
print(f"{PATH}: {len(frames)} frame, piksel hijau->kuning: {total_g}, biru->merah: {total_b}")
