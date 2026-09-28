"""Tiny voxel toolkit that writes Iris V2 .iob objects.

Coordinates used while building: x = east, z = south, y = up, with y = 0 being the
ground surface block the structure replaces. Anything below 0 is underground. When
written, the object is re-centred the way Iris expects (offsets from w/2, h/2, d/2)
and the vertical translate needed to seat y = 0 on the terrain surface is returned.

Iris skips minecraft:air and minecraft:cave_air when placing objects, but it does
place minecraft:void_air. Void air is therefore used to carve rooms, stairwells and
corridors out of the terrain (the same trick Iris' own smart-bore uses).
"""
import math
import random
import struct
import zlib

VA = "minecraft:void_air"


def _utf(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


class Palette:
    """Weighted block picker. Accepts a block string, a list of strings, or (block, weight) pairs."""

    def __init__(self, entries, rng):
        if isinstance(entries, str):
            entries = [(entries, 1)]
        self.items = [(e, 1) if isinstance(e, str) else e for e in entries]
        self.total = sum(w for _, w in self.items)
        self.rng = rng

    def __call__(self):
        r = self.rng.random() * self.total
        for b, w in self.items:
            r -= w
            if r <= 0:
                return b
        return self.items[-1][0]


class V:
    def __init__(self, name, seed=0):
        self.name = name
        self.b = {}
        self.rng = random.Random(zlib.crc32(name.encode()) ^ seed)

    # ------------------------------------------------------------------ basics
    def pal(self, entries):
        return Palette(entries, self.rng)

    def _block(self, block):
        return block() if callable(block) else block

    def set(self, x, y, z, block):
        if block is None:
            self.b.pop((x, y, z), None)
        else:
            self.b[(x, y, z)] = self._block(block)

    def get(self, x, y, z):
        return self.b.get((x, y, z))

    def fill(self, x1, y1, z1, x2, y2, z2, block):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block)

    def carve(self, x1, y1, z1, x2, y2, z2):
        self.fill(x1, y1, z1, x2, y2, z2, VA)

    def walls(self, x1, y1, z1, x2, y2, z2, block):
        """Four walls of a box (no floor or roof)."""
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.set(x, y, z1, block)
                self.set(x, y, z2, block)
            for z in range(z1, z2 + 1):
                self.set(x1, y, z, block)
                self.set(x2, y, z, block)

    def room(self, x1, y1, z1, x2, y2, z2, wall, floor=None, ceiling=None):
        """Hollow room: shell of `wall` (floor/ceiling overridable), interior carved to void air."""
        self.fill(x1, y1, z1, x2, y2, z2, wall)
        if floor:
            self.fill(x1, y1, z1, x2, y1, z2, floor)
        if ceiling:
            self.fill(x1, y2, z1, x2, y2, z2, ceiling)
        self.carve(x1 + 1, y1 + 1, z1 + 1, x2 - 1, y2 - 1, z2 - 1)

    def cylinder(self, cx, cz, y1, y2, r, block, hollow=False, thickness=1):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            for z in range(int(cz - r - 1), int(cz + r + 2)):
                d = math.hypot(x - cx, z - cz)
                if d <= r + 0.25 and (not hollow or d > r - thickness + 0.25):
                    for y in range(y1, y2 + 1):
                        self.set(x, y, z, block)

    def disc(self, cx, y, cz, r, block):
        self.cylinder(cx, cz, y, y, r, block)

    def cone(self, cx, cz, y0, r0, height, block):
        for i in range(height):
            r = r0 * (1 - i / height)
            self.cylinder(cx, cz, y0 + i, y0 + i, max(r, 0.3), block)

    def line(self, x1, y1, z1, x2, y2, z2, block):
        n = max(abs(x2 - x1), abs(y2 - y1), abs(z2 - z1), 1)
        for i in range(n + 1):
            t = i / n
            self.set(round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t), round(z1 + (z2 - z1) * t), block)

    # --------------------------------------------------------------- weathering
    def weather(self, swaps, chance):
        """Randomly swap blocks: swaps = {'minecraft:stone_bricks': ['minecraft:mossy_stone_bricks', ...]}"""
        for k, v in list(self.b.items()):
            base = v.split("[")[0]
            if base in swaps and self.rng.random() < chance:
                self.b[k] = self.rng.choice(swaps[base])

    def erode(self, chance, predicate=lambda x, y, z: True, keep_below=1):
        """Delete random exposed solid blocks at y >= keep_below to make ruins look crumbled."""
        for (x, y, z), v in list(self.b.items()):
            if v == VA or y < keep_below or not predicate(x, y, z):
                continue
            exposed = any(self.b.get(n) in (None, VA) for n in
                          ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y, z + 1), (x, y, z - 1)))
            if exposed and self.rng.random() < chance:
                if y < 0:
                    self.b[(x, y, z)] = VA
                else:
                    del self.b[(x, y, z)]
        return self

    def sprinkle(self, x1, y1, z1, x2, y2, z2, block, chance, on=None):
        """Place `block` on top of solid blocks (or blocks in `on`) inside a region, with probability."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    below = self.b.get((x, y - 1, z))
                    here = self.b.get((x, y, z))
                    if here not in (None, VA) or below in (None, VA):
                        continue
                    if on and below.split("[")[0] not in on:
                        continue
                    if self.rng.random() < chance:
                        self.set(x, y, z, block)

    # ------------------------------------------------------------------ helpers
    def stairs(self, block, facing, half="bottom"):
        """block is the stair family without namespace, e.g. "stone_brick" -> minecraft:stone_brick_stairs."""
        return f"minecraft:{block}_stairs[facing={facing},half={half},shape=straight,waterlogged=false]"

    def staircase_down(self, x1, x2, z_start, y_start, steps, direction, stair_block, body, headroom=4):
        """A straight staircase that descends `steps` blocks travelling in `direction` (north/south/east/west).
        Carves headroom above every step and puts `body` under it."""
        dx, dz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[direction]
        up = {"north": "south", "south": "north", "east": "west", "west": "east"}[direction]
        for i in range(steps):
            y = y_start - i
            for w in range(x1, x2 + 1):
                if dx == 0:
                    x, z = w, z_start + dz * i
                else:
                    x, z = x1 + dx * i, w
                self.set(x, y - 1, z, body)
                self.set(x, y, z, self.stairs(stair_block, up))
                for h in range(1, headroom + 1):
                    self.set(x, y + h, z, VA)
        return y_start - steps

    def spiral_stair(self, cx, cz, y_top, y_bottom, step, core, radius=2, landing=None):
        """Square spiral stair (full-block steps, two per level) in a shaft around a core column.
        Descends from y_top to a landing floor at y_bottom - 1."""
        r = radius
        ring = [(x, -r) for x in range(-r, r + 1)] + [(r, z) for z in range(-r + 1, r + 1)] \
            + [(x, r) for x in range(r - 1, -r - 1, -1)] + [(-r, z) for z in range(r - 1, -r, -1)]
        self.carve(cx - r, y_bottom, cz - r, cx + r, y_top + 3, cz + r)
        for y in range(y_bottom - 1, y_top + 4):
            self.set(cx, y, cz, core)
        i = 0
        for y in range(y_top, y_bottom - 1, -1):
            for _ in range(2):
                x, z = ring[i % len(ring)]
                self.set(cx + x, y, cz + z, step)
                i += 1
        self.fill(cx - r, y_bottom - 1, cz - r, cx + r, y_bottom - 1, cz + r, landing or step)
        self.set(cx, y_bottom - 1, cz, core)

    def chest(self, x, y, z, facing="north", barrel=False):
        if barrel:
            self.set(x, y, z, "minecraft:barrel[facing=up,open=false]")
        else:
            self.set(x, y, z, f"minecraft:chest[facing={facing},type=single,waterlogged=false]")

    # -------------------------------------------------------------------- output
    def bounds(self):
        xs = [k[0] for k in self.b]
        ys = [k[1] for k in self.b]
        zs = [k[2] for k in self.b]
        return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)

    def write(self, path):
        x0, y0, z0, x1, y1, z1 = self.bounds()
        w, h, d = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
        cx, cy, cz = w // 2, h // 2, d // 2
        palette, index = [], {}
        for v in self.b.values():
            if v not in index:
                index[v] = len(palette)
                palette.append(v)
        if len(palette) > 32767:
            raise ValueError(f"{self.name}: palette too large")
        out = bytearray()
        out += struct.pack(">iii", w, h, d)
        out += _utf("Iris V2 IOB;")
        out += struct.pack(">h", len(palette))
        for p in palette:
            out += _utf(p)
        out += struct.pack(">i", len(self.b))
        for (x, y, z), v in sorted(self.b.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])):
            out += struct.pack(">hhhh", x - x0 - cx, y - y0 - cy, z - z0 - cz, index[v])
        out += struct.pack(">i", 0)  # no tile states: Iris fills containers from loot tables
        with open(path, "wb") as f:
            f.write(out)
        # Iris places local y = 0 of the written object at the surface; our y = 0 is ground,
        # so the placement must shift by the depth of the underground portion.
        return {"w": w, "h": h, "d": d, "translateY": y0, "blocks": len(self.b), "palette": len(palette),
                "centerOffsetX": -(x0 + cx), "centerOffsetZ": -(z0 + cz)}


def read_iob(path):
    """Round-trip reader used by the self-test."""
    with open(path, "rb") as f:
        data = f.read()
    p = 0

    def take(fmt):
        nonlocal p
        v = struct.unpack_from(fmt, data, p)
        p += struct.calcsize(fmt)
        return v

    def utf():
        nonlocal p
        (n,) = take(">H")
        s = data[p:p + n].decode("utf-8")
        p += n
        return s

    w, h, d = take(">iii")
    assert utf() == "Iris V2 IOB;"
    (n,) = take(">h")
    pal = [utf() for _ in range(n)]
    (c,) = take(">i")
    blocks = {}
    for _ in range(c):
        x, y, z, i = take(">hhhh")
        assert -(w // 2) <= x < w - w // 2 and -(h // 2) <= y < h - h // 2 and -(d // 2) <= z < d - d // 2
        blocks[(x, y, z)] = pal[i]
    (t,) = take(">i")
    assert t == 0 and p == len(data)
    return w, h, d, blocks
