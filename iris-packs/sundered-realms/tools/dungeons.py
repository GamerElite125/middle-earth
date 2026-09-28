"""Shared underground dungeon generator.

Every dungeon object in the pack is a themed surface entrance sitting on top of a spiral
stair shaft that drops into a complex built here: a pillared central hall with corridors
leading to themed side chambers. Room and corridor volumes are carved with void air so the
complex cuts a real space out of the terrain it lands in.
"""
from voxel import VA

CANDLE = "minecraft:candle[candles=3,lit=true,waterlogged=false]"
WEB = "minecraft:cobweb"


def lantern(theme):
    return f"{theme.get('lantern', 'minecraft:lantern')}[hanging=true,waterlogged=false]"


def dungeon(v, theme, cx=0, cz=0, floor_y=-16, rooms=("treasure", "crypt", "shrine"), shaft_top=0,
            hall_half=6, corridor=6, hall_h=6):
    """Build a dungeon whose entry shaft is centred on (cx, cz). The central hall lies south of it.

    theme keys: wall, floor, ceiling, pillar, step, core, lantern, accent, web (chance),
    feature (callable(v, x, y, z)) for the hall centrepiece.
    """
    wall, floor = v.pal(theme["wall"]), v.pal(theme.get("floor", theme["wall"]))
    ceiling = v.pal(theme.get("ceiling", theme["wall"]))
    pillar = theme.get("pillar", theme["wall"][0][0] if isinstance(theme["wall"], list) else theme["wall"])
    accent = theme.get("accent", "minecraft:chiseled_stone_bricks")

    # entry shaft
    v.fill(cx - 3, floor_y, cz - 3, cx + 3, shaft_top - 1, cz + 3, wall)
    v.spiral_stair(cx, cz, shaft_top - 1, floor_y + 1, v.pal(theme.get("step", theme["wall"])), theme.get("core", pillar),
                   radius=2, landing=floor)
    for y in range(floor_y + 3, shaft_top - 1, 6):
        v.set(cx, y, cz, theme.get("core_light", "minecraft:shroomlight"))

    # corridor from shaft south to hall
    hz0 = cz + 3 + corridor  # hall north wall z
    v.room(cx - 2, floor_y, cz + 2, cx + 2, floor_y + 5, hz0 + 1, wall, floor, ceiling)
    v.carve(cx - 1, floor_y + 1, cz + 2, cx + 1, floor_y + 4, cz + 2)  # open into shaft
    hcz = hz0 + hall_half  # hall centre z
    _hall(v, theme, cx, hcz, floor_y, hall_half, hall_h, wall, floor, ceiling, pillar, accent)
    v.carve(cx - 1, floor_y + 1, hz0 - 1, cx + 1, floor_y + 4, hz0 + 1)  # doorway into hall
    v.set(cx - 2, floor_y + 5, hz0, accent)
    v.set(cx + 2, floor_y + 5, hz0, accent)

    # side chambers: east, west, south
    slots = [("east", cx + hall_half + corridor + 5, hcz), ("west", cx - hall_half - corridor - 5, hcz),
             ("south", cx, hcz + hall_half + corridor + 5)]
    for (side, rx, rz), kind in zip(slots, rooms):
        if side in ("east", "west"):
            sgn = 1 if side == "east" else -1
            x_a, x_b = cx + sgn * hall_half, rx - sgn * 4
            v.room(min(x_a, x_b), floor_y, rz - 2, max(x_a, x_b), floor_y + 5, rz + 2, wall, floor, ceiling)
            v.carve(min(x_a, x_b) - 1, floor_y + 1, rz - 1, max(x_a, x_b) + 1, floor_y + 3, rz + 1)
        else:
            z_a, z_b = hcz + hall_half, rz - 4
            v.room(rx - 2, floor_y, z_a, rx + 2, floor_y + 5, z_b, wall, floor, ceiling)
            v.carve(rx - 1, floor_y + 1, z_a - 1, rx + 1, floor_y + 3, z_b + 1)
        _chamber(v, theme, kind, rx, rz, floor_y, wall, floor, ceiling, accent)

    # cobwebs in upper corners of everything carved
    web = theme.get("web", 0.06)
    for (x, y, z), b in list(v.b.items()):
        if b == VA and y < shaft_top - 2 and y >= floor_y + 3 and v.rng.random() < web:
            if v.get(x, y + 1, z) not in (None, VA) and (v.get(x + 1, y, z) not in (None, VA) or v.get(x - 1, y, z) not in (None, VA)
                                                         or v.get(x, y, z + 1) not in (None, VA) or v.get(x, y, z - 1) not in (None, VA)):
                v.set(x, y, z, theme.get("web_block", WEB))
    return hcz


