#!/usr/bin/env python3
"""
Builds the "Middle-earth Overworld" datapack for Minecraft 1.21.1.

The pack adds the Middle-earth mod's (Fabric, 1.21.1, namespace "me") rock
layers, ores, dirt/sand pockets, plants, wild crops and animals to the vanilla
Overworld. Faction NPCs and monsters are never added.

Every underground feature only replaces stone/deepslate and is capped at
Y=16, so nothing appears on the surface, on mountain tops or on grass/dirt.

Usage:  python3 generate.py
Output: middle-earth-overworld/  and  middle-earth-overworld.zip
"""
import json
import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
VANILLA = os.path.join(HERE, "vanilla-1.21.1-biomes")
OUT = os.path.join(HERE, "middle-earth-overworld")
NS = "me_overworld"   # namespace of this datapack
ME = "me"             # namespace of the Middle-earth mod on 1.21.1

PACK_FORMAT = 48      # Minecraft 1.21 / 1.21.1

UNDERGROUND_ORES = 6       # GenerationStep.Feature index
VEGETAL_DECORATION = 9

STONE_TAG = {"predicate_type": "minecraft:tag_match", "tag": "minecraft:stone_ore_replaceables"}
DEEPSLATE_TAG = {"predicate_type": "minecraft:tag_match", "tag": "minecraft:deepslate_ore_replaceables"}
BASE_STONES = [STONE_TAG, DEEPSLATE_TAG]

# Highest Y any underground feature can reach: well below sea level (63),
# so it never shows on the surface, mountains, grass or dirt.
MAX_UNDERGROUND_Y = 16


def me(name):
    return f"{ME}:{name}"


def block(name):
    return {"predicate_type": "minecraft:block_match", "block": me(name)}


def target(test, state):
    return {"target": test, "state": {"Name": state}}


configured = {}   # name -> configured feature json
placed = {}       # name -> placed feature json
underground_order = []  # placed feature names, in generation order


def trapezoid(lo, hi):
    return {"type": "minecraft:height_range",
            "height": {"type": "minecraft:trapezoid",
                       "min_inclusive": {"absolute": lo},
                       "max_inclusive": {"absolute": min(hi, MAX_UNDERGROUND_Y)}}}


def uniform(lo, hi):
    return {"type": "minecraft:height_range",
            "height": {"type": "minecraft:uniform",
                       "min_inclusive": {"absolute": lo},
                       "max_inclusive": {"absolute": min(hi, MAX_UNDERGROUND_Y)}}}


def add_ore(name, targets, size, lo, hi, count=None, rarity=None, height="trapezoid",
            kind="minecraft:ore", discard=0.0):
    configured[name] = {"type": kind, "config": {
        "size": size, "discard_chance_on_air_exposure": discard, "targets": targets}}
    placement = []
    if count is not None:
        placement.append({"type": "minecraft:count", "count": count})
    if rarity is not None:
        placement.append({"type": "minecraft:rarity_filter", "chance": rarity})
    placement.append({"type": "minecraft:in_square"})
    placement.append((trapezoid if height == "trapezoid" else uniform)(lo, hi))
    placement.append({"type": "minecraft:biome"})
    placed[name] = {"feature": f"{NS}:{name}", "placement": placement}
    underground_order.append(name)


# ---------------------------------------------------------------------------
# 1. Rock layers. Order matters: rocks first, then pockets, then ores that
#    look for those rocks.
# ---------------------------------------------------------------------------

