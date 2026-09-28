#!/usr/bin/env python3
"""Generates the Middle-earth inspired Iris pack JSON (keeps the shared road layer identical everywhere)."""
import json, os, shutil, sys

OUT = sys.argv[1]
if os.path.exists(OUT):
    shutil.rmtree(OUT)


def write(rel, data):
    path = os.path.join(OUT, rel + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def b(block, weight=None):
    d = {"block": block if ":" in block else "minecraft:" + block}
    if weight:
        d["weight"] = weight
    return d


def pal(*blocks, style=None, zoom=None):
    d = {"palette": [b(x) if isinstance(x, str) else b(*x) for x in blocks]}
    if style:
        d["style"] = {"style": style, "zoom": zoom or 1}
    return d


YROT = {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 360, "interval": 90}}

# ---------------------------------------------------------------------------
# Roads
# ---------------------------------------------------------------------------
# Every land/shore biome uses this as layer 0. Iris seeds each surface layer from the world's
# terrain seed + layer index + min/max height + palette size, so identical settings in every
# biome = one continuous road network across the whole world (VASCULAR noise peaks along the
# edges of large cells, which always form a connected web).
ROAD_ZOOM = 4.0          # bigger = roads further apart (roughly 100 * zoom blocks between junctions)
ROAD_GROUND_WEIGHT = 397  # ground : verge : road weights control road width
ROAD_VERGE_WEIGHT = 2
ROAD_PATH_WEIGHT = 2


def road_layer(ground, verge, road):
    """ground/verge/road are lists of block ids; weights are spread so totals stay identical."""
    def spread(blocks, total):
        n = len(blocks)
        base, extra = divmod(total, n)
        return [b(x, base + (1 if i < extra else 0)) for i, x in enumerate(blocks)]
    return {
        "minHeight": 1,
        "maxHeight": 1,
        "zoom": 1,
        "style": {"style": "VASCULAR", "zoom": ROAD_ZOOM,
                  "fracture": {"style": "SIMPLEX", "zoom": 0.4, "multiplier": 8}},
        # Only the first ground block is used: the palette is chosen by distance-from-road, so
        # extra ground blocks would show up as rings around the roads.
        "palette": spread(ground[:1], ROAD_GROUND_WEIGHT) + spread(verge, ROAD_VERGE_WEIGHT) + spread(road, ROAD_PATH_WEIGHT),
    }


ROAD_DIRT = (["coarse_dirt"], ["dirt_path", "dirt_path"])        # verge, road
ROAD_STONE = (["gravel", "cobblestone"], ["stone_bricks", "cracked_stone_bricks"])
ROAD_GONDOR = (["gravel"], ["polished_andesite", "stone_bricks"])
ROAD_SAND = (["coarse_dirt"], ["smooth_sandstone", "sandstone"])
ROAD_MORDOR = (["gravel"], ["polished_blackstone_bricks", "cracked_polished_blackstone_bricks"])
ROAD_SNOW = (["gravel"], ["cobblestone", "mossy_cobblestone"])
ROAD_ELVEN = (["moss_block"], ["mossy_stone_bricks", "stone_bricks"])
ROAD_MUD = (["mud"], ["packed_mud", "mud_bricks"])


def land_layers(ground, road, sub="dirt", deep=("dirt", "stone")):
    verge, path = road
    return [
        road_layer(ground, verge, path),
        {"minHeight": 2, "maxHeight": 3, "palette": [b(sub)]},
        {"minHeight": 1, "maxHeight": 4, "palette": [b(x) for x in deep]},
    ]


def plants(ground, *entries):
    """Decorators that only grow on the biome ground (never on roads)."""
    out = []
    for chance, blocks in entries:
        out.append({"chance": chance, "whitelist": [b(g) for g in ground], "palette": [b(x) for x in blocks]})
    return out


def custom(bid, sky, fog, water, water_fog, grass, foliage, category, temp=0.7, humid=0.5,
           precip="rain", particle=None, rarity=None):
    d = {
        "id": bid, "category": category, "temperature": temp, "humidity": humid, "downfallType": precip,
        "skyColor": sky, "fogColor": fog, "waterColor": water, "waterFogColor": water_fog,
        "grassColor": grass, "foliageColor": foliage,
    }
    if particle:
        d["ambientParticle"] = {"particle": particle, "rarity": rarity or 35}
    return [d]


def tree(name, seed, trunk, leaves, profile, hmin, hmax, chance, width=1, leaf_mode="FILLED",
         leaf_density=0.85, forks=0, trunk_palette=None, leaves_palette=None, roots=False, extra=None):
    t = {
        "name": name, "chance": chance, "density": 1, "variants": 6, "seed": seed,
        "trunk": "minecraft:" + trunk, "leaves": "minecraft:" + leaves, "profile": profile,
        "heightMin": hmin, "heightMax": hmax, "trunkWidth": width, "rotation": YROT,
        "canopy": {"mode": leaf_mode, "leafDensity": leaf_density},
    }
    if forks:
        t.update({"trunkForks": forks, "forkHeight": 0.45, "forkAngle": 24})
    if trunk_palette:
        t["trunkPalette"] = trunk_palette
    if leaves_palette:
        t["leavesPalette"] = leaves_palette
    if roots:
        t["roots"] = True
    if extra:
        t.update(extra)
    return t


def boulder(name, seed, blocks, chance=0.05, hmin=2, hmax=5):
    return {
        "name": name, "chance": chance, "density": 1, "variants": 6, "seed": seed, "mode": "PAINT",
        "form": "BOULDER", "block": "minecraft:" + blocks[0], "blockPalette": pal(*blocks, style="CELLULAR", zoom=0.4),
        "translate": {"y": -2}, "heightMin": hmin, "heightMax": hmax, "baseWidthMin": 2, "baseWidthMax": 5,
        "roughness": 0.4, "jitter": 0.4, "rotation": YROT,
    }


