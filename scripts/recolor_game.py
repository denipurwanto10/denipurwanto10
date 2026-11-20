#!/usr/bin/env python3
"""Recolor the space shooter GIF: blocks -> cyan, ship -> green, bullets -> purple.

Usage:
  python scripts/recolor_game.py game.gif                  # GIF fresh from the generator
  python scripts/recolor_game.py game.gif --from-current   # GIF already recolored (yellow blocks, red ship, cyan bullets)
"""
import sys
import numpy as np
from PIL import Image, ImageSequence

args = [a for a in sys.argv[1:] if not a.startswith("--")]
FROM_CURRENT = "--from-current" in sys.argv
PATH = args[0] if args else "game.gif"

CYAN_HUE = 182.0
GREEN_HUE = 130.0
PURPLE_HUE = 272.0


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

    if FROM_CURRENT:
        # current GIF: yellow blocks -> cyan, red ship -> green, cyan bullets -> purple
        blocks = colored & (h >= 38) & (h <= 68)
        ship = colored & ((h <= 15) | (h >= 345))
        bullet = colored & (h >= 170) & (h <= 200)
    else:
        # generator output: green blocks -> cyan, blue ship -> green, yellow bullets -> purple
        blocks = colored & (h >= 80) & (h <= 170)
        ship = colored & (h >= 190) & (h <= 260)
        bullet = colored & (h >= 38) & (h <= 68)

    h2 = h.copy()
    h2[blocks] = CYAN_HUE
    h2[ship] = GREEN_HUE
    h2[bullet] = PURPLE_HUE
    changed = blocks | ship | bullet

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
    return result, int(blocks.sum()), int(ship.sum()), int(bullet.sum())


src = Image.open(PATH)
loop = src.info.get("loop", 0)
frames, durations = [], []
tot_blocks = tot_ship = tot_bullet = 0
for frame in ImageSequence.Iterator(src):
    durations.append(frame.info.get("duration", 40))
    rgb = np.array(frame.convert("RGB"))
    new, nb, ns, nbu = recolor(rgb)
    tot_blocks += nb
    tot_ship += ns
    tot_bullet += nbu
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
print(f"{PATH}: {len(frames)} frame, kotak->cyan: {tot_blocks}, pesawat->hijau: {tot_ship}, tembakan->ungu: {tot_bullet}")