# Upper rock band (Y -24..16): every natural Middle-earth rock type.
UPPER_ROCKS = [
    # (block, count, rarity)
    ("limestone", 1, None),
    ("dolomite", 1, None),
    ("gonluin", 1, None),
    ("blue_tuff", 1, None),
    ("green_tuff", 1, None),
    ("galonn", 1, None),
    ("izheraban", 1, None),
    ("zigilaban", 1, None),
    ("schist", 1, None),
    ("gneiss", 1, None),
    ("gabbro", 1, None),
    ("slate", 1, None),
    ("ironstone", 1, None),
    ("hematite", 1, None),
    ("ashen_stone", 1, None),
    ("pumice", 1, None),
    ("gilded_green_tuff", None, 4),
    ("old_limestone", None, 3),
    ("old_dolomite", None, 3),
    ("old_galonn", None, 3),
    ("old_izheraban", None, 3),
]
for rock, count, rarity in UPPER_ROCKS:
    add_ore(f"rock_{rock}", [target(t, me(rock)) for t in BASE_STONES],
            48, -24, 16, count=count, rarity=rarity)

# Deep rock layers, like the Middle-earth dimension: Nurgon under the upper
# band, Medgon at the very bottom of the world.
add_ore("rock_nurgon", [target(t, me("nurgon")) for t in BASE_STONES],
        64, -52, 0, count=6, height="uniform")
add_ore("rock_medgon", [target(t, me("medgon")) for t in BASE_STONES],
        64, -64, -28, count=7, height="uniform")

# Vanilla rock pockets the mod puts inside Nurgon/Medgon.
add_ore("nurgon_tuff", [target(block("nurgon"), "minecraft:tuff")], 32, -52, 0, count=2)
add_ore("nurgon_smooth_basalt", [target(block("nurgon"), "minecraft:smooth_basalt")], 32, -52, 0, count=2)
add_ore("medgon_blackstone", [target(block("medgon"), "minecraft:blackstone")], 32, -64, -28, count=2)

# ---------------------------------------------------------------------------
# 2. Dirt / sand / moss pockets, underground only.
# ---------------------------------------------------------------------------
POCKETS = [
    "ash_block", "ashen_dirt", "ashen_gravel", "ashen_sand", "black_sand",
    "white_sand", "river_sand", "dry_dirt", "mire", "turf", "dirty_roots",
    "grassy_dirt", "snowy_dirt", "old_podzol", "lorien_podzol",
    "forest_moss_block", "corrupted_moss_block",
]
for p in POCKETS:
    add_ore(f"pocket_{p}", [target(t, me(p)) for t in BASE_STONES],
            33, -32, 16, rarity=2)

# ---------------------------------------------------------------------------
# 3. Ores. Each Middle-earth rock gets its matching ore variant, following the
#    mod's own ore lists (CavesConfiguredFeatures).
# ---------------------------------------------------------------------------
# rock -> prefix of the ore set used inside it (None = vanilla ore block)
SHALLOW_ORE_SET = {
    "gonluin": "gonluin_",
    "limestone": "limestone_", "galonn": "limestone_", "izheraban": "limestone_",
    "ashen_stone": "ashen_",
    "ironstone": "ironstone_", "hematite": "ironstone_",
    "slate": "slate_",
    "dolomite": None, "green_tuff": None,
}


def shallow_targets(ore):
    """Coal / copper: only inside Middle-earth rocks (vanilla already has them in stone)."""
    out = []
    for rock, prefix in SHALLOW_ORE_SET.items():
        state = me(prefix + ore) if prefix else f"minecraft:{ore}"
        out.append(target(block(rock), state))
    out.append(target({"predicate_type": "minecraft:block_match", "block": "minecraft:calcite"},
                      me("calcite_" + ore)))
    return out


add_ore("ore_coal", shallow_targets("coal_ore"), 17, -24, 16, count=20)
add_ore("ore_copper", shallow_targets("copper_ore"), 15, -24, 16, count=16)

tin_targets = []
for rock, prefix in SHALLOW_ORE_SET.items():
    tin_targets.append(target(block(rock), me((prefix or "") + "tin_ore")))