def spire(name, seed, blocks, chance, hmin, hmax, form="SPIRE"):
    return {
        "name": name, "chance": chance, "density": 1, "variants": 6, "seed": seed, "mode": "PAINT",
        "form": form, "block": "minecraft:" + blocks[0], "blockPalette": pal(*blocks, style="SIMPLEX", zoom=0.6),
        "heightMin": hmin, "heightMax": hmax, "baseWidthMin": 3, "baseWidthMax": 6, "topWidth": 1,
        "profile": "TAPER", "roughness": 0.35, "jitter": 0.3, "rotation": YROT,
    }


def ruin(name, seed, form, blocks, weathered, chance, hmin, hmax, wmin=1, wmax=2, moss=0.4):
    return {
        "name": name, "chance": chance, "density": 1, "variants": 5, "seed": seed, "form": form,
        "mode": "MIN_HEIGHT", "block": "minecraft:" + blocks[0], "blockPalette": pal(*blocks, style="STATIC"),
        "weatheringPalette": pal(*weathered, style="STATIC"), "mossiness": moss, "erosion": 0.35,
        "buriedFraction": 0.2, "heightMin": hmin, "heightMax": hmax, "widthMin": wmin, "widthMax": wmax,
        "lengthMin": 1, "lengthMax": 2, "rotation": YROT,
    }


def biome(path, name, color, derivative, gens, layers, deriv=None, decorators=None, proc=None, rarity=1,
          vanilla=None):
    d = {"name": name, "color": color, "rarity": rarity, "derivative": derivative,
         "vanillaDerivative": vanilla or derivative}
    if deriv:
        d["customDerivitives"] = deriv
    d["generators"] = [{"generator": g, "min": lo, "max": hi} for g, lo, hi in gens]
    d["layers"] = layers
    if decorators:
        d["decorators"] = decorators
    if proc:
        d["proceduralObjects"] = proc
    write("biomes/" + path, d)


# ---------------------------------------------------------------------------
# Generators (height noise). Biome min/max heights are relative to sea level (63).
# ---------------------------------------------------------------------------
def gen(name, style, zoom, hscale, seed, fn="BILINEAR_STARCAST_9", fracture=None, exponent=None):
    style_d = {"style": style, "zoom": zoom}
    if fracture:
        style_d["fracture"] = fracture
    comp = {"style": style_d, "seed": seed}
    if exponent:
        comp["exponent"] = exponent
    write("generators/" + name, {"interpolator": {"function": fn, "horizontalScale": hscale},
                                 "seed": seed * 7 + 1, "composite": [comp]})


gen("lowland", "IRIS_DOUBLE", 0.9, 12, 1101, fracture={"style": "NOWHERE", "zoom": 0.2, "multiplier": 18})
gen("hills", "PERLIN_IRIS", 1.3, 24, 1102, fracture={"style": "FRACTAL_WATER", "zoom": 0.3, "multiplier": 12})
gen("mountain", "FRACTAL_SMOKE", 1.0, 52, 1103)
gen("peaks", "FRACTAL_SMOKE", 0.7, 36, 1104, exponent=1.35)
gen("jagged", "CELLULAR_HEIGHT_IRIS", 0.6, 20, 1105, fracture={"style": "FRACTAL_SMOKE", "zoom": 0.2, "multiplier": 24})
gen("dunes", "SIMPLEX", 0.5, 16, 1106)
gen("ocean", "NOWHERE", 1.2, 30, 1107, fn="BILINEAR_STARCAST_3",
    fracture={"style": "IRIS_HALF", "zoom": 0.345, "multiplier": 18})
gen("flat", "SIMPLEX", 2.0, 8, 1108)

# ---------------------------------------------------------------------------
# Shared sea / shore / cave biomes
# ---------------------------------------------------------------------------
biome("sea/belegaer", "Belegaer, the Great Sea", "#1F4E8C", "minecraft:deep_ocean", [("ocean", -34, -14)],
      [{"minHeight": 2, "maxHeight": 4, "palette": [b("sand"), b("gravel"), b("clay")],
        "style": {"style": "SIMPLEX", "zoom": 0.5}}, {"palette": [b("stone")]}],
      deriv=custom("belegaer", "#7BA4D9", "#9EB8D6", "#2B5DA8", "#0B2447", "#6FA35A", "#5E9A48", "ocean", 0.5, 0.5))
biome("sea/sea-of-rhun", "Sea of Rhûn", "#2F6E8E", "minecraft:ocean", [("ocean", -20, -8)],
      [{"minHeight": 2, "maxHeight": 4, "palette": [b("sand", 3), b("gravel")]}, {"palette": [b("stone")]}],
      deriv=custom("sea_of_rhun", "#8FB3D1", "#A8C0D4", "#3A7CA0", "#123A52", "#7FA35C", "#6A9A4A", "ocean", 0.6, 0.5))
biome("sea/icebay-forochel", "Ice-bay of Forochel", "#A9D6F2", "minecraft:frozen_ocean", [("ocean", -24, -10)],
      [{"minHeight": 2, "maxHeight": 3, "palette": [b("gravel", 2), b("sand")]}, {"palette": [b("stone")]}],
      deriv=custom("forochel", "#C4D6E8", "#D8E4EE", "#3D57D6", "#050533", "#80B497", "#60A17B", "icy", 0.0, 0.5,
                   precip="snow"))

biome("shore/beach", "Grey Havens Shore", "#E8DCA0", "minecraft:beach", [("lowland", -4, 2)],
      land_layers(["sand"], ROAD_SAND, sub="sand", deep=("sandstone",)),
      deriv=custom("grey_havens_shore", "#9DC2E8", "#C8D8E8", "#4C8DC9", "#123A6B", "#8DB86A", "#77AB56", "beach", 0.7, 0.4))