def _hall(v, theme, cx, cz, fy, hh, h, wall, floor, ceiling, pillar, accent):
    v.room(cx - hh, fy, cz - hh, cx + hh, fy + h + 1, cz + hh, wall, floor, ceiling)
    # vaulted ceiling ribs
    for x in range(cx - hh + 1, cx + hh):
        if (x - cx) % 3 == 0:
            for z in range(cz - hh + 1, cz + hh):
                v.set(x, fy + h, z, accent)
    # pillars
    for px in (cx - hh + 3, cx + hh - 3):
        for pz in (cz - hh + 3, cz + hh - 3):
            v.fill(px, fy + 1, pz, px, fy + h, pz, pillar)
            v.set(px + (1 if px > cx else -1), fy + h - 1, pz, "minecraft:iron_chain[axis=y,waterlogged=false]")
            v.set(px + (1 if px > cx else -1), fy + h - 2, pz, lantern(theme))
    # floor inlay
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 3):
            if abs(x - cx) == 2 or abs(z - cz) == 2:
                v.set(x, fy, z, accent)
    feature = theme.get("feature")
    if feature:
        feature(v, cx, fy + 1, cz)
    else:
        v.set(cx, fy + 1, cz, "minecraft:lodestone")
        v.set(cx, fy + 2, cz, CANDLE)
    # wall candles / skulls
    for z in (cz - hh + 2, cz + hh - 2):
        for x in (cx - hh + 1, cx + hh - 1):
            v.set(x, fy + 1, z, theme.get("hall_decor", "minecraft:skeleton_skull[rotation=0]"))