tin_targets += [
    target({"predicate_type": "minecraft:block_match", "block": "minecraft:calcite"}, me("calcite_tin_ore")),
    target(block("nurgon"), me("nurgon_tin_ore")),
    target(STONE_TAG, me("tin_ore")),
    target(DEEPSLATE_TAG, me("deepslate_tin_ore")),
]
add_ore("ore_tin", tin_targets, 12, -48, 16, count=12)

add_ore("ore_quartzite", [
    target(block("ashen_stone"), me("quartzite")),
    target(block("gonluin"), me("quartzite")),
    target(block("limestone"), me("quartzite")),
    target(STONE_TAG, me("quartzite")),
    target(DEEPSLATE_TAG, me("quartzite")),
], 21, -32, 16, count=2)

add_ore("ore_lead", [
    target(block("nurgon"), me("nurgon_lead_ore")),
    target(block("medgon"), me("medgon_lead_ore")),
    target(DEEPSLATE_TAG, me("deepslate_lead_ore")),
], 12, -64, 0, count=10)

add_ore("ore_iron", [
    target(block("nurgon"), me("nurgon_iron_ore")),
    target(block("medgon"), me("medgon_iron_ore")),
], 10, -64, 4, count=14)

add_ore("ore_silver", [
    target(block("nurgon"), me("nurgon_silver_ore")),
    target(block("medgon"), me("medgon_silver_ore")),
], 7, -64, 0, count=6)

add_ore("ore_gold", [
    target(block("nurgon"), me("nurgon_gold_ore")),
    target(block("medgon"), me("medgon_gold_ore")),
], 5, -64, -8, count=4)

add_ore("ore_jade", [
    target(block("nurgon"), me("jadeite")),
    target(block("medgon"), me("jadeite")),
], 16, -64, 0, count=3)

add_ore("ore_mithril", [target(block("medgon"), me("medgon_mithril_ore"))],
        3, -64, -32, count=3, height="uniform", kind="minecraft:scattered_ore")

# ---------------------------------------------------------------------------
# 4. Plants, flowers and wild crops (surface).
# ---------------------------------------------------------------------------
TEMPERATE = ["plains", "sunflower_plains", "meadow", "forest", "flower_forest",
             "birch_forest", "old_growth_birch_forest", "dark_forest",
             "windswept_forest", "cherry_grove"]
FORESTS = ["forest", "flower_forest", "birch_forest", "old_growth_birch_forest",
           "dark_forest", "windswept_forest", "taiga", "old_growth_pine_taiga",
           "old_growth_spruce_taiga", "snowy_taiga"]
HILLS = ["windswept_hills", "windswept_gravelly_hills", "windswept_forest", "meadow", "grove"]
COLD = ["taiga", "old_growth_pine_taiga", "old_growth_spruce_taiga", "snowy_taiga",
        "snowy_plains", "grove", "snowy_slopes", "ice_spikes"]
DRY = ["savanna", "savanna_plateau", "windswept_savanna", "badlands",
       "wooded_badlands", "eroded_badlands", "desert"]
WET = ["swamp", "mangrove_swamp", "river"]
COAST = ["beach"]
JUNGLE = ["jungle", "sparse_jungle", "bamboo_jungle"]
MUSHROOM = ["mushroom_fields"]

