"""All hand-designed structures of the Sundered Realms pack.

Each builder returns a voxel.V. build_objects.py writes them to objects/sundered/<zone>/<name>.iob
and records the vertical translate each one needs in objects-manifest.json.
"""
import math

from voxel import V, VA
from dungeons import dungeon, shaft_frame, CANDLE

M = "minecraft:"


def S(block, **props):
    if not props:
        return M + block
    return M + block + "[" + ",".join(f"{k}={v}" for k, v in props.items()) + "]"


def stair(block, facing, half="bottom"):
    """block is the stair family, e.g. "stone_brick" -> minecraft:stone_brick_stairs."""
    return S(block + "_stairs", facing=facing, half=half, shape="straight", waterlogged="false")


def slab(block, typ="bottom"):
    return S(block, type=typ, waterlogged="false")


def fence(block):
    return M + block


LANTERN = S("lantern", hanging="false", waterlogged="false")
HLANTERN = S("lantern", hanging="true", waterlogged="false")
SOUL_LANTERN = S("soul_lantern", hanging="false", waterlogged="false")
HSOUL_LANTERN = S("soul_lantern", hanging="true", waterlogged="false")
CAMPFIRE = S("campfire", facing="north", lit="true", signal_fire="false", waterlogged="false")
SOUL_CAMPFIRE = S("soul_campfire", facing="north", lit="true", signal_fire="false", waterlogged="false")
CHAIN = S("iron_chain", axis="y", waterlogged="false")  # "chain" was renamed in 1.21.9
SKULL = S("skeleton_skull", rotation="8")
WSKULL = S("wither_skeleton_skull", rotation="8")

MAYAN = [(M + "mossy_stone_bricks", 4), (M + "stone_bricks", 3), (M + "cracked_stone_bricks", 2),
         (M + "mossy_cobblestone", 1)]
JADE = M + "prismarine_bricks"


# =============================================================================== AZURE ISLES
def sun_serpent_pyramid():
    """Great step pyramid of the Sun Serpent. Temple on top, burial chamber inside, crypt below."""
    v = V("sun-serpent-pyramid")
    stone = v.pal(MAYAN)
    halves = [20, 17, 14, 11, 8, 5]
    for k, hf in enumerate(halves):
        y0 = k * 3
        v.fill(-hf, y0, -hf, hf, y0 + 2, hf, stone)
        # carved glyph band on each tier face
        for i in range(-hf + 1, hf, 2):
            for x, z in ((i, -hf), (i, hf), (-hf, i), (hf, i)):
                v.set(x, y0 + 1, z, M + "chiseled_stone_bricks")
        # jade trim on tier lip
        for i in range(-hf, hf + 1):
            for x, z in ((i, -hf), (i, hf), (-hf, i), (hf, i)):
                if (i + k) % 5 == 0:
                    v.set(x, y0 + 2, z, JADE)
    top = 18
    # grand staircase (north face) with serpent balustrades
    for y in range(0, top + 1):
        z = -23 + y
        for x in range(-2, 3):
            v.fill(x, 0, z, x, y - 1, z, stone) if y > 0 else None
            v.set(x, y, z, stair("stone_brick", "south"))
            for h in range(1, 4):
                if v.get(x, y + h, z) is not None and y + h < top:
                    v.set(x, y + h, z, VA)
        for x in (-3, 3):
            v.fill(x, 0, z, x, y, z, stone)
            v.set(x, y + 1, z, M + "chiseled_stone_bricks" if y % 3 == 0 else stone)
    # feathered serpent heads guarding the stair base
    for x in (-3, 3):
        v.fill(x - 1 if x < 0 else x, 0, -26, x if x < 0 else x + 1, 2, -24, M + "mossy_stone_bricks")
        v.set(x, 2, -27, stair("stone_brick", "south"))
        v.set(x, 1, -27, stair("stone_brick", "south", "top"))
        v.set(x, 0, -27, S("red_nether_brick_slab", type="bottom", waterlogged="false"))
        v.set(x - 1 if x < 0 else x + 1, 2, -26, M + "emerald_block")
        v.set(x, 3, -25, JADE)
        v.set(x, 3, -24, JADE)
    # summit temple
    v.fill(-5, top, -5, 5, top, 5, M + "chiseled_stone_bricks")
    v.room(-4, top, -4, 4, top + 7, 4, stone, M + "polished_andesite", M + "stone_bricks")
    for x in (-2, 0, 2):
        v.carve(x, top + 1, -4, x, top + 4, -4)
    for x in (-3, -1, 1, 3):
        v.fill(x, top + 1, -5, x, top + 5, -5, M + "chiseled_stone_bricks")
    # roof comb (crest)
    for x in range(-4, 5):
        for y in range(top + 8, top + 12):
            if (x + y) % 2 == 0 or y == top + 8:
                v.set(x, y, -1, S("stone_brick_wall", east="low", west="low", north="none", south="none", up="true", waterlogged="false"))
    v.set(0, top + 12, -1, M + "gold_block")
    for x, z in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
        v.set(x, top + 1, z, CAMPFIRE)
    # altar and hidden shaft to the burial chamber
    v.fill(-1, top + 1, 2, 1, top + 1, 3, M + "gold_block")
    v.set(0, top + 2, 3, CANDLE)
    v.carve(-1, 2, -1, 1, top, 1)
    # burial chamber inside the pyramid
    v.room(-6, 0, -6, 6, 7, 6, stone, M + "smooth_stone", M + "stone_bricks")
    v.carve(-1, 2, -1, 1, 7, 1)
    v.set(0, 1, 0, M + "chiseled_stone_bricks")
    v.fill(-2, 1, 4, 2, 1, 5, M + "gold_block")
    v.fill(0, 1, 3, 0, 7, 3, JADE)
    v.fill(0, 1, 2, 0, top, 2, S("ladder", facing="north", waterlogged="false"))
    v.set(-5, 1, -5, HLANTERN.replace("hanging=true", "hanging=false"))
    v.chest(-5, 1, 5, "north")
    v.chest(5, 1, 5, "north")
    # collapsed side tunnel from the south foot of the pyramid
    for z in range(6, 21):
        v.carve(-1, 1, z, 1, 3, z)
        v.set(-2, 1, z, M + "mossy_cobblestone")
        v.set(2, 1, z, M + "mossy_cobblestone")
    v.fill(-1, 1, 12, 1, 1, 13, M + "gravel")
    # stair down to the crypt of the Serpent Kings
    theme = {
        "wall": MAYAN, "floor": [(M + "polished_andesite", 3), (M + "mossy_stone_bricks", 1)],
        "pillar": JADE, "accent": M + "chiseled_stone_bricks", "step": M + "mossy_stone_bricks",
        "core": JADE, "core_light": M + "sea_lantern", "web": 0.05, "lantern": "minecraft:lantern",
        "riches": [M + "gold_block", M + "emerald_block", M + "raw_gold_block"],
        "idol": M + "emerald_block",
        "feature": lambda v, x, y, z: (v.fill(x - 1, y, z - 1, x + 1, y, z + 1, M + "gold_block"),
                                       v.set(x, y + 1, z, M + "emerald_block"),
                                       v.set(x, y + 2, z, CANDLE)),
    }
    v.weather({M + "stone_bricks": [M + "mossy_stone_bricks", M + "cracked_stone_bricks"]}, 0.15)
    dungeon(v, theme, cx=-3, cz=0, floor_y=-20, rooms=("treasure", "crypt", "flooded"), shaft_top=1, hall_half=6)
    return v


def jungle_shrine():
    v = V("jungle-shrine")
    stone = v.pal(MAYAN)
    v.fill(-5, 0, -5, 5, 0, 5, stone)
    v.fill(-4, 1, -4, 4, 1, 4, stone)
    for x, z in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        v.fill(x, 2, z, x, 6, z, M + "chiseled_stone_bricks" if x < 0 else stone)
    v.fill(-3, 7, -3, 3, 7, 3, stone)
    v.set(0, 2, 2, JADE)
    v.set(0, 3, 2, M + "emerald_block")
    v.set(-1, 2, 2, CANDLE)
    v.set(1, 2, 2, CANDLE)
    v.chest(0, 2, 0, "south")
    for x in range(-3, 4):
        v.set(x, 2, -4, stair("stone_brick", "north"))
    v.erode(0.35, lambda x, y, z: y >= 5)
    return v


def serpent_stela():
    v = V("serpent-stela")
    for y in range(0, 9):
        for x in (-1, 0, 1):
            v.set(x, y, 0, M + ("chiseled_stone_bricks" if (x + y) % 3 == 0 else "mossy_stone_bricks"))
    v.set(0, 9, 0, M + "gold_block")
    v.set(0, 6, -1, M + "emerald_block")
    v.set(-1, 0, -1, stair("mossy_stone_brick", "south"))
    v.set(1, 0, -1, stair("mossy_stone_brick", "south"))
    return v