def _chamber(v, theme, kind, cx, cz, fy, wall, floor, ceiling, accent):
    v.room(cx - 4, fy, cz - 4, cx + 4, fy + 5, cz + 4, wall, floor, ceiling)
    v.set(cx, fy + 4, cz, lantern(theme))
    if kind == "treasure":
        v.fill(cx - 1, fy + 1, cz - 1, cx + 1, fy + 1, cz + 1, accent)
        v.chest(cx, fy + 2, cz, "south")
        v.chest(cx - 3, fy + 1, cz + 3, "north")
        v.chest(cx + 3, fy + 1, cz - 3, "south")
        for x, z in ((cx - 3, cz - 3), (cx + 3, cz + 3), (cx - 3, cz), (cx + 3, cz)):
            v.set(x, fy + 1, z, v.pal(theme.get("riches", ["minecraft:gold_block", "minecraft:raw_gold_block"]))())
    elif kind == "crypt":
        for x in (cx - 2, cx + 2):
            v.fill(x, fy + 1, cz - 2, x, fy + 1, cz + 2, theme.get("sarcophagus", "minecraft:smooth_stone"))
            v.set(x, fy + 2, cz - 2, "minecraft:skeleton_skull[rotation=8]")
        v.chest(cx, fy + 1, cz + 3, "north")
        v.sprinkle(cx - 3, fy + 1, cz - 3, cx + 3, fy + 1, cz + 3, "minecraft:bone_block[axis=y]", 0.05)
    elif kind == "shrine":
        v.fill(cx - 1, fy + 1, cz + 2, cx + 1, fy + 1, cz + 3, accent)
        v.set(cx, fy + 2, cz + 3, theme.get("idol", "minecraft:gold_block"))
        v.set(cx - 1, fy + 2, cz + 2, CANDLE)
        v.set(cx + 1, fy + 2, cz + 2, CANDLE)
        v.chest(cx, fy + 2, cz + 2, "north")
    elif kind == "prison":
        for z in (cz - 3, cz + 3):
            for x in range(cx - 3, cx + 4):
                v.set(x, fy + 1, z + (1 if z < cz else -1), "minecraft:iron_bars")
                v.set(x, fy + 2, z + (1 if z < cz else -1), "minecraft:iron_bars")
                v.set(x, fy + 3, z + (1 if z < cz else -1), "minecraft:iron_bars")
        v.set(cx, fy + 1, cz - 3, "minecraft:skeleton_skull[rotation=0]")
        v.set(cx - 2, fy + 1, cz + 3, "minecraft:bone_block[axis=x]")
        v.chest(cx + 3, fy + 1, cz, "west")
        v.set(cx, fy + 1, cz, "minecraft:iron_chain[axis=y,waterlogged=false]")
    elif kind == "library":
        for x in range(cx - 3, cx + 4):
            for y in range(fy + 1, fy + 4):
                v.set(x, y, cz - 3, "minecraft:bookshelf")
                v.set(x, y, cz + 3, "minecraft:chiseled_bookshelf[facing=north,slot_0_occupied=true,slot_1_occupied=false,slot_2_occupied=true,slot_3_occupied=false,slot_4_occupied=true,slot_5_occupied=false]")
        v.set(cx, fy + 1, cz, "minecraft:lectern[facing=north,has_book=false,powered=false]")
        v.chest(cx + 3, fy + 1, cz, "west")
    elif kind == "armory":
        for x in (cx - 3, cx + 3):
            for z in range(cz - 2, cz + 3, 2):
                v.set(x, fy + 1, z, "minecraft:barrel[facing=up,open=false]")
        v.set(cx, fy + 1, cz - 3, "minecraft:anvil[facing=east]")
        v.set(cx - 1, fy + 1, cz - 3, "minecraft:grindstone[face=floor,facing=north]")
        v.set(cx + 1, fy + 1, cz - 3, "minecraft:smithing_table")
        v.chest(cx, fy + 1, cz + 3, "north")
    elif kind == "flooded":
        v.fill(cx - 3, fy, cz - 3, cx + 3, fy + 1, cz + 3, theme.get("fluid", "minecraft:water"))
        v.fill(cx - 1, fy, cz - 1, cx + 1, fy + 1, cz + 1, accent)
        v.chest(cx, fy + 2, cz, "south")
    elif kind == "forge":
        v.fill(cx - 3, fy, cz - 1, cx + 3, fy, cz + 1, "minecraft:lava")
        v.fill(cx - 3, fy + 1, cz + 3, cx + 3, fy + 1, cz + 3, "minecraft:blast_furnace[facing=north,lit=false]")
        v.set(cx, fy + 1, cz - 3, "minecraft:anvil[facing=east]")
        v.chest(cx - 3, fy + 1, cz - 3, "south")
        v.chest(cx + 3, fy + 1, cz - 3, "south")
    elif kind == "altar":
        v.fill(cx - 2, fy + 1, cz - 2, cx + 2, fy + 1, cz + 2, accent)
        v.set(cx, fy + 2, cz, theme.get("idol", "minecraft:crying_obsidian"))
        for x, z in ((cx - 2, cz - 2), (cx + 2, cz - 2), (cx - 2, cz + 2), (cx + 2, cz + 2)):
            v.set(x, fy + 2, z, "minecraft:soul_campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
        v.chest(cx, fy + 1, cz + 3, "north")


def shaft_frame(v, cx, cz, rim, post, cap=None, open_side="north", height=4, lintel=None):
    """Ring an open-air dungeon shaft with a waist-high rim, corner posts and an optional lintel over the gap."""
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            if max(abs(dx), abs(dz)) != 3:
                continue
            gap = {"north": dz == -3 and abs(dx) <= 1, "south": dz == 3 and abs(dx) <= 1,
                   "east": dx == 3 and abs(dz) <= 1, "west": dx == -3 and abs(dz) <= 1}[open_side]
            if gap:
                v.set(cx + dx, 1, cz + dz, VA)
                continue
            v.set(cx + dx, 1, cz + dz, rim)
    for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        v.fill(cx + dx, 1, cz + dz, cx + dx, height, cz + dz, post)
        if cap:
            v.set(cx + dx, height + 1, cz + dz, cap)
    if lintel:
        ox, oz = {"north": (0, -3), "south": (0, 3), "east": (3, 0), "west": (-3, 0)}[open_side]
        for i in (-2, -1, 0, 1, 2):
            x, z = (cx + i, cz + oz) if ox == 0 else (cx + ox, cz + i)
            v.set(x, height, z, lintel)