# (block, biomes, rarity (1 in N chunks), tries, spread)
PLANTS = [
    # wild crops -> seeds/food for the mod's farming and cooking
    ("wild_wheat", TEMPERATE, 24, 32, 6),
    ("tall_wild_wheat", TEMPERATE, 32, 24, 6),
    ("wild_flax", TEMPERATE + HILLS, 32, 24, 5),
    ("wild_pipeweed", TEMPERATE, 48, 20, 5),
    ("wild_tomato", TEMPERATE + JUNGLE, 48, 20, 5),
    ("wild_bell_pepper", TEMPERATE + JUNGLE + DRY, 48, 20, 5),
    ("wild_cucumber", TEMPERATE + JUNGLE, 48, 20, 5),
    ("wild_garlic", TEMPERATE + FORESTS, 48, 20, 5),
    ("wild_onion", TEMPERATE + HILLS, 48, 20, 5),
    ("wild_lettuce", TEMPERATE, 48, 20, 5),
    ("wild_leek", TEMPERATE + HILLS, 48, 20, 5),
    ("wild_potato", TEMPERATE + COLD, 48, 20, 5),
    ("wild_carrot", TEMPERATE, 48, 20, 5),
    ("wild_beetroot", TEMPERATE, 48, 20, 5),
    # berry bushes
    ("strawberry_bush", TEMPERATE, 24, 16, 5),
    ("tough_berry_bush", FORESTS + COLD + HILLS, 24, 16, 5),
    # flowers
    ("elanor", ["meadow", "flower_forest"], 12, 24, 5),
    ("mallos", ["meadow", "flower_forest", "plains"], 16, 24, 5),
    ("green_jewel_cornflower", ["meadow", "flower_forest", "plains", "sunflower_plains"], 16, 24, 5),
    ("yellow_flower", TEMPERATE, 12, 24, 5),
    ("light_blue_flowers", TEMPERATE, 16, 32, 6),
    ("magenta_flowers", TEMPERATE, 16, 32, 6),
    ("orange_flowers", TEMPERATE + DRY, 16, 32, 6),
    ("pink_flowers", TEMPERATE, 16, 32, 6),
    ("purple_flowers", TEMPERATE, 16, 32, 6),
    ("red_flowers", TEMPERATE, 16, 32, 6),
    ("white_flowers", TEMPERATE + COLD, 16, 32, 6),
    ("yellow_flowers", TEMPERATE, 16, 32, 6),
    ("lavender", ["meadow", "plains", "sunflower_plains", "savanna"], 12, 32, 6),
    ("yellow_trollius", ["meadow", "flower_forest", "swamp"], 16, 24, 5),
    ("sedum", HILLS + ["stony_shore"], 12, 24, 5),
    ("yellow_sedum", HILLS, 12, 24, 5),
    ("heather", HILLS + COLD, 8, 32, 6),
    ("red_heather", HILLS, 12, 32, 6),
    ("dry_heather", HILLS + DRY, 12, 32, 6),
    ("dead_heather", COLD, 12, 32, 6),
    ("heath", HILLS + COLD, 8, 32, 6),
    # grasses / ferns / shrubs
    ("wild_grass", TEMPERATE, 4, 32, 7),
    ("wildergrass", TEMPERATE + HILLS, 6, 32, 7),
    ("temperate_grass", TEMPERATE, 6, 32, 7),
    ("grass_tuft", TEMPERATE + HILLS, 6, 32, 7),
    ("false_oatgrass", TEMPERATE, 8, 32, 7),
    ("wheatgrass", TEMPERATE + DRY, 8, 32, 7),
    ("bracken", FORESTS + HILLS, 4, 32, 7),
    ("green_shrub", TEMPERATE + JUNGLE, 8, 24, 6),
    ("fallen_leaves", FORESTS, 4, 32, 7),
    ("grim_grass", ["dark_forest"], 4, 32, 7),
    ("frozen_grass", COLD, 4, 32, 7),
    ("frozen_tuft", COLD, 6, 32, 7),
    ("frozen_shrub", COLD, 8, 24, 6),
    ("dry_grass", DRY, 4, 32, 7),
    ("dying_grass", DRY, 6, 32, 7),
    ("brown_grass", DRY + HILLS, 6, 32, 7),
    ("small_dry_shrub", DRY, 6, 24, 6),
    ("tan_shrub", DRY, 8, 24, 6),
    ("shriveled_shrub", DRY, 8, 24, 6),
    ("horokaka", DRY, 16, 16, 5),
    ("scorched_grass", ["badlands", "eroded_badlands", "wooded_badlands"], 6, 32, 7),
    ("scorched_tuft", ["badlands", "eroded_badlands", "wooded_badlands"], 8, 32, 7),
    ("scorched_shrub", ["badlands", "eroded_badlands", "wooded_badlands"], 8, 24, 6),
    ("beach_grass", COAST, 4, 32, 7),
    ("coastal_panic_grass", COAST + ["stony_shore"], 6, 32, 7),
    ("short_bulrush", WET, 4, 32, 6),
    ("tall_bulrush", WET, 6, 32, 6),
    ("short_cattails", WET, 4, 32, 6),
    ("tall_cattails", WET, 6, 32, 6),
    # mushrooms
    ("brown_bolete", FORESTS + MUSHROOM + ["swamp"], 12, 16, 5),
    ("morsel", FORESTS + MUSHROOM, 16, 16, 5),
    ("white_mushroom", FORESTS + MUSHROOM + ["swamp"], 16, 16, 5),
]