def cenote_temple():
    """Sacred sinkhole: a ring shrine around a flooded well; a spiral descends to the drowned sanctum."""
    v = V("cenote-temple")
    stone = v.pal(MAYAN)
    v.cylinder(0, 0, 0, 0, 8, stone)
    v.cylinder(0, 0, 1, 1, 8, stone, hollow=True)
    for a in range(0, 360, 45):
        x, z = round(7 * math.cos(math.radians(a))), round(7 * math.sin(math.radians(a)))
        v.fill(x, 1, z, x, 5, z, M + "chiseled_stone_bricks")
        v.set(x, 6, z, CAMPFIRE if a % 90 == 0 else JADE)
    v.cylinder(0, 0, -6, 0, 4, VA)
    v.cylinder(0, 0, -6, -6, 4, M + "water")
    theme = {
        "wall": MAYAN, "floor": [(M + "mossy_stone_bricks", 1), (M + "moss_block", 1)],
        "ceiling": [(M + "mossy_stone_bricks", 3), (M + "dripstone_block", 1)],
        "pillar": JADE, "accent": JADE, "core": M + "mossy_stone_bricks", "core_light": M + "sea_lantern",
        "web": 0.03, "riches": [M + "gold_block", M + "emerald_block"],
        "feature": lambda v, x, y, z: (v.fill(x - 2, y - 1, z - 2, x + 2, y - 1, z + 2, M + "water"),
                                       v.set(x, y - 1, z, JADE), v.set(x, y, z, M + "conduit[waterlogged=false]")),
        "hall_decor": M + "moss_carpet",
    }
    dungeon(v, theme, cx=0, cz=-13, floor_y=-24, rooms=("flooded", "treasure", "shrine"), shaft_top=1)
    shaft_frame(v, 0, -13, M + "mossy_stone_bricks", M + "chiseled_stone_bricks", cap=JADE, open_side="south",
                height=4, lintel=M + "emerald_block")
    return v


def pirate_cove():
    v = V("pirate-cove")
    plank = v.pal([(M + "spruce_planks", 3), (M + "dark_oak_planks", 1)])
    # dock on posts reaching over the water (north side)
    for z in range(-14, 1):
        for x in (-2, -1, 0, 1, 2):
            v.set(x, 1, z, plank)
        if z % 3 == 0:
            for x in (-2, 2):
                v.fill(x, -4, z, x, 0, z, M + "spruce_log[axis=y]")
                v.set(x, 2, z, fence("spruce_fence"))
    v.set(-2, 3, -14, LANTERN)
    v.set(2, 3, -14, LANTERN)
    # shack
    v.fill(-5, 0, 1, 5, 0, 9, plank)
    v.walls(-5, 1, 1, 5, 4, 9, M + "stripped_spruce_log[axis=y]")
    v.carve(-4, 1, 2, 4, 4, 8)
    v.carve(-1, 1, 1, 0, 2, 1)
    for x in range(-6, 7):
        for z in range(0, 11):
            y = 5 + min(z, 10 - z) // 2
            v.set(x, y, z, stair("dark_oak", "south" if z < 5 else "north") if z != 5 else M + "dark_oak_planks")
    v.set(3, 2, 1, M + "glass_pane")
    v.set(-3, 2, 1, M + "glass_pane")
    v.chest(-4, 1, 8, "north")
    v.chest(4, 1, 8, "north")
    v.set(0, 1, 8, M + "barrel[facing=up,open=false]")
    v.set(-4, 1, 3, M + "barrel[facing=up,open=false]")
    v.set(4, 1, 3, M + "cartography_table")
    v.set(0, 4, 5, HLANTERN)
    # cannon pointing out to sea
    v.set(3, 2, -3, M + "black_concrete")
    v.set(3, 2, -4, M + "polished_blackstone_button[face=wall,facing=north,powered=false]")
    v.set(3, 1, -2, M + "dark_oak_planks")
    # jolly roger
    v.fill(-6, 1, 0, -6, 9, 0, M + "spruce_fence")
    v.fill(-6, 7, 1, -6, 9, 3, M + "black_wool")
    v.set(-6, 8, 2, M + "white_wool")
    return v


def volcano_caldera():
    """Summit crown for volcanoes: jagged basalt rim, magma skirt, lava lake and a smoking vent."""
    v = V("volcano-caldera")
    rim = v.pal([(M + "basalt[axis=y]", 3), (M + "blackstone", 3), (M + "tuff", 1), (M + "magma_block", 1)])
    for x in range(-14, 15):
        for z in range(-14, 15):
            d = math.hypot(x, z)
            if d <= 14:
                if d > 10:
                    h = 2 + int(4 * (1 - abs(d - 12) / 3)) + v.rng.randint(0, 3)
                    v.fill(x, -3, z, x, h, z, rim)
                elif d > 7:
                    v.fill(x, -3, z, x, 0, z, v.pal([(M + "magma_block", 2), (M + "blackstone", 1)]))
                    v.carve(x, 1, z, x, 4, z)
                else:
                    v.fill(x, -4, z, x, -2, z, M + "magma_block")
                    v.fill(x, -1, z, x, 0, z, M + "lava")
                    v.carve(x, 1, z, x, 4, z)
    v.fill(0, -1, 0, 0, 2, 0, M + "obsidian")
    v.set(0, 3, 0, SOUL_CAMPFIRE.replace("signal_fire=false", "signal_fire=true"))
    return v


def ember_temple():
    """Obsidian step temple on the volcano flanks; its forge vault lies beneath."""
    v = V("ember-temple")
    stone = v.pal([(M + "polished_blackstone_bricks", 4), (M + "cracked_polished_blackstone_bricks", 2), (M + "blackstone", 1)])
    for k, hf in enumerate([10, 8, 6]):
        v.fill(-hf, k * 3, -hf, hf, k * 3 + 2, hf, stone)
        for i in range(-hf, hf + 1, 3):
            v.set(i, k * 3 + 1, -hf, M + "gilded_blackstone")
    for y in range(0, 9):
        for x in (-1, 0, 1):
            v.set(x, y, -13 + y, stair("polished_blackstone_brick", "south"))
            v.carve(x, y + 1, -13 + y, x, y + 3, -13 + y)
    v.room(-4, 9, -4, 4, 14, 4, stone, M + "polished_blackstone", M + "obsidian")
    v.carve(-1, 10, -4, 1, 12, -4)
    v.fill(-1, 10, 3, 1, 10, 3, M + "magma_block")
    v.set(0, 11, 3, M + "crying_obsidian")
    for x in (-5, 5):
        v.set(x, 10, -5, SOUL_CAMPFIRE)
    theme = {
        "wall": [(M + "polished_blackstone_bricks", 3), (M + "basalt[axis=y]", 1)],
        "floor": M + "polished_blackstone", "pillar": M + "polished_basalt[axis=y]",
        "accent": M + "gilded_blackstone", "core": M + "obsidian", "core_light": M + "magma_block",
        "lantern": "minecraft:soul_lantern", "web": 0.02, "idol": M + "crying_obsidian",
        "feature": lambda v, x, y, z: (v.fill(x - 1, y - 1, z - 1, x + 1, y - 1, z + 1, M + "lava"),
                                       v.set(x, y, z, M + "obsidian")),
    }
    dungeon(v, theme, cx=0, cz=0, floor_y=-16, rooms=("forge", "treasure", "altar"), shaft_top=9)
    return v


# =============================================================================== ASHFANG REACH
PALISADE = [(M + "spruce_log[axis=y]", 3), (M + "dark_oak_log[axis=y]", 2), (M + "stripped_spruce_log[axis=y]", 1)]


def orc_warcamp():
    v = V("orc-warcamp")
    ground = v.pal([(M + "coarse_dirt", 3), (M + "packed_mud", 1), (M + "soul_soil", 1)])
    v.cylinder(0, 0, 0, 0, 16, ground)
    log = v.pal(PALISADE)
    for a in range(0, 360, 4):
        x, z = round(15 * math.cos(math.radians(a))), round(15 * math.sin(math.radians(a)))
        if -2 <= x <= 2 and z < 0:
            continue  # gate
        h = 5 + v.rng.randint(0, 2)
        v.fill(x, 1, z, x, h, z, log)
        v.set(x, h + 1, z, M + "pointed_dripstone[thickness=tip,vertical_direction=up,waterlogged=false]")
    # gate towers with skulls
    for x in (-3, 3):
        v.fill(x, 1, -15, x, 9, -15, M + "dark_oak_log[axis=y]")
        v.set(x, 10, -15, SKULL)
    v.fill(-3, 8, -15, 3, 8, -15, M + "dark_oak_planks")
    # hide tents
    for i, (tx, tz) in enumerate([(-8, -4), (8, -4), (-7, 7), (7, 7)]):
        wool = [M + "brown_wool", M + "black_wool", M + "gray_wool", M + "red_wool"][i]
        for dz in range(-2, 3):
            for dx in range(-3, 4):
                y = 4 - abs(dx)
                if y >= 1:
                    v.set(tx + dx, y, tz + dz, wool)
            v.carve(tx - 1, 1, tz + dz, tx + 1, 2, tz + dz) if abs(dz) < 2 else None
        v.set(tx, 1, tz - 2, VA)
        v.set(tx, 2, tz - 2, VA)
        v.chest(tx, 1, tz + 1, "north") if i % 2 == 0 else v.set(tx, 1, tz + 1, M + "barrel[facing=up,open=false]")
    # great bonfire
    v.cylinder(0, 0, 0, 0, 2, M + "netherrack")
    v.set(0, 1, 0, M + "fire")
    for dx, dz in ((-2, 0), (2, 0), (0, 2), (0, -2)):
        v.set(dx, 1, dz, SOUL_CAMPFIRE)
    # skull pikes, cages, weapon racks
    for x, z in ((-5, -10), (5, -10), (-11, 1), (11, 1)):
        v.fill(x, 1, z, x, 3, z, M + "spruce_fence")
        v.set(x, 4, z, SKULL)
    for x, z in ((0, 11),):
        v.walls(x - 1, 1, z - 1, x + 1, 3, z + 1, M + "iron_bars")
        v.fill(x - 1, 4, z - 1, x + 1, 4, z + 1, M + "dark_oak_slab[type=bottom,waterlogged=false]")
        v.set(x, 1, z, M + "bone_block[axis=y]")
    v.set(-4, 1, 11, M + "grindstone[face=floor,facing=north]")
    v.set(4, 1, 11, M + "anvil[facing=east]")
    v.set(0, 1, 12, M + "chest[facing=north,type=single,waterlogged=false]")
    return v