biome("shore/stony-shore", "Stony Shore", "#8E8E8E", "minecraft:stony_shore", [("lowland", -3, 4)],
      land_layers(["stone", "gravel", "andesite"], ROAD_STONE, sub="stone", deep=("stone",)),
      vanilla="minecraft:stony_shore")
biome("shore/ash-shore", "Ashen Shore", "#3A3030", "minecraft:basalt_deltas", [("lowland", -3, 3)],
      land_layers(["blackstone", "basalt", "gravel"], ROAD_MORDOR, sub="blackstone", deep=("blackstone",)),
      deriv=custom("ashen_shore", "#4A2A22", "#3A2A26", "#3D3A2E", "#1A1612", "#6B6048", "#5A5040", "beach", 1.2, 0.0,
                   precip="none", particle="minecraft:white_ash", rarity=20),
      vanilla="minecraft:stony_shore")

biome("caves/deep-halls", "Deep Halls of the Dwarves", "#5A5A60", "minecraft:dripstone_caves", [("flat", 0, 0)],
      [{"minHeight": 1, "maxHeight": 1, "palette": [b("stone", 3), b("tuff"), b("deepslate")],
        "style": {"style": "CELLULAR", "zoom": 0.4}}, {"palette": [b("stone")]}])

SEA = ["sea/belegaer"]
SHORES = ["shore/beach", "shore/stony-shore"]
CAVES = ["caves/deep-halls"]

# ---------------------------------------------------------------------------
# ERIADOR: the Shire, Bree-land, the Lone-lands, the Old Forest, the Trollshaws
# ---------------------------------------------------------------------------
G = ["grass_block"]
biome("eriador/the-shire", "The Shire", "#5DBB3F", "minecraft:plains", [("hills", 3, 14)],
      land_layers(G, ROAD_DIRT),
      deriv=custom("the_shire", "#78A7FF", "#C0D8FF", "#3F76E4", "#050533", "#79C05A", "#59AE30", "plains", 0.8, 0.5),
      decorators=plants(G, (0.45, ["short_grass"]), (0.06, ["dandelion", "poppy", "cornflower", "oxeye_daisy", "azure_bluet"]),
                        (0.02, ["tall_grass"]), (0.01, ["sweet_berry_bush"])),
      proc={"trees": [tree("shire-oak", 2001, "oak_log", "oak_leaves", "OAK", 8, 13, 0.08, forks=2),
                      tree("shire-hedge", 2002, "oak_log", "oak_leaves", "BUSH", 2, 3, 0.05)]}, rarity=1)
biome("eriador/bree-land", "Bree-land", "#6EA84A", "minecraft:forest", [("hills", 4, 18)],
      land_layers(G, ROAD_DIRT),
      deriv=custom("bree_land", "#7AA6F0", "#BCD2F0", "#3F76E4", "#050533", "#6DAA4E", "#58A036", "forest", 0.7, 0.6),
      decorators=plants(G, (0.4, ["short_grass"]), (0.04, ["fern"]), (0.03, ["dandelion", "poppy"])),
      proc={"trees": [tree("bree-oak", 2011, "oak_log", "oak_leaves", "OAK", 9, 15, 0.25, forks=2),
                      tree("bree-birch", 2012, "birch_log", "birch_leaves", "BIRCH", 10, 14, 0.12)]})
biome("eriador/lone-lands", "The Lone-lands", "#9DA86A", "minecraft:plains", [("hills", 6, 24)],
      land_layers(G + ["coarse_dirt"], ROAD_STONE),
      deriv=custom("lone_lands", "#8AA2C8", "#B8C4CC", "#4E7AB0", "#10223A", "#9AA862", "#8A9A52", "plains", 0.6, 0.3),
      decorators=plants(G + ["coarse_dirt"], (0.35, ["short_grass"]), (0.05, ["tall_grass"]), (0.01, ["dead_bush"])),
      proc={"trees": [tree("lone-oak", 2021, "oak_log", "oak_leaves", "OAK", 6, 10, 0.02)],
            "formations": [boulder("lone-boulder", 2022, ["stone", "andesite", "mossy_cobblestone"], 0.04)],
            "ruins": [ruin("arnor-watchtower", 2023, "PILLAR", ["stone_bricks", "cracked_stone_bricks", "cobblestone"],
                           ["mossy_stone_bricks", "mossy_cobblestone"], 0.02, 6, 14, 2, 3),
                      ruin("arnor-wall", 2024, "WALL", ["cobblestone", "stone_bricks"], ["mossy_cobblestone"], 0.02, 2, 5, 4, 9)]})
biome("eriador/old-forest", "The Old Forest", "#2F5A2A", "minecraft:dark_forest", [("hills", 2, 12)],
      land_layers(["grass_block", "podzol", "moss_block"], ROAD_DIRT),
      deriv=custom("old_forest", "#6A8A9A", "#8AA090", "#3A6A5A", "#0A201A", "#4E7A34", "#3A6A28", "forest", 0.6, 0.9,
                   particle="minecraft:spore_blossom_air", rarity=60),
      decorators=plants(["grass_block", "podzol", "moss_block"], (0.3, ["fern", "short_grass"]), (0.03, ["brown_mushroom", "red_mushroom"])),
      proc={"trees": [tree("old-willow", 2031, "dark_oak_log", "dark_oak_leaves", "WILLOW", 12, 18, 0.25, width=2, roots=True),
                      tree("old-oak", 2032, "oak_log", "oak_leaves", "DARK_OAK", 14, 22, 0.35, width=2, forks=3, roots=True)]},
      rarity=2)