# Ground a plant may be placed on (checked one block below).
GROUND = ["minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt",
          "minecraft:podzol", "minecraft:rooted_dirt", "minecraft:mud",
          "minecraft:moss_block", "minecraft:mycelium", "minecraft:snow_block"]
SANDY = ["minecraft:sand", "minecraft:red_sand", "minecraft:grass_block",
         "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:terracotta"]

vegetation_order = []
plant_biomes = {}
for name, biomes, rarity, tries, spread in PLANTS:
    ground = SANDY if (set(biomes) & set(DRY + COAST)) else GROUND
    configured[f"patch_{name}"] = {"type": "minecraft:random_patch", "config": {
        "tries": tries, "xz_spread": spread, "y_spread": 3,
        "feature": {
            "feature": {"type": "minecraft:simple_block", "config": {
                "to_place": {"type": "minecraft:simple_state_provider",
                             "state": {"Name": me(name)}}}},
            "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {
                "type": "minecraft:all_of", "predicates": [
                    {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                    {"type": "minecraft:matching_blocks", "offset": [0, -1, 0], "blocks": ground},
                ]}}],
        }}}
    placed[f"patch_{name}"] = {"feature": f"{NS}:patch_{name}", "placement": [
        {"type": "minecraft:rarity_filter", "chance": rarity},
        {"type": "minecraft:in_square"},
        {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING"},
        {"type": "minecraft:biome"},
    ]}
    vegetation_order.append(f"patch_{name}")
    plant_biomes[f"patch_{name}"] = set(biomes)

# ---------------------------------------------------------------------------
# 5. Animals only (no faction NPCs, orcs, trolls, spiders, wargs, wights...).
# ---------------------------------------------------------------------------
ANIMALS = [
    # (entity, weight, min, max, biomes)
    ("deer", 8, 1, 4, FORESTS + ["meadow", "cherry_grove", "grove", "plains"]),
    ("pheasant", 6, 1, 2, TEMPERATE + ["savanna", "taiga"]),
    ("swan", 7, 1, 3, WET),
    ("snail", 5, 1, 3, FORESTS + JUNGLE + ["swamp", "mangrove_swamp", "lush_caves"]),
    ("broadhoof_goat", 4, 1, 3, HILLS + ["stony_peaks", "jagged_peaks", "frozen_peaks", "snowy_slopes"]),
]


# ---------------------------------------------------------------------------
# 6. Chunk flag + retrofit for chunks that existed before the pack was added.
#
#    New chunks: world generation adds everything above, then replaces the
#    bedrock at the chunk's corner (x0, -64, z0) with reinforced deepslate as
#    a "done" flag.
#    Old chunks: still have bedrock there. A function loop finds them around
#    players, runs the same features with /place feature, then sets the flag.
#    So every chunk gets the content exactly once.
# ---------------------------------------------------------------------------
TOP_LAYER_MODIFICATION = 10
FLAG_BLOCK = "minecraft:reinforced_deepslate"
RETRO_RADIUS = 4        # chunks around each player that get checked
RETRO_BUDGET = 2        # old chunks converted per player per run
RETRO_INTERVAL = "10t"  # how often the loop runs

configured["chunk_flag"] = {"type": "minecraft:simple_block", "config": {
    "to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": FLAG_BLOCK}}}}