def skullgate_fortress():
    """Blackstone war-fortress of the Ashfang warlord. The Maw (dungeon pits) lies beneath the courtyard."""
    v = V("skullgate-fortress")
    wall = v.pal([(M + "polished_blackstone_bricks", 4), (M + "cracked_polished_blackstone_bricks", 2),
                  (M + "blackstone", 2), (M + "red_nether_bricks", 1)])
    H = 17
    v.fill(-H, 0, -H, H, 0, H, M + "polished_blackstone")
    v.walls(-H, 1, -H, H, 9, H, wall)
    v.walls(-H + 1, 1, -H + 1, H - 1, 9, H - 1, wall)
    for i in range(-H, H + 1, 2):
        for x, z in ((i, -H), (i, H), (-H, i), (H, i)):
            v.set(x, 10, z, wall)
    # corner towers with iron spikes
    for tx in (-H, H):
        for tz in (-H, H):
            v.cylinder(tx, tz, 0, 15, 4, wall)
            v.cylinder(tx, tz, 1, 14, 2.4, VA)
            for a in range(0, 360, 60):
                x, z = tx + round(4 * math.cos(math.radians(a))), tz + round(4 * math.sin(math.radians(a)))
                v.fill(x, 16, z, x, 18, z, M + "iron_bars")
            v.set(tx, 15, tz, M + "magma_block")
            v.set(tx, 16, tz, M + "fire")
    # skull gate (north)
    v.carve(-3, 1, -H - 1, 3, 7, -H + 2)
    v.fill(-5, 8, -H - 1, 5, 13, -H - 1, M + "bone_block[axis=y]")
    for x in (-3, -1, 1, 3):
        v.set(x, 10, -H - 2, WSKULL.replace("rotation=8", "rotation=8"))
    v.fill(-2, 11, -H - 2, -1, 11, -H - 2, M + "shroomlight")
    v.fill(1, 11, -H - 2, 2, 11, -H - 2, M + "shroomlight")
    # courtyard: warlord hall
    v.room(-7, 0, 3, 7, 10, 13, wall, M + "polished_blackstone", M + "blackstone")
    v.carve(-2, 1, 3, 2, 5, 3)
    v.fill(-1, 1, 11, 1, 3, 12, M + "gilded_blackstone")
    v.set(0, 4, 12, WSKULL)
    for x in (-6, 6):
        for z in (5, 8, 11):
            v.set(x, 2, z, SOUL_LANTERN)
    v.chest(-5, 1, 12, "north")
    v.chest(5, 1, 12, "north")
    for x in range(-5, 6, 2):
        v.set(x, 1, 7, M + "red_carpet")
    # banners of war: red/black wool hangings on the walls
    for x in range(-H + 3, H - 2, 6):
        v.fill(x, 5, -H + 2, x, 8, -H + 2, M + "red_wool")
    # the Maw: pit stairs down from the courtyard
    theme = {
        "wall": [(M + "blackstone", 3), (M + "basalt[axis=y]", 1), (M + "cracked_polished_blackstone_bricks", 1)],
        "floor": [(M + "soul_soil", 1), (M + "blackstone", 2)], "pillar": M + "polished_basalt[axis=y]",
        "accent": M + "red_nether_bricks", "core": M + "blackstone", "core_light": M + "magma_block",
        "lantern": "minecraft:soul_lantern", "web": 0.04, "idol": M + "crying_obsidian",
        "hall_decor": WSKULL,
        "feature": lambda v, x, y, z: (v.fill(x - 1, y - 1, z - 1, x + 1, y - 1, z + 1, M + "lava"),
                                       v.fill(x, y, z, x, y + 3, z, M + "iron_bars"),
                                       v.set(x, y + 4, z, CHAIN)),
    }
    dungeon(v, theme, cx=0, cz=-8, floor_y=-18, rooms=("prison", "armory", "altar"), shaft_top=1)
    shaft_frame(v, 0, -8, M + "iron_bars", M + "polished_blackstone_wall[up=true,north=none,south=none,east=none,west=none,waterlogged=false]",
                cap=WSKULL, open_side="south", height=2)
    return v


def blood_altar():
    v = V("blood-altar")
    v.fill(-3, 0, -3, 3, 0, 3, M + "red_nether_bricks")
    v.fill(-2, 1, -2, 2, 1, 2, M + "nether_bricks")
    v.fill(-1, 2, -1, 1, 2, 1, M + "crimson_nylium")
    v.set(0, 3, 0, SOUL_CAMPFIRE)
    for x, z in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        v.fill(x, 1, z, x, 4, z, M + "bone_block[axis=y]")
        v.set(x, 5, z, SKULL)
    v.sprinkle(-3, 1, -3, 3, 1, 3, M + "crimson_roots", 0.2, on={M + "red_nether_bricks"})
    return v


def bone_totem():
    v = V("bone-totem")
    for y in range(0, 10):
        v.set(0, y, 0, M + ("bone_block[axis=y]" if y % 3 else "red_nether_bricks"))
    v.set(-1, 6, 0, M + "bone_block[axis=x]")
    v.set(1, 6, 0, M + "bone_block[axis=x]")
    v.set(-2, 7, 0, M + "bone_block[axis=y]")
    v.set(2, 7, 0, M + "bone_block[axis=y]")
    v.set(0, 10, 0, WSKULL)
    v.set(0, 4, -1, M + "shroomlight")
    return v


# =============================================================================== DREADMIRE
def witch_hut():
    v = V("stilt-witch-hut")
    for x in (-3, 3):
        for z in (-3, 3):
            v.fill(x, -3, z, x, 3, z, M + "mangrove_log[axis=y]")
    v.fill(-3, 4, -3, 3, 4, 3, M + "mangrove_planks")
    v.walls(-3, 5, -3, 3, 8, 3, M + "dark_oak_planks")
    v.carve(-2, 5, -2, 2, 8, 2)
    v.carve(0, 5, -3, 0, 6, -3)
    v.set(-3, 6, 0, M + "glass_pane")
    v.set(3, 6, 0, M + "glass_pane")
    for i in range(0, 4):
        v.fill(-4 + i, 9 + i, -4 + i, 4 - i, 9 + i, 4 - i, M + "moss_block" if i % 2 else M + "dark_oak_planks")
    v.carve(-1, 9, -1, 1, 9, 1)
    v.set(-2, 5, 2, M + "cauldron")
    v.set(2, 5, 2, M + "brewing_stand[has_bottle_0=true,has_bottle_1=false,has_bottle_2=true]")
    v.chest(2, 5, -2, "south")
    v.set(-2, 5, -2, M + "crafting_table")
    v.set(0, 8, 0, HSOUL_LANTERN)
    v.set(0, 4, -4, M + "mangrove_planks")
    for y in range(0, 4):
        v.set(0, y, -5 + (0 if y < 0 else 0), None)
    for i, y in enumerate(range(3, -1, -1)):
        v.set(0, y, -5 - i, stair("mangrove", "south"))
    v.set(-3, 9, -4, HLANTERN)
    return v