biome("eriador/trollshaws", "The Trollshaws", "#4F7A48", "minecraft:old_growth_spruce_taiga", [("hills", 10, 30), ("mountain", 0, 10)],
      land_layers(["grass_block", "podzol", "coarse_dirt"], ROAD_STONE),
      deriv=custom("trollshaws", "#7C98B8", "#A8B4C0", "#3D6A9A", "#0A1A30", "#5E8A4E", "#4A7A3C", "taiga", 0.4, 0.7),
      decorators=plants(["grass_block", "podzol"], (0.35, ["fern", "short_grass"]), (0.02, ["sweet_berry_bush"])),
      proc={"trees": [tree("troll-spruce", 2041, "spruce_log", "spruce_leaves", "SPRUCE", 14, 22, 0.3)],
            "formations": [boulder("troll-stone", 2042, ["stone", "mossy_cobblestone", "andesite"], 0.06, 3, 7)]},
      rarity=2)

# ---------------------------------------------------------------------------
# ANGMAR & the Ettenmoors: cold, bleak, ruined
# ---------------------------------------------------------------------------
SNOWY = ["snow_block", "grass_block", "coarse_dirt"]
biome("angmar/angmar-wastes", "Wastes of Angmar", "#6C6E78", "minecraft:snowy_taiga", [("hills", 8, 26)],
      land_layers(["snow_block", "coarse_dirt", "gravel", "podzol"], ROAD_SNOW, sub="dirt", deep=("stone", "deepslate")),
      deriv=custom("angmar", "#5A6070", "#6A6E7A", "#2E3A52", "#0A0E1A", "#6A7A6A", "#4E5E4E", "icy", -0.3, 0.4,
                   precip="snow", particle="minecraft:white_ash", rarity=25),
      decorators=plants(["snow_block", "podzol"], (0.08, ["dead_bush"]), (0.05, ["fern"])),
      proc={"trees": [tree("angmar-dead-spruce", 2101, "spruce_log", "spruce_leaves", "SPRUCE", 8, 14, 0.06,
                           leaf_mode="TATTERED", leaf_density=0.35),
                      tree("angmar-snag", 2102, "dark_oak_log", "spruce_leaves", "COLUMNAR", 5, 9, 0.03,
                           leaf_mode="TATTERED", leaf_density=0.1)],
            "ruins": [ruin("carn-dum-tower", 2103, "PILLAR", ["polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "deepslate_bricks"],
                           ["cracked_deepslate_bricks", "blackstone"], 0.03, 8, 18, 2, 3, moss=0.0),
                      ruin("angmar-arch", 2104, "ARCH", ["deepslate_bricks", "polished_blackstone_bricks"], ["cracked_deepslate_bricks"],
                           0.015, 5, 9, 3, 5, moss=0.0)],
            "formations": [spire("angmar-spike", 2105, ["deepslate", "blackstone", "tuff"], 0.03, 8, 16)]})
biome("angmar/carn-dum-peaks", "Peaks of Carn Dûm", "#9CA0AA", "minecraft:jagged_peaks", [("peaks", 40, 110), ("jagged", 0, 20)],
      land_layers(["snow_block", "stone", "deepslate"], ROAD_SNOW, sub="stone", deep=("deepslate", "stone")),
      deriv=custom("carn_dum", "#4A4E5E", "#5A5E6A", "#26324A", "#080C18", "#5E6E5E", "#465646", "extreme_hills", -0.6, 0.4,
                   precip="snow", particle="minecraft:white_ash", rarity=20),
      proc={"formations": [spire("carn-dum-spire", 2111, ["deepslate", "blackstone", "basalt"], 0.05, 12, 26)]}, rarity=2)
biome("angmar/ettenmoors", "The Ettenmoors", "#7B7A5A", "minecraft:windswept_hills", [("hills", 12, 34), ("jagged", 0, 8)],
      land_layers(["grass_block", "coarse_dirt", "stone", "gravel"], ROAD_STONE),
      deriv=custom("ettenmoors", "#7888A0", "#98A0A8", "#3A5A7A", "#0A1628", "#7E8A5A", "#6A7A4A", "extreme_hills", 0.2, 0.3),
      decorators=plants(["grass_block", "coarse_dirt"], (0.3, ["short_grass"]), (0.03, ["dead_bush"])),
      proc={"formations": [boulder("etten-boulder", 2121, ["stone", "andesite", "cobblestone"], 0.08, 3, 8)],
            "ruins": [ruin("rhudaur-wall", 2122, "WALL", ["cobblestone", "stone_bricks"], ["mossy_cobblestone"], 0.015, 2, 5, 4, 8)]})

# ---------------------------------------------------------------------------
# MISTY MOUNTAINS
# ---------------------------------------------------------------------------
biome("misty/misty-peaks", "Misty Mountains", "#B8C0CC", "minecraft:frozen_peaks", [("peaks", 50, 140), ("mountain", 0, 20)],
      land_layers(["snow_block", "stone"], ROAD_SNOW, sub="stone", deep=("stone", "andesite")),
      deriv=custom("misty_mountains", "#A8B8CC", "#D0D8E0", "#3D57D6", "#050533", "#80A08A", "#60907A", "extreme_hills", -0.5, 0.6,
                   precip="snow", particle="minecraft:snowflake", rarity=15))
biome("misty/misty-foothills", "Misty Foothills", "#7C9A7A", "minecraft:grove", [("mountain", 18, 52)],
      land_layers(["grass_block", "stone", "snow_block", "coarse_dirt"], ROAD_STONE, sub="stone", deep=("stone",)),
      deriv=custom("misty_foothills", "#8AA4C4", "#B8C4D0", "#3D6AA0", "#0A1A30", "#6E9A6A", "#5A8A56", "taiga", 0.1, 0.6),
      decorators=plants(["grass_block"], (0.3, ["short_grass", "fern"])),
      proc={"trees": [tree("misty-pine", 2201, "spruce_log", "spruce_leaves", "SPRUCE", 12, 20, 0.2)],
            "formations": [boulder("misty-boulder", 2202, ["stone", "andesite", "diorite"], 0.05, 3, 6)]})
biome("misty/high-pass", "The High Pass", "#9AA09A", "minecraft:windswept_gravelly_hills", [("mountain", 30, 70)],
      land_layers(["stone", "gravel", "andesite", "snow_block"], ROAD_STONE, sub="stone", deep=("stone",)),
      deriv=custom("high_pass", "#98A8BC", "#C0C8D0", "#3D57D6", "#050533", "#7A9A80", "#5E8A68", "extreme_hills", -0.2, 0.5,
                   precip="snow"),
      proc={"formations": [spire("goblin-crag", 2211, ["stone", "andesite", "tuff"], 0.03, 8, 16)]}, rarity=2)

# ---------------------------------------------------------------------------
# WILDERLAND: Mirkwood, the Vales of Anduin, Dale & the Lonely Mountain
# ---------------------------------------------------------------------------
MIRK = ["podzol", "grass_block", "coarse_dirt", "moss_block"]
biome("wilderland/mirkwood", "Mirkwood", "#1E3A1E", "minecraft:dark_forest", [("hills", 2, 14)],
      land_layers(MIRK, ROAD_DIRT),
      deriv=custom("mirkwood", "#2E3A2E", "#1E2A1E", "#2A3A2A", "#050A05", "#2E4A22", "#1E3A16", "forest", 0.6, 0.9,
                   particle="minecraft:mycelium", rarity=10),
      decorators=plants(MIRK, (0.25, ["fern"]), (0.06, ["cobweb"]), (0.04, ["brown_mushroom", "red_mushroom"]), (0.03, ["dead_bush"])),
      proc={"trees": [tree("mirkwood-giant", 2301, "dark_oak_log", "dark_oak_leaves", "DARK_OAK_FLAT_WIDE", 18, 30, 0.45, width=3,
                           forks=3, roots=True, leaf_mode="CLUMPED", leaf_density=0.95),
                      tree("mirkwood-dark", 2302, "dark_oak_log", "dark_oak_leaves", "DARK_OAK", 12, 20, 0.4, width=2, roots=True)]})
biome("wilderland/mirkwood-edge", "Eaves of Mirkwood", "#35583A", "minecraft:forest", [("hills", 3, 14)],
      land_layers(["grass_block", "podzol"], ROAD_DIRT),
      deriv=custom("mirkwood_eaves", "#5E7A8A", "#6E8A7A", "#2E5A4A", "#081A12", "#3E6A2E", "#2E5A22", "forest", 0.6, 0.8),
      decorators=plants(["grass_block", "podzol"], (0.35, ["fern", "short_grass"]), (0.02, ["cobweb"])),
      proc={"trees": [tree("eaves-oak", 2311, "dark_oak_log", "dark_oak_leaves", "DARK_OAK", 12, 18, 0.25, width=2),
                      tree("eaves-birch", 2312, "birch_log", "birch_leaves", "BIRCH", 10, 14, 0.1)]})
biome("wilderland/anduin-vale", "Vales of Anduin", "#7CC25A", "minecraft:meadow", [("lowland", 2, 10)],
      land_layers(G, ROAD_DIRT),
      deriv=custom("anduin_vale", "#78A7FF", "#C0D8FF", "#3F76E4", "#050533", "#83C860", "#66B83E", "plains", 0.7, 0.7),
      decorators=plants(G, (0.5, ["short_grass"]), (0.08, ["cornflower", "allium", "azure_bluet", "oxeye_daisy", "lily_of_the_valley"]),
                        (0.03, ["tall_grass"])),
      proc={"trees": [tree("vale-poplar", 2321, "birch_log", "oak_leaves", "POPLAR", 12, 18, 0.03)]})
biome("wilderland/dale", "Dale & the Long Lake", "#8FB85A", "minecraft:plains", [("hills", 4, 16)],
      land_layers(G, ROAD_STONE),
      deriv=custom("dale", "#80A8E8", "#C0D0E8", "#3F76E4", "#050533", "#86B45A", "#6AA042", "plains", 0.6, 0.5),
      decorators=plants(G, (0.4, ["short_grass"]), (0.04, ["dandelion", "poppy"])),
      proc={"trees": [tree("dale-oak", 2331, "oak_log", "oak_leaves", "OAK", 8, 12, 0.03)],
            "ruins": [ruin("dale-ruin", 2332, "WALL", ["stone_bricks", "cobblestone"], ["mossy_stone_bricks"], 0.02, 2, 6, 3, 7)]})
biome("wilderland/lonely-mountain", "Erebor, the Lonely Mountain", "#8A8478", "minecraft:stony_peaks", [("peaks", 60, 150)],
      land_layers(["stone", "andesite", "gravel"], ROAD_STONE, sub="stone", deep=("stone", "deepslate")),
      deriv=custom("erebor", "#7898C0", "#A8B8C8", "#3F76E4", "#050533", "#7A9070", "#62806A", "extreme_hills", 0.3, 0.4),
      rarity=6)

# ---------------------------------------------------------------------------
# LOTHLÓRIEN: golden mallorn woods (oak leaves tinted gold by the custom biome datapack)
# ---------------------------------------------------------------------------
MALLORN_TRUNK = pal(("birch_wood", 3), ("stripped_birch_wood", 2), style="CELLULAR", zoom=0.4)
biome("lorien/golden-wood", "Lothlórien, the Golden Wood", "#E3C23A", "minecraft:forest", [("hills", 3, 14)],
      land_layers(["grass_block", "moss_block"], ROAD_ELVEN),
      deriv=custom("lothlorien", "#A6C8FF", "#F2E6B0", "#5AB0E0", "#103A50", "#C8C850", "#F0C030", "forest", 0.8, 0.8,
                   particle="minecraft:spore_blossom_air", rarity=30),
      decorators=plants(["grass_block", "moss_block"], (0.4, ["short_grass"]),
                        (0.1, ["lily_of_the_valley", "oxeye_daisy", "dandelion", "azure_bluet"]), (0.03, ["tall_grass"])),
      proc={"trees": [tree("mallorn", 2401, "birch_wood", "oak_leaves", "OAK", 28, 42, 0.35, width=3, forks=3,
                           trunk_palette=MALLORN_TRUNK, roots=True, leaf_mode="CLUMPED", leaf_density=0.9),
                      tree("young-mallorn", 2402, "birch_log", "oak_leaves", "POPLAR", 14, 22, 0.2)]})
biome("lorien/cerin-amroth", "Cerin Amroth", "#F0DC6A", "minecraft:meadow", [("hills", 10, 22)],
      land_layers(["grass_block"], ROAD_ELVEN),
      deriv=custom("cerin_amroth", "#A6C8FF", "#F6ECC0", "#5AB0E0", "#103A50", "#B8D060", "#F0C830", "plains", 0.8, 0.7,
                   particle="minecraft:spore_blossom_air", rarity=20),
      decorators=plants(["grass_block"], (0.5, ["short_grass"]), (0.25, ["dandelion", "lily_of_the_valley", "oxeye_daisy"])),
      proc={"trees": [tree("amroth-mallorn", 2411, "birch_wood", "oak_leaves", "OAK", 32, 46, 0.03, width=3, forks=4,
                           trunk_palette=MALLORN_TRUNK, roots=True, leaf_mode="CLUMPED")]}, rarity=3)

# ---------------------------------------------------------------------------
# ROHAN & FANGORN
# ---------------------------------------------------------------------------
biome("rohan/rohan-plains", "Plains of Rohan", "#A4C04A", "minecraft:plains", [("lowland", 2, 12)],
      land_layers(G, ROAD_DIRT),
      deriv=custom("rohan", "#7AA8F0", "#C8DAF0", "#3F76E4", "#050533", "#A8C050", "#8AAA40", "plains", 0.8, 0.4),
      decorators=plants(G, (0.7, ["short_grass"]), (0.2, ["tall_grass"]), (0.02, ["dandelion", "oxeye_daisy"])))
biome("rohan/emyn-muil", "Emyn Muil", "#8C8474", "minecraft:windswept_hills", [("jagged", 10, 40)],
      land_layers(["stone", "gravel", "coarse_dirt", "andesite"], ROAD_STONE, sub="stone", deep=("stone",)),
      deriv=custom("emyn_muil", "#8898B0", "#A8A8A8", "#4A6A8A", "#0A1A2A", "#8A906A", "#72805A", "extreme_hills", 0.5, 0.2),
      proc={"formations": [spire("muil-crag", 2501, ["stone", "andesite", "tuff"], 0.06, 6, 14, form="HOODOO")]}, rarity=3)
biome("rohan/fangorn", "Fangorn Forest", "#2E5030", "minecraft:old_growth_pine_taiga", [("hills", 6, 24)],
      land_layers(["podzol", "moss_block", "rooted_dirt"], ROAD_DIRT),
      deriv=custom("fangorn", "#6A8A8A", "#7A9080", "#2E5A4A", "#081A12", "#4A7036", "#38602A", "forest", 0.5, 0.9,
                   particle="minecraft:spore_blossom_air", rarity=50),
      decorators=plants(["podzol", "moss_block", "rooted_dirt"], (0.35, ["fern", "large_fern"]), (0.05, ["brown_mushroom"]), (0.04, ["moss_carpet"])),
      proc={"trees": [tree("ent-tree", 2511, "dark_oak_log", "dark_oak_leaves", "DARK_OAK", 20, 32, 0.35, width=3, forks=4,
                           roots=True, leaf_mode="CLUMPED"),
                      tree("fangorn-spruce", 2512, "spruce_log", "spruce_leaves", "SPRUCE", 18, 28, 0.25, width=2, roots=True)]},
      rarity=2)

# ---------------------------------------------------------------------------
# GONDOR, ITHILIEN & the White Mountains
# ---------------------------------------------------------------------------
biome("gondor/gondor-fields", "Fields of Gondor", "#8CC254", "minecraft:plains", [("lowland", 3, 12)],
      land_layers(G, ROAD_GONDOR),
      deriv=custom("gondor", "#78A7FF", "#C8DCFF", "#3F76E4", "#050533", "#8CC254", "#6EAE3C", "plains", 0.8, 0.5),
      decorators=plants(G, (0.5, ["short_grass"]), (0.04, ["poppy", "cornflower", "oxeye_daisy"])),
      proc={"trees": [tree("gondor-oak", 2601, "oak_log", "oak_leaves", "OAK", 8, 12, 0.03)],
            "ruins": [ruin("numenor-pillar", 2602, "PILLAR", ["quartz_pillar", "smooth_quartz", "calcite"], ["calcite", "diorite"],
                           0.015, 5, 10, 1, 2, moss=0.1)]})
biome("gondor/ithilien", "Ithilien", "#4E9C3A", "minecraft:flower_forest", [("hills", 4, 18)],
      land_layers(["grass_block", "moss_block"], ROAD_GONDOR),
      deriv=custom("ithilien", "#78A7FF", "#C0D8F0", "#3F8AE4", "#05203A", "#5EB040", "#48A02C", "forest", 0.9, 0.7),
      decorators=plants(["grass_block", "moss_block"], (0.4, ["short_grass", "fern"]),
                        (0.12, ["lilac", "rose_bush", "peony", "allium", "blue_orchid", "poppy"])),
      proc={"trees": [tree("ithilien-oak", 2611, "oak_log", "oak_leaves", "OAK", 10, 16, 0.15, forks=2),
                      tree("ithilien-cedar", 2612, "spruce_log", "spruce_leaves", "COLUMNAR", 10, 16, 0.06),
                      tree("ithilien-cherry", 2613, "cherry_log", "cherry_leaves", "CHERRY", 7, 11, 0.04)],
            "ruins": [ruin("ithilien-arch", 2614, "ARCH", ["stone_bricks", "polished_andesite"], ["mossy_stone_bricks"], 0.01, 5, 8, 3, 5)]})
biome("gondor/white-mountains", "Ered Nimrais, the White Mountains", "#E4E4DC", "minecraft:snowy_slopes", [("peaks", 45, 120)],
      land_layers(["snow_block", "calcite", "stone", "diorite"], ROAD_GONDOR, sub="stone", deep=("calcite", "stone")),
      deriv=custom("white_mountains", "#A8C0E0", "#D8E0E8", "#3D57D6", "#050533", "#80A890", "#60987A", "extreme_hills", -0.3, 0.5,
                   precip="snow"))

# ---------------------------------------------------------------------------
# MORDOR: Gorgoroth, the Ephel Dúath, Orodruin & the Dead Marshes
# ---------------------------------------------------------------------------
ASH = ["blackstone", "basalt", "gravel", "coarse_dirt"]
MORDOR_SKY = dict(sky="#3A1A12", fog="#2A1410", water="#3A2A1A", water_fog="#120A06")
biome("mordor/gorgoroth", "Plateau of Gorgoroth", "#3A2E2A", "minecraft:basalt_deltas", [("hills", 8, 22)],
      land_layers(ASH, ROAD_MORDOR, sub="blackstone", deep=("blackstone", "basalt")),
      deriv=custom("gorgoroth", MORDOR_SKY["sky"], MORDOR_SKY["fog"], MORDOR_SKY["water"], MORDOR_SKY["water_fog"],
                   "#5A4A30", "#4A3A28", "desert", 1.4, 0.0, precip="none", particle="minecraft:ash", rarity=8),
      decorators=plants(["coarse_dirt", "gravel"], (0.04, ["dead_bush"])),
      proc={"formations": [spire("mordor-spire", 2701, ["blackstone", "basalt", "tuff"], 0.04, 8, 18),
                           {**spire("basalt-column", 2702, ["basalt", "smooth_basalt"], 0.05, 4, 10), "form": "BASALT_COLUMN"}],
            "ruins": [ruin("orc-watchtower", 2703, "PILLAR", ["polished_blackstone_bricks", "blackstone", "cracked_polished_blackstone_bricks"],
                           ["gilded_blackstone", "blackstone"], 0.02, 10, 20, 2, 3, moss=0.0)],
            "trees": [tree("mordor-snag", 2704, "dark_oak_log", "dark_oak_leaves", "COLUMNAR", 4, 7, 0.02,
                           leaf_mode="TATTERED", leaf_density=0.02)]})
biome("mordor/ephel-duath", "Ephel Dúath, the Mountains of Shadow", "#1E1A1C", "minecraft:jagged_peaks", [("jagged", 30, 80), ("peaks", 0, 40)],
      land_layers(["blackstone", "basalt", "deepslate"], ROAD_MORDOR, sub="blackstone", deep=("deepslate", "blackstone")),
      deriv=custom("ephel_duath", "#2A1210", "#1E0E0C", MORDOR_SKY["water"], MORDOR_SKY["water_fog"],
                   "#4A3A28", "#3A2A20", "extreme_hills", 1.0, 0.0, precip="none", particle="minecraft:ash", rarity=6),
      proc={"formations": [spire("shadow-fang", 2711, ["blackstone", "deepslate", "basalt"], 0.08, 14, 30)]})
biome("mordor/orodruin", "Orodruin, Mount Doom", "#7A2A10", "minecraft:basalt_deltas", [("peaks", 60, 130)],
      land_layers(["basalt", "blackstone", "magma_block", "smooth_basalt"], ROAD_MORDOR, sub="magma_block", deep=("blackstone", "magma_block")),
      deriv=custom("orodruin", "#5A1A08", "#4A1206", MORDOR_SKY["water"], MORDOR_SKY["water_fog"],
                   "#4A3020", "#3A2418", "desert", 2.0, 0.0, precip="none", particle="minecraft:lava", rarity=40),
      rarity=6)
biome("mordor/dead-marshes", "The Dead Marshes", "#4A5238", "minecraft:swamp", [("flat", -2, 2)],
      land_layers(["mud", "grass_block", "moss_block", "mud"], ROAD_MUD, sub="mud", deep=("mud", "clay")),
      deriv=custom("dead_marshes", "#5A6050", "#4A5040", "#3A4A2A", "#10180A", "#5A6A38", "#4A5A2E", "swamp", 0.8, 0.9,
                   particle="minecraft:mycelium", rarity=20),
      decorators=plants(["grass_block", "moss_block", "mud"], (0.2, ["short_grass"]), (0.05, ["dead_bush"]), (0.04, ["brown_mushroom"])),
      proc={"trees": [tree("marsh-willow", 2721, "mangrove_log", "mangrove_leaves", "WILLOW", 6, 10, 0.05, leaf_mode="TATTERED",
                           leaf_density=0.4)]})

# ---------------------------------------------------------------------------
# HARAD (far south)
# ---------------------------------------------------------------------------
biome("harad/harad-desert", "Deserts of Harad", "#E0C070", "minecraft:desert", [("dunes", 2, 18)],
      land_layers(["sand", "sand", "red_sand"], ROAD_SAND, sub="sand", deep=("sandstone",)),
      deriv=custom("harad", "#8AB0F0", "#E8D8B0", "#3FA0C4", "#08303A", "#BFB755", "#AEA42A", "desert", 2.0, 0.0, precip="none"),
      decorators=plants(["sand", "red_sand"], (0.02, ["dead_bush"]), (0.005, ["cactus"])),
      proc={"trees": [tree("harad-palm", 2801, "jungle_log", "jungle_leaves", "PALM", 7, 11, 0.01)],
            "ruins": [ruin("harad-obelisk", 2802, "PILLAR", ["sandstone", "cut_sandstone", "chiseled_sandstone"], ["smooth_sandstone"],
                           0.01, 8, 14, 1, 2, moss=0.0)]})
biome("harad/near-harad", "Near Harad Savanna", "#B8B050", "minecraft:savanna", [("hills", 3, 14)],
      land_layers(["grass_block", "coarse_dirt"], ROAD_SAND),
      deriv=custom("near_harad", "#80A8F0", "#D8D0B0", "#3F90C4", "#08283A", "#BFB755", "#AEA42A", "savanna", 1.6, 0.1, precip="none"),
      decorators=plants(["grass_block"], (0.5, ["short_grass"]), (0.05, ["tall_grass"])),
      proc={"trees": [tree("harad-acacia", 2811, "acacia_log", "acacia_leaves", "ACACIA", 7, 11, 0.04)]})

# ---------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------
def region(name, title, color, land, rarity=1, sea=None, shore=None, zoom=2.5, proc=None):
    d = {"name": title, "color": color, "rarity": rarity, "landBiomes": land, "seaBiomes": sea or SEA,
         "shoreBiomes": shore or SHORES, "caveBiomes": CAVES, "landBiomeZoom": zoom, "seaBiomeZoom": 4,
         "shoreBiomeZoom": 2, "shoreHeightMin": 0.75, "shoreHeightMax": 2.25, "shoreHeightZoom": 3.2}
    if proc:
        d["proceduralObjects"] = proc
    write("regions/" + name, d)


region("eriador", "Eriador", "#6DBB4F", ["eriador/the-shire", "eriador/bree-land", "eriador/lone-lands",
                                          "eriador/old-forest", "eriador/trollshaws"])
region("angmar", "Angmar", "#6C6E78", ["angmar/angmar-wastes", "angmar/carn-dum-peaks", "angmar/ettenmoors"], rarity=2,
       sea=["sea/icebay-forochel"], shore=["shore/stony-shore"])
region("misty-mountains", "The Misty Mountains", "#B8C0CC",
       ["misty/misty-peaks", "misty/misty-foothills", "misty/high-pass"], rarity=2, shore=["shore/stony-shore"])
region("wilderland", "Wilderland (Rhovanion)", "#3E7A3A", ["wilderland/mirkwood", "wilderland/mirkwood-edge", "wilderland/anduin-vale",
                                                          "wilderland/dale", "wilderland/lonely-mountain"],
       sea=["sea/sea-of-rhun"])
region("lothlorien", "Lothlórien", "#E3C23A", ["lorien/golden-wood", "lorien/cerin-amroth"], rarity=3, zoom=2)
region("rohan", "Rohan & Fangorn", "#A4C04A", ["rohan/rohan-plains", "rohan/fangorn", "rohan/emyn-muil"])
region("gondor", "Gondor", "#8CC254", ["gondor/gondor-fields", "gondor/ithilien", "gondor/white-mountains"])
region("mordor", "Mordor", "#3A2E2A", ["mordor/gorgoroth", "mordor/ephel-duath", "mordor/orodruin", "mordor/dead-marshes"],
       rarity=2, shore=["shore/ash-shore"])
region("harad", "Harad", "#E0C070", ["harad/harad-desert", "harad/near-harad"], rarity=2)

# ---------------------------------------------------------------------------
# Dimension
# ---------------------------------------------------------------------------
write("dimensions/middleearth", {
    "name": "Middle-earth",
    "version": 1,
    "environment": "NORMAL",
    "fluidHeight": 63,
    "dimensionHeight": {"min": -64, "max": 320},
    "landChance": 0.7,
    "continentZoom": 1.4,
    "continentalStyle": {"style": "NOWHERE_CELLULAR", "zoom": 6,
                         "fracture": {"style": "FRACTAL_SMOKE", "multiplier": 1}},
    "regionZoom": 12,
    "regionStyle": {"style": "CELLULAR_IRIS_DOUBLE",
                    "fracture": {"style": "FRACTAL_WATER", "zoom": 0.15, "multiplier": 9}},
    "landBiomeStyle": {"style": "NOWHERE_CELLULAR",
                       "fracture": {"style": "NOWHERE", "zoom": 0.15, "multiplier": 55}},
    "seaBiomeStyle": {"style": "SIMPLEX"},
    "shoreBiomeStyle": {"style": "NOWHERE_CELLULAR"},
    "caveBiomeStyle": {"style": "SIMPLEX", "zoom": 2.6},
    "coordFractureZoom": 0.15,
    "regions": ["eriador", "angmar", "misty-mountains", "wilderland", "lothlorien", "rohan", "gondor", "mordor", "harad"],
    "rockPalette": pal("stone"),
    "fluidPalette": pal("water"),
    "preventLeafDecay": True,
    "useMantle": True,
    "carvingEnabled": True,
    "decorate": True,
})
print("wrote", OUT)