placed["chunk_flag"] = {"feature": f"{NS}:chunk_flag", "placement": [
    {"type": "minecraft:height_range",
     "height": {"type": "minecraft:constant", "value": {"absolute": -64}}},
    {"type": "minecraft:block_predicate_filter",
     "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:bedrock"}},
    {"type": "minecraft:biome"},
]}

# /place feature only takes configured features, and a nested placed feature
# cannot use the "biome" modifier. So each retrofit feature is a
# random_selector whose default is the same placed feature minus that
# modifier; the biome check is done in the function with biome tags.
retro_configured = {}
for name in underground_order + vegetation_order:
    mods = [m for m in placed[name]["placement"] if m["type"] != "minecraft:biome"]
    retro_configured[f"retro_{name}"] = {"type": "minecraft:random_selector", "config": {
        "features": [], "default": {"feature": f"{NS}:{name}", "placement": mods}}}
configured.update(retro_configured)


def functions():
    f = {}
    f["load"] = [
        "scoreboard objectives add me_ow dummy",
        "scoreboard players set #16 me_ow 16",
        "execute unless score #enabled me_ow matches 0..1 run scoreboard players set #enabled me_ow 1",
        f"schedule function {NS}:retrofit/loop {RETRO_INTERVAL} replace",
    ]
    f["retrofit/loop"] = [
        f"schedule function {NS}:retrofit/loop {RETRO_INTERVAL} replace",
        "execute unless score #enabled me_ow matches 1 run return 0",
        f"execute as @a[gamemode=!spectator] at @s if dimension minecraft:overworld run function {NS}:retrofit/player",
    ]
    offsets = sorted(((dx, dz) for dx in range(-RETRO_RADIUS, RETRO_RADIUS + 1)
                      for dz in range(-RETRO_RADIUS, RETRO_RADIUS + 1)),
                     key=lambda o: (o[0] ** 2 + o[1] ** 2, o))
    player = [
        "execute store result score #px me_ow run data get entity @s Pos[0]",
        "execute store result score #pz me_ow run data get entity @s Pos[2]",
        "scoreboard players operation #px me_ow /= #16 me_ow",
        "scoreboard players operation #pz me_ow /= #16 me_ow",
        f"scoreboard players set #budget me_ow {RETRO_BUDGET}",
    ]
    for dx, dz in offsets:
        player += [f"execute if score #budget me_ow matches 1.. run scoreboard players set #dx me_ow {dx}",
                   f"execute if score #budget me_ow matches 1.. run scoreboard players set #dz me_ow {dz}",
                   f"execute if score #budget me_ow matches 1.. run function {NS}:retrofit/try"]
    f["retrofit/player"] = player
    tr = []
    for axis in ("x", "z"):
        tr += [f"scoreboard players operation #c{axis} me_ow = #p{axis} me_ow",
               f"scoreboard players operation #c{axis} me_ow += #d{axis} me_ow",
               f"scoreboard players operation #c{axis} me_ow *= #16 me_ow",
               f"execute store result storage {NS}:tmp c.{axis} int 1 run scoreboard players get #c{axis} me_ow",
               f"execute store result storage {NS}:tmp c.{axis}m int 1 run scoreboard players remove #c{axis} me_ow 16",
               f"execute store result storage {NS}:tmp c.{axis}p int 1 run scoreboard players add #c{axis} me_ow 32"]
    tr.append(f"function {NS}:retrofit/check with storage {NS}:tmp c")
    f["retrofit/try"] = tr
    f["retrofit/check"] = [
        "# Only chunks from before the pack (bedrock still at the corner).",
        "$execute unless loaded $(x) 0 $(z) run return 0",
        "$execute unless loaded $(xm) 0 $(zm) run return 0",
        "$execute unless loaded $(xp) 0 $(zp) run return 0",
        "$execute unless loaded $(xm) 0 $(zp) run return 0",
        "$execute unless loaded $(xp) 0 $(zm) run return 0",
        f"$execute unless block $(x) -64 $(z) minecraft:bedrock run return 0",
        f"$execute positioned $(x) 0 $(z) run function {NS}:retrofit/generate",
        f"$setblock $(x) -64 $(z) {FLAG_BLOCK}",
        "scoreboard players remove #budget me_ow 1",
    ]
    gen = [f"place feature {NS}:retro_{n} ~ ~ ~" for n in underground_order]
    for n in vegetation_order:
        gen.append(f"execute if biome ~8 ~64 ~8 #{NS}:{n} run place feature {NS}:retro_{n} ~ ~ ~")
    f["retrofit/generate"] = gen
    f["retrofit/stop"] = ["scoreboard players set #enabled me_ow 0",
                          'tellraw @s {"text":"Middle-earth Overworld: converting old chunks is OFF","color":"yellow"}']
    f["retrofit/start"] = ["scoreboard players set #enabled me_ow 1",
                           'tellraw @s {"text":"Middle-earth Overworld: converting old chunks is ON","color":"green"}']
    return f