def sunken_crypt():
    v = V("sunken-crypt")
    stone = v.pal([(M + "mossy_stone_bricks", 3), (M + "mossy_cobblestone", 2), (M + "cracked_stone_bricks", 1),
                   (M + "mud_bricks", 1)])
    v.fill(-5, 0, -7, 5, 0, 7, stone)
    v.walls(-4, 1, -6, 4, 6, 6, stone)
    v.carve(-3, 1, -5, 3, 6, 5)
    v.carve(-1, 1, -6, 1, 4, -6)
    for x in range(-5, 6):
        for z in range(-7, 8):
            y = 7 + (5 - abs(x)) // 2
            v.set(x, y, z, M + "mossy_stone_brick_slab[type=bottom,waterlogged=false]" if abs(x) == 5 else stone)
    for x in (-2, 2):
        v.fill(x, 1, -7, x, 5, -7, M + "chiseled_stone_bricks")
        v.set(x, 6, -8, HSOUL_LANTERN)
    v.set(0, 7, -7, WSKULL)
    theme = {
        "wall": [(M + "mossy_stone_bricks", 3), (M + "mud_bricks", 2), (M + "packed_mud", 1)],
        "floor": [(M + "mud", 1), (M + "mossy_cobblestone", 2)], "pillar": M + "mossy_stone_brick_wall[up=true,north=none,south=none,east=none,west=none,waterlogged=false]",
        "accent": M + "chiseled_stone_bricks", "core": M + "mossy_stone_bricks", "core_light": M + "ochre_froglight[axis=y]",
        "lantern": "minecraft:soul_lantern", "web": 0.08, "sarcophagus": M + "mossy_stone_bricks",
        "hall_decor": M + "moss_carpet",
        "feature": lambda v, x, y, z: (v.fill(x - 2, y - 1, z - 2, x + 2, y - 1, z + 2, M + "water"),
                                       v.set(x, y - 1, z, M + "mossy_stone_bricks"), v.set(x, y, z, SKULL)),
    }
    dungeon(v, theme, cx=0, cz=0, floor_y=-16, rooms=("crypt", "flooded", "treasure"), shaft_top=1)
    return v


def gibbet():
    v = V("hanging-gibbet")
    v.fill(0, 0, 0, 0, 7, 0, M + "dark_oak_log[axis=y]")
    v.fill(0, 7, 0, 3, 7, 0, M + "dark_oak_log[axis=x]")
    v.fill(3, 5, 0, 3, 6, 0, CHAIN)
    v.walls(2, 2, -1, 4, 4, 1, M + "iron_bars")
    v.set(3, 2, 0, SKULL)
    v.set(3, 1, 0, None)
    v.set(3, 5, 0, CHAIN)
    return v


def drowned_shrine():
    v = V("drowned-shrine")
    v.fill(-4, -1, -4, 4, 0, 4, M + "mossy_cobblestone")
    for x, z in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, -4), (0, 4)):
        v.fill(x, 1, z, x, 3 + (abs(x) + z) % 3, z, M + "mossy_stone_bricks")
    v.set(0, 1, 0, M + "mossy_stone_bricks")
    v.set(0, 2, 0, M + "sculk_catalyst")
    v.chest(1, 1, 0, "west")
    v.erode(0.25, lambda x, y, z: y > 2)
    return v


# =============================================================================== FRONTIER
def frontier_town():
    """Dust-blown boomtown: saloon, sheriff's jail, general store, bank and a water tower along one street."""
    v = V("frontier-town")
    road = v.pal([(M + "dirt_path", 3), (M + "coarse_dirt", 2), (M + "packed_mud", 1)])
    v.fill(-24, 0, -3, 24, 0, 3, road)
    plank = v.pal([(M + "spruce_planks", 3), (M + "oak_planks", 1)])
    lots = [(-19, "saloon"), (-7, "sheriff"), (5, "store"), (17, "bank")]
    for side, zsign in ((0, -1), (1, 1)):
        for i, (x, kind) in enumerate(lots):
            if (i + side) % 2:
                continue
            z0 = 4 if zsign > 0 else -14
            z1 = z0 + 10
            front = z0 if zsign > 0 else z1
            _western_building(v, x - 5, z0, x + 5, z1, front, kind, plank)
    # water tower
    for x in (-2, 2):
        for z in (-9, -5):
            v.fill(x + 22, 1, z, x + 22, 8, z, M + "spruce_log[axis=y]")
    v.cylinder(22, -7, 9, 13, 3, M + "spruce_planks", hollow=True)
    v.cylinder(22, -7, 9, 9, 3, M + "spruce_planks")
    v.cylinder(22, -7, 10, 12, 2.2, M + "water")
    v.cylinder(22, -7, 14, 14, 3.4, M + "dark_oak_slab[type=bottom,waterlogged=false]")
    # hitching posts, troughs, barrels
    for x in range(-22, 23, 6):
        v.set(x, 1, -3, M + "oak_fence")
        v.set(x, 1, 3, M + "oak_fence")
    v.fill(-2, 1, 2, 1, 1, 2, M + "cauldron")
    for x, z in ((-10, 2), (9, -2), (0, -2)):
        v.set(x, 1, z, M + "barrel[facing=up,open=false]")
    v.set(-24, 1, 0, M + "hay_block[axis=x]")
    v.set(24, 1, 1, M + "hay_block[axis=z]")
    # gallows at the west end
    v.fill(-26, 0, -2, -24, 0, 2, M + "spruce_planks")
    v.fill(-26, 1, 0, -26, 5, 0, M + "spruce_log[axis=y]")
    v.fill(-26, 5, 0, -24, 5, 0, M + "spruce_log[axis=x]")
    v.set(-24, 4, 0, CHAIN)
    return v


