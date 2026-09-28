"""Build every structure into pack/objects/sundered/<zone>/<name>.iob and write objects-manifest.json.

usage: python3 build_objects.py [--preview DIR]
"""
import json
import os
import sys

from structures import BUILDERS
from voxel import read_iob, VA

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.normpath(os.path.join(HERE, "..", "pack"))


def color(block):
    b = block.split("[")[0].replace("minecraft:", "")
    table = [
        ("gold", (230, 190, 40)), ("emerald", (40, 200, 90)), ("prismarine", (90, 170, 150)), ("lava", (255, 110, 0)),
        ("magma", (180, 60, 20)), ("water", (40, 90, 220)), ("glass", (170, 120, 210)), ("amethyst", (150, 100, 210)),
        ("purple", (120, 60, 150)), ("purpur", (170, 120, 170)), ("red", (160, 40, 40)), ("blue", (50, 70, 160)),
        ("yellow", (220, 200, 60)), ("green", (70, 130, 50)), ("orange", (210, 120, 40)), ("white", (230, 230, 230)),
        ("black", (30, 30, 35)), ("moss", (90, 120, 50)), ("mossy", (100, 120, 90)), ("blackstone", (45, 40, 48)),
        ("basalt", (70, 70, 75)), ("deepslate", (70, 70, 80)), ("obsidian", (30, 20, 50)), ("bone", (220, 215, 190)),
        ("skull", (220, 215, 190)), ("sandstone", (215, 200, 150)), ("sand", (220, 205, 160)), ("terracotta", (160, 90, 60)),
        ("calcite", (225, 225, 220)), ("quartz", (235, 230, 225)), ("mud", (90, 75, 60)), ("dirt", (110, 80, 55)),
        ("gravel", (130, 125, 120)), ("spruce", (110, 80, 50)), ("dark_oak", (70, 50, 30)), ("mangrove", (120, 50, 45)),
        ("oak", (170, 135, 85)), ("log", (100, 75, 45)), ("planks", (160, 125, 80)), ("wool", (200, 200, 200)),
        ("iron", (200, 200, 205)), ("lantern", (255, 210, 120)), ("campfire", (255, 150, 50)), ("fire", (255, 120, 20)),
        ("lamp", (255, 220, 140)), ("light", (255, 230, 170)), ("shroom", (255, 170, 80)), ("tuff", (110, 110, 100)),
        ("netherrack", (120, 40, 40)), ("nether", (80, 30, 35)), ("soul", (80, 65, 55)), ("hay", (200, 170, 50)),
        ("cobble", (120, 120, 120)), ("andesite", (135, 135, 135)), ("stone", (130, 130, 130)), ("ore", (140, 130, 120)),
        ("sculk", (15, 50, 60)), ("rail", (120, 110, 100)), ("ladder", (150, 115, 70)), ("chest", (170, 120, 50)),
        ("barrel", (140, 100, 60)), ("book", (150, 90, 60)), ("web", (235, 235, 235)), ("chain", (60, 60, 70)),
    ]
    for k, c in table:
        if k in b:
            return c
    return (150, 150, 150)


def render(blocks, path, cut=False):
    from PIL import Image, ImageDraw
    pts = {k: v for k, v in blocks.items() if v != VA}
    if cut:
        xs = sorted({k[0] for k in pts})
        mid = xs[len(xs) // 2]
        pts = {k: v for k, v in pts.items() if k[0] <= mid}
    if not pts:
        return
    s = 4
    xs = [k[0] for k in pts]; ys = [k[1] for k in pts]; zs = [k[2] for k in pts]
    minx, maxx, miny, maxy, minz, maxz = min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
    W = int((maxx - minx + maxz - minz + 4) * s * 1.8) + 40
    H = int((maxy - miny + 2) * s * 2 + (maxx - minx + maxz - minz + 2) * s) + 40
    img = Image.new("RGB", (W, H), (24, 26, 32))
    d = ImageDraw.Draw(img)
    ox = (maxz - minz + 2) * s * 1.73 + 20
    oy = (maxy - miny + 1) * s * 2 + 20

    def proj(x, y, z):
        return (ox + (x - minx - (z - minz)) * s * 1.73, oy + (x - minx + z - minz) * s - (y - miny) * s * 2)

    for (x, y, z) in sorted(pts, key=lambda k: (k[0] + k[2], k[1])):
        c = color(pts[(x, y, z)])
        top = [proj(x, y + 1, z), proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x, y + 1, z + 1)]
        left = [proj(x, y + 1, z + 1), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x, y, z + 1)]
        right = [proj(x + 1, y + 1, z), proj(x + 1, y + 1, z + 1), proj(x + 1, y, z + 1), proj(x + 1, y, z)]
        d.polygon(top, fill=c)
        d.polygon(left, fill=tuple(int(v * 0.72) for v in c))
        d.polygon(right, fill=tuple(int(v * 0.55) for v in c))
    img.save(path)


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(preview, exist_ok=True)
    manifest = {}
    for zone, builders in BUILDERS.items():
        out_dir = os.path.join(PACK, "objects", "sundered", zone)
        os.makedirs(out_dir, exist_ok=True)
        for fn in builders:
            v = fn()
            key = f"sundered/{zone}/{v.name}"
            info = v.write(os.path.join(out_dir, v.name + ".iob"))
            w, h, d, blocks = read_iob(os.path.join(out_dir, v.name + ".iob"))
            assert (w, h, d) == (info["w"], info["h"], info["d"]) and len(blocks) == info["blocks"]
            info["underground"] = info["translateY"] < -3
            manifest[key] = info
            print(f"{key:48s} {w:3d}x{h:3d}x{d:3d} blocks={info['blocks']:6d} palette={info['palette']:3d} translateY={info['translateY']}")
            if preview:
                render(v.b, os.path.join(preview, v.name + ".png"))
                if info["underground"]:
                    render(v.b, os.path.join(preview, v.name + "-cutaway.png"), cut=True)
    with open(os.path.join(HERE, "objects-manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(len(manifest), "objects")


if __name__ == "__main__":
    main()