# ---------------------------------------------------------------------------
# Write the pack
# ---------------------------------------------------------------------------


def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)

    dump(os.path.join(OUT, "pack.mcmeta"), {"pack": {
        "pack_format": PACK_FORMAT,
        "description": "Middle-earth rocks, ores, plants & animals in the Overworld (MC 1.21.1)"}})
    shutil.copy(os.path.join(HERE, "pack-README.txt"), os.path.join(OUT, "README.txt"))

    for name, data in configured.items():
        dump(os.path.join(OUT, "data", NS, "worldgen", "configured_feature", name + ".json"), data)
    for name, data in placed.items():
        dump(os.path.join(OUT, "data", NS, "worldgen", "placed_feature", name + ".json"), data)

    for fname in sorted(os.listdir(VANILLA)):
        biome = fname[:-5]
        with open(os.path.join(VANILLA, fname)) as f:
            data = json.load(f)
        features = data["features"]
        while len(features) <= TOP_LAYER_MODIFICATION:
            features.append([])
        features[UNDERGROUND_ORES] += [f"{NS}:{n}" for n in underground_order]
        features[VEGETAL_DECORATION] += [f"{NS}:{n}" for n in vegetation_order
                                         if biome in plant_biomes[n]]
        features[TOP_LAYER_MODIFICATION].append(f"{NS}:chunk_flag")
        creatures = data.setdefault("spawners", {}).setdefault("creature", [])
        for entity, weight, lo, hi, biomes in ANIMALS:
            if biome in biomes:
                creatures.append({"type": me(entity), "weight": weight,
                                  "minCount": lo, "maxCount": hi})
        dump(os.path.join(OUT, "data", "minecraft", "worldgen", "biome", fname), data)

    for name, lines in functions().items():
        path = os.path.join(OUT, "data", NS, "function", name + ".mcfunction")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
    dump(os.path.join(OUT, "data", "minecraft", "tags", "function", "load.json"),
         {"values": [f"{NS}:load"]})
    for n in vegetation_order:
        dump(os.path.join(OUT, "data", NS, "tags", "worldgen", "biome", n + ".json"),
             {"values": [f"minecraft:{b}" for b in sorted(plant_biomes[n])]})

    zpath = OUT + ".zip"
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, OUT))
    print(f"{len(configured)} configured features, {len(placed)} placed features, "
          f"{len(os.listdir(VANILLA))} biomes -> {zpath}")


if __name__ == "__main__":
    main()