def _western_building(v, x0, z0, x1, z1, front, kind, plank):
    tall = kind in ("saloon", "bank")
    top = 9 if tall else 5
    v.fill(x0, 0, z0, x1, 0, z1, M + "spruce_planks")
    v.walls(x0, 1, z0, x1, top, z1, plank)
    for x in (x0, x1):
        for z in (z0, z1):
            v.fill(x, 1, z, x, top, z, M + "stripped_spruce_log[axis=y]")
    v.carve(x0 + 1, 1, z0 + 1, x1 - 1, top, z1 - 1)
    if tall:
        v.fill(x0 + 1, 5, z0 + 1, x1 - 1, 5, z1 - 1, plank)
        zz = (z0 + z1) // 2
        v.fill(x1 - 1, 1, zz, x1 - 1, 5, zz, M + "ladder[facing=west,waterlogged=false]")
        v.set(x0 + 2, 6, zz, M + "red_bed[facing=south,occupied=false,part=head]")
        v.set(x0 + 2, 6, zz + 1, M + "red_bed[facing=south,occupied=false,part=foot]")
    v.fill(x0, top + 1, z0, x1, top + 1, z1, M + "dark_oak_planks")
    # false front facade
    for x in range(x0, x1 + 1):
        for y in range(top + 1, top + 4):
            v.set(x, y, front, plank)
    v.fill(x0 + 2, top + 2, front, x1 - 2, top + 2, front, M + {"saloon": "red_terracotta", "sheriff": "yellow_terracotta",
                                                              "store": "light_blue_terracotta", "bank": "green_terracotta"}[kind])
    # porch with awning
    d = -1 if front == z0 else 1
    for x in range(x0, x1 + 1):
        v.set(x, 0, front + d, M + "spruce_planks")
        v.set(x, 4, front + d, M + "spruce_slab[type=bottom,waterlogged=false]")
        v.set(x, 4, front + 2 * d, M + "spruce_slab[type=bottom,waterlogged=false]")
    for x in (x0, x1):
        v.fill(x, 1, front + 2 * d, x, 3, front + 2 * d, M + "spruce_fence")
    mid = (x0 + x1) // 2
    v.carve(mid, 1, front, mid + 1, 2, front)  # saloon doors
    for x in (x0 + 2, x1 - 2):
        v.set(x, 2, front, M + "glass_pane")
    v.set(mid, 3, front + d, HLANTERN.replace("hanging=true", "hanging=true"))
    inner = z0 + 2 if front == z1 else z1 - 2
    if kind == "saloon":
        v.fill(x0 + 2, 1, inner, x1 - 2, 1, inner, M + "stripped_dark_oak_log[axis=x]")
        v.set(x0 + 2, 2, inner, M + "brewing_stand[has_bottle_0=true,has_bottle_1=true,has_bottle_2=false]")
        for x in (x0 + 3, x1 - 3):
            v.set(x, 1, (z0 + z1) // 2, M + "oak_fence")
            v.set(x, 2, (z0 + z1) // 2, M + "oak_pressure_plate[powered=false]")
        v.chest(x1 - 1, 1, inner, "north" if front == z1 else "south")
    elif kind == "sheriff":
        v.fill(x0 + 1, 1, inner, x0 + 4, 3, inner, M + "iron_bars")
        v.set(x1 - 2, 1, inner, M + "lectern[facing=north,has_book=false,powered=false]")
        v.chest(x1 - 1, 1, inner, "north" if front == z1 else "south")
    elif kind == "store":
        for x in range(x0 + 1, x1):
            v.set(x, 1, inner, M + "barrel[facing=up,open=false]")
            v.set(x, 2, inner, M + "barrel[facing=up,open=false]") if x % 2 else None
        v.chest(mid, 1, (z0 + z1) // 2, "north")
    elif kind == "bank":
        v.walls(x0 + 2, 1, inner - 1, x0 + 5, 3, inner + 1, M + "iron_block")
        v.carve(x0 + 3, 1, inner, x0 + 4, 2, inner)
        v.chest(x0 + 3, 1, inner, "north" if front == z1 else "south")
        v.chest(x0 + 4, 1, inner, "north" if front == z1 else "south")
    v.set(mid, top - 1, (z0 + z1) // 2, HLANTERN)


def abandoned_mine():
    """Timber mine adit into a hillside; tracks lead down to the flooded galleries of the Deepvein Lode."""
    v = V("abandoned-mine")
    beam = M + "stripped_oak_log[axis=y]"
    v.fill(-4, 0, -4, 4, 0, 2, v.pal([(M + "gravel", 1), (M + "coarse_dirt", 2)]))
    for x in (-2, 2):
        v.fill(x, 1, -2, x, 4, -2, beam)
    v.fill(-2, 5, -2, 2, 5, -2, M + "stripped_oak_log[axis=x]")
    v.set(-3, 1, -3, M + "barrel[facing=up,open=false]")
    v.set(3, 1, -3, M + "tnt[unstable=false]")
    # descending adit with rails
    y = 0
    z = -1
    for i in range(18):
        for x in (-1, 0, 1):
            v.set(x, y - 1, z, M + "cobblestone")
            v.carve(x, y, z, x, y + 3, z)
        v.set(0, y, z, S("rail", shape="ascending_north", waterlogged="false") if i > 0 else S("rail", shape="north_south", waterlogged="false"))
        if i % 4 == 0:
            v.fill(-2, y - 1, z, -2, y + 3, z, beam)
            v.fill(2, y - 1, z, 2, y + 3, z, beam)
            v.fill(-2, y + 4, z, 2, y + 4, z, M + "stripped_oak_log[axis=x]")
            v.set(-1, y + 3, z, HLANTERN)
        else:
            for x in (-2, 2):
                v.fill(x, y - 1, z, x, y + 3, z, M + "stone")
            v.fill(-1, y + 4, z, 1, y + 4, z, M + "stone")
        y -= 1
        z += 1
    theme = {
        "wall": [(M + "stone", 4), (M + "andesite", 1), (M + "tuff", 1), (M + "iron_ore", 1), (M + "gold_ore", 1),
                 (M + "coal_ore", 1)],
        "floor": [(M + "gravel", 1), (M + "cobblestone", 2)], "pillar": M + "stripped_oak_log[axis=y]",
        "accent": M + "oak_planks", "core": M + "stripped_oak_log[axis=y]", "core_light": M + "redstone_lamp[lit=true]",
        "lantern": "minecraft:lantern", "web": 0.12, "riches": [M + "raw_gold_block", M + "raw_iron_block"],
        "feature": lambda v, x, y, z: (v.fill(x - 1, y, z - 1, x + 1, y, z + 1, M + "raw_iron_block"),
                                       v.set(x, y + 1, z, M + "raw_gold_block")),
        "hall_decor": M + "barrel[facing=up,open=false]", "shaft_lights": False,
    }
    dungeon(v, theme, cx=0, cz=z + 2, floor_y=y - 12, rooms=("forge", "treasure", "flooded"), shaft_top=y)
    v.carve(-1, y, z - 1, 1, y + 3, z - 1)
    return v


def bandit_fort():
    v = V("bandit-fort")
    log = v.pal([(M + "spruce_log[axis=y]", 3), (M + "oak_log[axis=y]", 1)])
    v.fill(-9, 0, -9, 9, 0, 9, M + "coarse_dirt")
    for i in range(-9, 10):
        for x, z in ((i, -9), (i, 9), (-9, i), (9, i)):
            if not (x == 0 and z == 9) and not (abs(x) <= 1 and z == 9):
                v.fill(x, 1, z, x, 4 + (i % 2), z, log)
    v.fill(4, 1, 4, 7, 10, 7, M + "spruce_planks")
    v.carve(5, 1, 5, 6, 10, 6)
    v.fill(3, 11, 3, 8, 11, 8, M + "spruce_planks")
    v.walls(3, 12, 3, 8, 12, 8, M + "spruce_fence")
    v.fill(5, 1, 5, 5, 11, 5, M + "ladder[facing=east,waterlogged=false]")
    v.set(5, 11, 5, VA)
    v.set(8, 13, 8, LANTERN)
    v.fill(-7, 1, -7, -3, 1, -5, M + "hay_block[axis=x]")
    v.chest(-7, 1, 7, "east")
    v.chest(-6, 1, 7, "north")
    v.set(0, 1, 0, CAMPFIRE)
    v.set(-8, 1, 0, M + "tnt[unstable=false]")
    v.set(-8, 2, 0, M + "tnt[unstable=false]")
    return v


def sun_oracle():
    """Sandstone oracle shrine with a golden sun disc; the Vault of Noon lies beneath."""
    v = V("sun-oracle")
    sand = v.pal([(M + "cut_sandstone", 3), (M + "smooth_sandstone", 2), (M + "chiseled_sandstone", 1)])
    v.fill(-6, 0, -6, 6, 0, 6, sand)
    for x, z in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
        v.fill(x, 1, z, x, 7, z, M + "cut_red_sandstone")
        v.set(x, 8, z, M + "orange_glazed_terracotta[facing=north]")
    v.fill(-5, 8, -5, 5, 8, 5, sand)
    v.carve(-4, 8, -4, 4, 8, 4)
    v.fill(-4, 8, -4, 4, 8, -4, sand)
    v.fill(-4, 8, 4, 4, 8, 4, sand)
    # golden sun disc facing north
    for x in range(-3, 4):
        for y in range(10, 17):
            if math.hypot(x, y - 13) <= 3.2:
                v.set(x, y, 0, M + ("gold_block" if math.hypot(x, y - 13) <= 1.5 else "raw_gold_block"))
    theme = {
        "wall": [(M + "smooth_sandstone", 3), (M + "cut_sandstone", 2), (M + "sandstone", 1)],
        "floor": [(M + "smooth_red_sandstone", 1), (M + "cut_red_sandstone", 1)],
        "pillar": M + "chiseled_red_sandstone", "accent": M + "orange_terracotta", "core": M + "smooth_sandstone",
        "core_light": M + "glowstone", "lantern": "minecraft:lantern", "web": 0.03,
        "riches": [M + "gold_block", M + "raw_gold_block"], "idol": M + "gold_block",
        "sarcophagus": M + "chiseled_sandstone",
    }
    dungeon(v, theme, cx=0, cz=-3, floor_y=-15, rooms=("crypt", "treasure", "shrine"), shaft_top=1)
    shaft_frame(v, 0, -3, M + "cut_sandstone_slab[type=bottom,waterlogged=false]", M + "cut_red_sandstone",
                cap=M + "orange_glazed_terracotta[facing=north]", open_side="north", height=2)
    return v


def cattle_skull_marker():
    v = V("longhorn-marker")
    v.fill(0, 0, 0, 0, 3, 0, M + "spruce_fence")
    v.set(0, 4, 0, SKULL)
    v.set(-1, 4, 0, M + "bone_block[axis=x]")
    v.set(1, 4, 0, M + "bone_block[axis=x]")
    v.set(-2, 5, 0, M + "bone_block[axis=y]")
    v.set(2, 5, 0, M + "bone_block[axis=y]")
    return v


# =============================================================================== EVERBLOOM
def mage_tower():
    """Violet-roofed spire of the Everbloom Conclave. Stairs spiral to the observatory; an arcane vault lies below."""
    v = V("mage-tower")
    stone = v.pal([(M + "stone_bricks", 3), (M + "mossy_stone_bricks", 1), (M + "calcite", 1)])
    v.cylinder(0, 0, 0, 0, 7, M + "polished_deepslate")
    v.cylinder(0, 0, 1, 26, 5, stone, hollow=True, thickness=1.2)
    v.cylinder(0, 0, 1, 26, 3.8, VA)
    for y in (8, 14, 20):
        v.cylinder(0, 0, y, y, 4.2, M + "spruce_planks")
        v.cylinder(0, 0, y, y, 1.2, VA)
    # spiral stair hugging the wall
    for i in range(0, 26):
        a = i * 30
        x, z = round(3.2 * math.cos(math.radians(a))), round(3.2 * math.sin(math.radians(a)))
        v.set(x, i + 1, z, M + "polished_deepslate")
        for h in range(1, 3):
            if v.get(x, i + 1 + h, z) == M + "spruce_planks":
                v.set(x, i + 1 + h, z, VA)
    # windows with stained glass
    for y in (4, 11, 17, 23):
        for a in range(0, 360, 90):
            x, z = round(5 * math.cos(math.radians(a + y * 7))), round(5 * math.sin(math.radians(a + y * 7)))
            v.set(x, y, z, M + "purple_stained_glass")
            v.set(x, y + 1, z, M + "magenta_stained_glass")
    v.carve(0, 1, -5, 0, 3, -5)
    # conical violet roof
    for i in range(0, 12):
        r = 6.5 - i * 0.55
        v.cylinder(0, 0, 27 + i, 27 + i, max(r, 0.4), M + "purple_terracotta" if i % 3 else M + "amethyst_block", hollow=True, thickness=1.2)
    v.set(0, 39, 0, M + "end_rod[facing=up]")
    v.set(0, 40, 0, M + "amethyst_cluster[facing=up,waterlogged=false]")
    # library, alchemy, enchanting floors
    for a in range(0, 360, 40):
        x, z = round(3.6 * math.cos(math.radians(a))), round(3.6 * math.sin(math.radians(a)))
        v.set(x, 9, z, M + "bookshelf")
        v.set(x, 10, z, M + "bookshelf")
    v.set(0, 15, 0, M + "brewing_stand[has_bottle_0=true,has_bottle_1=true,has_bottle_2=true]")
    v.set(1, 15, 0, M + "cauldron")
    v.set(0, 21, 0, M + "enchanting_table")
    v.chest(-2, 21, 0, "east")
    v.set(0, 25, 0, M + "amethyst_block")
    v.set(0, 24, 0, S("end_rod", facing="down"))
    theme = {
        "wall": [(M + "deepslate_tiles", 3), (M + "polished_deepslate", 2), (M + "calcite", 1)],
        "floor": M + "polished_deepslate", "pillar": M + "amethyst_block", "accent": M + "purpur_block",
        "core": M + "calcite", "core_light": M + "pearlescent_froglight[axis=y]", "lantern": "minecraft:soul_lantern",
        "web": 0.0, "idol": M + "amethyst_block",
        "feature": lambda v, x, y, z: (v.set(x, y, z, M + "lodestone"), v.set(x, y + 1, z, M + "end_rod[facing=up]"),
                                       v.set(x, y + 2, z, M + "amethyst_cluster[facing=up,waterlogged=false]")),
        "hall_decor": M + "amethyst_cluster[facing=up,waterlogged=false]",
    }
    # vault annex on the south side of the tower, enclosing the stair shaft
    v.room(-3, 0, 4, 3, 6, 14, stone, M + "polished_deepslate", M + "purple_terracotta")
    v.carve(-1, 1, 3, 1, 3, 6)
    for x in (-3, 3):
        v.set(x, 3, 10, M + "purple_stained_glass")
    v.set(0, 5, 6, HSOUL_LANTERN)
    dungeon(v, theme, cx=0, cz=10, floor_y=-14, rooms=("library", "treasure", "shrine"), shaft_top=1)
    return v


def fairy_ring():
    v = V("fairy-ring")
    for a in range(0, 360, 20):
        x, z = round(6 * math.cos(math.radians(a))), round(6 * math.sin(math.radians(a)))
        v.set(x, 0, z, M + "moss_block")
        v.set(x, 1, z, M + ("red_mushroom" if a % 40 else "brown_mushroom"))
    for a in range(10, 360, 40):
        x, z = round(5 * math.cos(math.radians(a))), round(5 * math.sin(math.radians(a)))
        v.set(x, -1, z, M + "shroomlight")
        v.set(x, 0, z, M + "moss_block")
        v.set(x, 1, z, M + "pink_petals[facing=north,flower_amount=4]")
    v.set(0, 0, 0, M + "moss_block")
    v.set(0, 1, 0, M + "flowering_azalea")
    return v


def moonwell():
    v = V("moonwell")
    v.cylinder(0, 0, 0, 0, 5, M + "calcite")
    v.cylinder(0, 0, 0, 0, 3.5, M + "water")
    v.cylinder(0, 0, -2, -1, 3.5, M + "calcite")
    v.set(0, -1, 0, M + "sea_lantern")
    for a in range(0, 360, 60):
        x, z = round(5 * math.cos(math.radians(a))), round(5 * math.sin(math.radians(a)))
        v.fill(x, 1, z, x, 4, z, M + "quartz_pillar[axis=y]")
        v.set(x, 5, z, M + "amethyst_cluster[facing=up,waterlogged=false]")
    return v


def arcane_henge():
    v = V("arcane-henge")
    for a in range(0, 360, 30):
        x, z = round(9 * math.cos(math.radians(a))), round(9 * math.sin(math.radians(a)))
        h = 4 + (a // 30) % 3
        v.fill(x, 0, z, x, h, z, M + ("mossy_cobblestone" if a % 60 else "deepslate_bricks"))
        if a % 90 == 0:
            v.set(x, h + 1, z, M + "amethyst_block")
    v.fill(-1, 0, -1, 1, 1, 1, M + "polished_deepslate")
    v.set(0, 2, 0, M + "amethyst_cluster[facing=up,waterlogged=false]")
    return v


# =============================================================================== CROWNLANDS
def market_crossroads():
    v = V("market-crossroads")
    road = v.pal([(M + "stone_bricks", 3), (M + "cobblestone", 2), (M + "andesite", 1), (M + "mossy_cobblestone", 1)])
    v.fill(-16, 0, -2, 16, 0, 2, road)
    v.fill(-2, 0, -16, 2, 0, 16, road)
    v.cylinder(0, 0, 0, 0, 5, road)
    # the well
    v.cylinder(0, 0, 0, 1, 2, M + "stone_bricks", hollow=True)
    v.cylinder(0, 0, -3, 0, 1.2, M + "water")
    for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        v.fill(x, 2, z, x, 4, z, M + "oak_fence")
    v.fill(-2, 5, -2, 2, 5, 2, M + "spruce_slab[type=bottom,waterlogged=false]")
    v.set(0, 4, 0, HLANTERN)
    # market stalls
    colors = ["red", "yellow", "blue", "green", "orange", "purple", "cyan", "lime"]
    spots = [(-10, -6), (-5, -6), (5, -6), (10, -6), (-10, 6), (-5, 6), (5, 6), (10, 6)]
    for (sx, sz), c in zip(spots, colors):
        for x in (sx - 1, sx + 1):
            for z in (sz - 1, sz + 1):
                v.fill(x, 1, z, x, 3, z, M + "oak_fence")
        for x in range(sx - 2, sx + 3):
            for z in range(sz - 1, sz + 2):
                v.set(x, 4, z, M + (f"{c}_wool" if (x + z) % 2 == 0 else "white_wool"))
        counter = sz + (1 if sz < 0 else -1)
        v.fill(sx - 1, 1, counter, sx + 1, 1, counter, M + "spruce_planks")
        v.set(sx, 2, counter, M + ["barrel[facing=up,open=false]", "composter[level=7]", "cauldron", "loom[facing=north]",
                                   "fletching_table", "smoker[facing=north,lit=false]", "stonecutter[facing=north]",
                                   "cartography_table"][colors.index(c)])
        v.chest(sx, 1, sz, "north" if sz > 0 else "south")
    # lamp posts and signposts
    for x, z in ((-7, 0), (7, 0), (0, -7), (0, 7)):
        v.fill(x, 1, z, x, 3, z, M + "dark_oak_fence")
        v.set(x, 4, z, LANTERN)
    for x, z in ((-15, -3), (15, 3)):
        v.fill(x, 1, z, x, 2, z, M + "hay_block[axis=y]")
    return v


def watchtower():
    v = V("crown-watchtower")
    stone = v.pal([(M + "stone_bricks", 4), (M + "cobblestone", 1), (M + "andesite", 1)])
    v.fill(-3, 0, -3, 3, 16, 3, stone)
    v.carve(-2, 1, -2, 2, 16, 2)
    for y in (6, 11):
        v.fill(-2, y, -2, 2, y, 2, M + "spruce_planks")
        v.set(2, y, 2, VA)
    v.fill(2, 1, 2, 2, 16, 2, M + "ladder[facing=north,waterlogged=false]")
    v.carve(0, 1, -3, 0, 2, -3)
    v.fill(-4, 17, -4, 4, 17, 4, stone)
    for i in range(-4, 5, 2):
        for x, z in ((i, -4), (i, 4), (-4, i), (4, i)):
            v.set(x, 18, z, stone)
    v.set(2, 17, 2, VA)
    v.set(-3, 18, -3, CAMPFIRE)
    for y in (4, 9, 14):
        for x, z in ((0, -3), (0, 3), (-3, 0), (3, 0)):
            v.set(x, y, z, M + "glass_pane")
    v.fill(-4, 12, -4, -4, 15, -4, M + "blue_wool")
    v.fill(4, 12, 4, 4, 15, 4, M + "yellow_wool")
    v.chest(-2, 12, -2, "south")
    return v


def windmill():
    v = V("windmill")
    v.cylinder(0, 0, 0, 12, 3.5, M + "stone_bricks", hollow=True)
    v.cylinder(0, 0, 0, 0, 3.5, M + "oak_planks")
    v.cylinder(0, 0, 1, 12, 2.3, VA)
    for i in range(0, 5):
        v.cylinder(0, 0, 13 + i, 13 + i, 4 - i * 0.9, M + "spruce_planks")
    v.fill(0, 11, -4, 0, 11, -5, M + "stripped_oak_log[axis=z]")
    for L in range(1, 9):
        for dx, dy in ((L, 0), (-L, 0), (0, L), (0, -L)):
            v.set(dx, 11 + dy, -5, M + "stripped_spruce_log[axis=x]" if dy == 0 else M + "stripped_spruce_log[axis=y]")
            if L > 2:
                ox, oy = (0, 1) if dy == 0 else (1, 0)
                v.set(dx + ox, 11 + dy + oy, -5, M + "white_wool")
    v.carve(0, 1, -4, 0, 2, -3)
    v.set(0, 1, 0, M + "grindstone[face=floor,facing=north]")
    v.fill(-1, 1, 1, 1, 1, 2, M + "hay_block[axis=x]")
    v.chest(1, 1, -1, "west")
    return v


def castle_keep():
    """Crownland keep with curtain walls, gatehouse and a vaulted undercroft treasury."""
    v = V("castle-keep")
    stone = v.pal([(M + "stone_bricks", 5), (M + "cracked_stone_bricks", 1), (M + "andesite", 1), (M + "polished_andesite", 1)])
    H = 16
    v.fill(-H, 0, -H, H, 0, H, M + "cobblestone")
    v.walls(-H, 1, -H, H, 8, H, stone)
    for i in range(-H, H + 1, 2):
        for x, z in ((i, -H), (i, H), (-H, i), (H, i)):
            v.set(x, 9, z, stone)
    for tx in (-H, H):
        for tz in (-H, H):
            v.cylinder(tx, tz, 0, 12, 3, stone)
            v.cylinder(tx, tz, 1, 11, 1.8, VA)
            v.cone(tx, tz, 13, 4, 6, M + "blue_terracotta")
    # gatehouse
    v.fill(-4, 0, -H - 2, 4, 12, -H + 2, stone)
    v.carve(-2, 1, -H - 2, 2, 5, -H + 2)
    v.fill(-2, 5, -H - 1, 2, 5, -H - 1, M + "iron_bars")
    for x in (-4, 4):
        v.fill(x, 8, -H - 3, x, 11, -H - 3, M + "red_wool")
    # keep
    v.fill(-6, 0, 0, 6, 0, 12, stone)
    v.walls(-6, 1, 0, 6, 18, 12, stone)
    v.carve(-5, 1, 1, 5, 18, 11)
    for y in (6, 12):
        v.fill(-5, y, 1, 5, y, 11, M + "spruce_planks")
        v.set(4, y, 10, VA)
    v.fill(4, 1, 10, 4, 18, 10, M + "ladder[facing=west,waterlogged=false]")
    v.fill(-6, 19, 0, 6, 19, 12, stone)
    for x in range(-6, 7, 2):
        v.set(x, 20, 0, stone)
        v.set(x, 20, 12, stone)
    v.carve(-1, 1, 0, 1, 3, 0)
    v.fill(-2, 1, 9, 2, 1, 11, M + "red_carpet")
    v.set(0, 1, 11, M + "gold_block")
    v.set(0, 2, 11, stair("oak", "north"))
    for y in (4, 10, 16):
        for x in (-6, 6):
            v.set(x, y, 6, M + "glass_pane")
    v.fill(-5, 7, 11, 5, 9, 11, M + "bookshelf")
    v.chest(-4, 13, 10, "south")
    v.set(0, 19, 6, M + "blue_wool")
    v.fill(0, 20, 6, 0, 24, 6, M + "oak_fence")
    v.fill(0, 22, 7, 0, 24, 9, M + "blue_wool")
    v.set(0, 23, 8, M + "yellow_wool")
    theme = {
        "wall": [(M + "stone_bricks", 3), (M + "cracked_stone_bricks", 1), (M + "cobblestone", 1)],
        "floor": M + "polished_andesite", "pillar": M + "stone_brick_wall[up=true,north=none,south=none,east=none,west=none,waterlogged=false]",
        "accent": M + "chiseled_stone_bricks", "core": M + "stone_bricks", "core_light": M + "glowstone",
        "lantern": "minecraft:lantern", "web": 0.04,
    }
    dungeon(v, theme, cx=-3, cz=5, floor_y=-13, rooms=("treasure", "armory", "prison"), shaft_top=1)
    return v


def lighthouse():
    v = V("lighthouse")
    for y in range(0, 22):
        c = M + ("white_terracotta" if (y // 4) % 2 == 0 else "red_terracotta")
        v.cylinder(0, 0, y, y, 3.2 - y * 0.04, c, hollow=True)
    v.cylinder(0, 0, 0, 0, 3.2, M + "stone_bricks")
    v.cylinder(0, 0, 1, 21, 2.1, VA)
    v.fill(0, 1, 2, 0, 21, 2, M + "ladder[facing=north,waterlogged=false]")
    v.carve(0, 1, -3, 0, 2, -3)
    v.cylinder(0, 0, 22, 22, 4.2, M + "stone_bricks")
    v.cylinder(0, 0, 23, 23, 4.2, M + "iron_bars", hollow=True)
    v.cylinder(0, 0, 23, 26, 1.5, M + "glass")
    v.fill(0, 23, 0, 0, 25, 0, M + "sea_lantern")
    v.cone(0, 0, 27, 3, 4, M + "red_nether_bricks")
    v.set(0, 22, 2, VA)
    return v


# =============================================================================== WARSCAR MARCHES
def ruined_keep():
    """Shattered keep of the Broken Oath. The siege vaults beneath were never breached."""
    v = V("ruined-keep")
    stone = v.pal([(M + "cracked_stone_bricks", 3), (M + "stone_bricks", 2), (M + "cobblestone", 2),
                   (M + "blackstone", 1), (M + "tuff_bricks", 1)])
    v.fill(-11, 0, -11, 11, 0, 11, v.pal([(M + "cobblestone", 2), (M + "gravel", 1), (M + "coarse_dirt", 1)]))
    v.walls(-11, 1, -11, 11, 12, 11, stone)
    v.walls(-10, 1, -10, 10, 12, 10, stone)
    v.cylinder(-11, -11, 0, 18, 3, stone)
    v.cylinder(-11, -11, 1, 17, 1.8, VA)
    v.carve(-2, 1, -11, 2, 5, -10)
    v.erode(0.5, lambda x, y, z: y > 3 + (abs(x * 7 + z * 3) % 6))
    v.erode(0.4, lambda x, y, z: y > 6)
    # scorch marks and debris
    v.sprinkle(-9, 1, -9, 9, 1, 9, M + "cobblestone_slab[type=bottom,waterlogged=false]", 0.05)
    v.sprinkle(-9, 1, -9, 9, 1, 9, M + "soul_campfire[facing=north,lit=false,signal_fire=false,waterlogged=false]", 0.01)
    v.sprinkle(-9, 1, -9, 9, 1, 9, SKULL, 0.01)
    v.fill(5, 1, 5, 5, 2, 5, M + "dark_oak_fence")
    v.set(5, 3, 5, M + "red_wool")
    theme = {
        "wall": [(M + "stone_bricks", 2), (M + "cracked_stone_bricks", 2), (M + "tuff_bricks", 1)],
        "floor": [(M + "cobblestone", 2), (M + "gravel", 1)], "pillar": M + "polished_tuff",
        "accent": M + "chiseled_tuff_bricks", "core": M + "tuff_bricks", "core_light": M + "glowstone",
        "lantern": "minecraft:lantern", "web": 0.07,
        "feature": lambda v, x, y, z: (v.fill(x - 1, y, z - 1, x + 1, y, z + 1, M + "stone_brick_slab[type=bottom,waterlogged=false]"),
                                       v.set(x, y, z, M + "lodestone"),
                                       v.set(x, y + 1, z, M + "iron_block")),
    }
    dungeon(v, theme, cx=0, cz=0, floor_y=-15, rooms=("armory", "treasure", "crypt"), shaft_top=1)
    shaft_frame(v, 0, 0, M + "cobblestone_slab[type=bottom,waterlogged=false]", M + "cracked_stone_bricks",
                open_side="north", height=2)
    return v


def broken_trebuchet():
    v = V("broken-trebuchet")
    for x in (-3, 3):
        v.fill(x, 0, -4, x, 0, 4, M + "dark_oak_log[axis=z]")
        v.line(x, 1, -3, x, 7, 0, M + "dark_oak_log[axis=y]")
        v.line(x, 1, 3, x, 7, 0, M + "dark_oak_log[axis=y]")
    v.fill(-3, 7, 0, 3, 7, 0, M + "stripped_dark_oak_log[axis=x]")
    v.line(0, 7, 0, 0, 1, -9, M + "dark_oak_log[axis=z]")
    v.fill(-1, 1, 5, 1, 2, 6, M + "cobblestone")
    v.set(0, 1, -10, M + "cobblestone")
    v.set(2, 1, -6, M + "dark_oak_slab[type=bottom,waterlogged=false]")
    v.set(-4, 1, 2, M + "dark_oak_slab[type=bottom,waterlogged=false]")
    return v


def war_graves():
    v = V("war-graves")
    for gx in range(-8, 9, 4):
        for gz in range(-6, 7, 4):
            if v.rng.random() < 0.8:
                kind = v.rng.random()
                if kind < 0.5:
                    v.fill(gx, 1, gz, gx, 2, gz, M + "cobblestone_wall[up=true,north=none,south=none,east=none,west=none,waterlogged=false]")
                    v.set(gx, 3, gz, M + "stone_brick_wall[up=true,north=none,south=none,east=none,west=none,waterlogged=false]")
                elif kind < 0.8:
                    v.fill(gx, 1, gz, gx, 2, gz, M + "dark_oak_fence")
                    v.set(gx, 3, gz, SKULL)
                else:
                    v.fill(gx, 1, gz, gx, 1, gz + 1, M + "coarse_dirt")
                    v.set(gx, 2, gz, M + "stone_brick_slab[type=bottom,waterlogged=false]")
            v.set(gx, 0, gz + 1, M + "coarse_dirt")
            v.set(gx, 0, gz + 2, M + "podzol")
    v.fill(-10, 1, -8, -10, 5, -8, M + "dark_oak_fence")
    v.fill(-10, 3, -7, -10, 5, -7, M + "black_wool")
    v.fill(-10, 3, -6, -10, 4, -6, M + "red_wool")
    return v


def burned_house():
    v = V("burned-house")
    v.fill(-4, 0, -3, 4, 0, 3, M + "cobblestone")
    wall = v.pal([(M + "blackstone", 2), (M + "stripped_dark_oak_log[axis=y]", 2), (M + "cobblestone", 1)])
    v.walls(-4, 1, -3, 4, 4, 3, wall)
    v.carve(-3, 1, -2, 3, 4, 2)
    v.erode(0.55, lambda x, y, z: y > 1)
    v.sprinkle(-3, 1, -2, 3, 1, 2, M + "campfire[facing=north,lit=false,signal_fire=false,waterlogged=false]", 0.04)
    v.chest(3, 1, 2, "north")
    return v


# =============================================================================== UMBRAL PEAKS
def gothic_cathedral():
    """The Hollow Cathedral: a ruined gothic nave of the drowned sun-god; the Ossuary Catacombs lie below."""
    v = V("hollow-cathedral")
    stone = v.pal([(M + "deepslate_bricks", 4), (M + "cracked_deepslate_bricks", 2), (M + "deepslate_tiles", 1),
                   (M + "polished_blackstone_bricks", 1)])
    L, W, H = 22, 8, 20
    v.fill(-W - 1, 0, -L, W + 1, 0, L, M + "polished_deepslate")
    v.walls(-W, 1, -L, W, H, L, stone)
    v.carve(-W + 1, 1, -L + 1, W - 1, H + 6, L - 1)
    # buttresses and lancet windows
    for z in range(-L + 3, L - 2, 5):
        for x in (-W - 1, W + 1):
            v.fill(x, 1, z, x, H - 4, z, stone)
            v.set(x + (1 if x > 0 else -1), 1, z, stone)
        for x in (-W, W):
            for y in range(4, H - 3):
                c = M + ("red_stained_glass" if y % 5 == 0 else "purple_stained_glass" if y % 3 else "black_stained_glass")
                v.set(x, y, z + 1, c)
                v.set(x, y, z + 2, c)
    # pointed vault roof
    for x in range(-W, W + 1):
        y = H + (W - abs(x))
        for z in range(-L, L + 1):
            v.set(x, y, z, stone)
    # bell tower at the west end (north)
    v.fill(-4, 0, -L - 8, 4, H + 14, -L, stone)
    v.carve(-3, 1, -L - 7, 3, H + 14, -L + 1)
    v.carve(-2, 1, -L - 8, 2, 7, -L - 8)
    v.set(0, H + 11, -L - 4, M + "bell[attachment=ceiling,facing=north,powered=false]")
    v.set(0, H + 12, -L - 4, M + "dark_oak_planks")
    v.cone(0, -L - 4, H + 15, 5, 10, M + "deepslate_tiles")
    # rose window
    for x in range(-4, 5):
        for y in range(10, 19):
            d = math.hypot(x, y - 14)
            if d <= 4.2:
                v.set(x, y, L, M + ("red_stained_glass" if d < 1.5 else "black_stained_glass" if d > 3.4 else "magenta_stained_glass"))
    # altar, pews
    v.fill(-3, 1, L - 5, 3, 1, L - 2, M + "polished_blackstone")
    v.fill(-1, 2, L - 3, 1, 2, L - 3, M + "gilded_blackstone")
    v.set(0, 3, L - 3, WSKULL)
    for x in (-3, 3):
        v.set(x, 2, L - 4, M + "soul_campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    for z in range(-L + 4, L - 7, 2):
        for x in list(range(-6, -1)) + list(range(2, 7)):
            if v.rng.random() < 0.8:
                v.set(x, 1, z, stair("dark_oak", "south"))
    for z in range(-L + 3, L - 2, 5):
        for x in (-W + 1, W - 1):
            v.fill(x, 1, z, x, H - 1, z, M + "polished_deepslate")
            v.set(x + (1 if x < 0 else -1), H - 4, z, HSOUL_LANTERN)
    v.erode(0.55, lambda x, y, z: y > H - 2 and (z * 13 + x * 7) % 11 < 6)
    v.erode(0.25, lambda x, y, z: y > 10 and z > 5)
    theme = {
        "wall": [(M + "deepslate_bricks", 3), (M + "cracked_deepslate_bricks", 2), (M + "sculk", 1)],
        "floor": [(M + "deepslate_tiles", 2), (M + "cracked_deepslate_tiles", 1)],
        "pillar": M + "polished_deepslate", "accent": M + "chiseled_deepslate", "core": M + "deepslate_bricks",
        "core_light": M + "verdant_froglight[axis=y]", "lantern": "minecraft:soul_lantern", "web": 0.1,
        "idol": M + "sculk_shrieker[can_summon=false,shrieking=false,waterlogged=false]",
        "sarcophagus": M + "polished_blackstone", "hall_decor": WSKULL,
        "feature": lambda v, x, y, z: (v.fill(x - 1, y, z - 1, x + 1, y, z + 1, M + "bone_block[axis=y]"),
                                       v.set(x, y + 1, z, M + "sculk_catalyst"), v.set(x, y + 2, z, WSKULL)),
    }
    dungeon(v, theme, cx=0, cz=L - 10, floor_y=-20, rooms=("crypt", "altar", "library"), shaft_top=1, hall_half=7)
    return v


def necropolis_gate():
    v = V("necropolis-gate")
    stone = v.pal([(M + "deepslate_bricks", 3), (M + "polished_blackstone_bricks", 2), (M + "cracked_deepslate_bricks", 1)])
    v.fill(-6, 0, -6, 6, 0, 6, M + "deepslate_tiles")
    for x in (-5, 5):
        v.fill(x, 1, -5, x, 12, -3, stone)
        v.set(x, 13, -4, WSKULL)
    v.fill(-5, 10, -5, 5, 12, -3, stone)
    v.carve(-4, 1, -5, 4, 9, -3)
    for x in range(-3, 4):
        v.set(x, 9, -4, M + "iron_bars")
    v.fill(-2, 12, -6, 2, 12, -6, M + "bone_block[axis=x]")
    v.set(0, 11, -6, SOUL_LANTERN.replace("hanging=false", "hanging=true"))
    theme = {
        "wall": [(M + "deepslate_bricks", 3), (M + "sculk", 1), (M + "cracked_deepslate_bricks", 1)],
        "floor": M + "deepslate_tiles", "pillar": M + "bone_block[axis=y]", "accent": M + "chiseled_deepslate",
        "core": M + "deepslate_bricks", "core_light": M + "verdant_froglight[axis=y]",
        "lantern": "minecraft:soul_lantern", "web": 0.12, "hall_decor": WSKULL, "sarcophagus": M + "polished_basalt[axis=x]",
    }
    dungeon(v, theme, cx=0, cz=0, floor_y=-18, rooms=("crypt", "crypt", "treasure"), shaft_top=1)
    return v


def soulfire_obelisk():
    v = V("soulfire-obelisk")
    v.fill(-2, 0, -2, 2, 0, 2, M + "polished_blackstone")
    for y in range(1, 13):
        r = 1 if y < 10 else 0
        v.fill(-r, y, -r, r, y, r, M + ("polished_blackstone_bricks" if y % 4 else "gilded_blackstone"))
    v.set(0, 13, 0, SOUL_CAMPFIRE)
    for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        v.set(x, 1, z, SOUL_LANTERN)
    return v


def gibbet_cage():
    v = V("gibbet-cage")
    v.fill(0, 0, 0, 0, 9, 0, M + "dark_oak_log[axis=y]")
    v.fill(0, 9, 0, 3, 9, 0, M + "dark_oak_log[axis=x]")
    v.fill(3, 7, 0, 3, 8, 0, CHAIN)
    v.walls(2, 4, -1, 4, 6, 1, M + "iron_bars")
    v.fill(2, 4, -1, 4, 4, 1, M + "iron_bars")
    v.set(3, 5, 0, WSKULL)
    return v


BUILDERS = {
    "azure": [sun_serpent_pyramid, jungle_shrine, serpent_stela, cenote_temple, pirate_cove, volcano_caldera, ember_temple],
    "ashfang": [orc_warcamp, skullgate_fortress, blood_altar, bone_totem],
    "dreadmire": [witch_hut, sunken_crypt, gibbet, drowned_shrine],
    "frontier": [frontier_town, abandoned_mine, bandit_fort, sun_oracle, cattle_skull_marker],
    "everbloom": [mage_tower, fairy_ring, moonwell, arcane_henge],
    "crownlands": [market_crossroads, watchtower, windmill, castle_keep, lighthouse],
    "warscar": [ruined_keep, broken_trebuchet, war_graves, burned_house],
    "umbral": [gothic_cathedral, necropolis_gate, soulfire_obelisk, gibbet_cage],
}
