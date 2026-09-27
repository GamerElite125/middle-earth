#!/usr/bin/env python3
"""
Builds the Middle-earth datapacks for Minecraft 1.21.1 and 1.21.8.

Two packs per version:

  middle-earth-overworld-<ver>
      Keeps the vanilla Overworld and adds the Middle-earth mod's rock layers,
      ores, dirt/sand pockets (underground only, capped at Y=16), plants, wild
      crops and animals. No faction NPCs or monsters. Old chunks are converted
      by a function loop, new chunks during generation.

  middle-earth-map-overworld-<ver>
      Replaces the Overworld generator with the mod's own Middle-earth
      generator, so the Overworld is the real Middle-earth map with all of its
      biomes, terrain, rocks, ores, trees, plants, structures and spawns
      (animals, monsters and faction NPCs). New worlds only.

Both need the Middle-earth Fabric mod for the same Minecraft version.

Usage:  python3 generate.py
Output: dist/<pack>/  and  dist/<pack>.zip
"""
import json
import os
import shutil
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "dist")
NS = "me_overworld"   # namespace of these datapacks

UNDERGROUND_ORES = 6       # GenerationStep.Feature indexes
VEGETAL_DECORATION = 9
TOP_LAYER_MODIFICATION = 10

STONE_TAG = {"predicate_type": "minecraft:tag_match", "tag": "minecraft:stone_ore_replaceables"}
DEEPSLATE_TAG = {"predicate_type": "minecraft:tag_match", "tag": "minecraft:deepslate_ore_replaceables"}
BASE_STONES = [STONE_TAG, DEEPSLATE_TAG]
CALCITE = {"predicate_type": "minecraft:block_match", "block": "minecraft:calcite"}

# Highest Y any underground feature can reach: well below sea level (63),
# so it never shows on the surface, mountains, grass or dirt.
MAX_UNDERGROUND_Y = 16

# Hobbiton: map pixel (933, 900) x 32 blocks per pixel (both versions).
MAP_SPAWN = (29856, 90, 28800)

# ---------------------------------------------------------------------------
# Per-version data, taken from the mod's source for that Minecraft version.
# ---------------------------------------------------------------------------
COMMON_POCKETS = [
    "ash_block", "ashen_dirt", "ashen_gravel", "ashen_sand", "black_sand",
    "white_sand", "river_sand", "dry_dirt", "mire", "turf", "dirty_roots",
    "grassy_dirt", "snowy_dirt", "old_podzol", "lorien_podzol",
    "forest_moss_block", "corrupted_moss_block",
]

VERSIONS = {
    "1.21.1": {
        "pack_format": 48,
        "me": "me",
        "animal_ns": {},  # all animals are in the "me" namespace
        "rocks": [
            "limestone", "dolomite", "gonluin", "blue_tuff", "green_tuff", "galonn",
            "izheraban", "zigilaban", "schist", "gneiss", "gabbro", "slate",
            "ironstone", "hematite", "ashen_stone", "pumice",
        ],
        "rare_rocks": {"gilded_green_tuff": 4, "old_limestone": 3, "old_dolomite": 3,
                       "old_galonn": 3, "old_izheraban": 3},
        # rock -> ore set prefix (None = vanilla ore / plain tin_ore)
        "ore_sets": {
            "gonluin": "gonluin_",
            "limestone": "limestone_", "galonn": "limestone_", "izheraban": "limestone_",
            "ashen_stone": "ashen_",
            "ironstone": "ironstone_", "hematite": "ironstone_",
            "slate": "slate_",
            "dolomite": None, "green_tuff": None,
        },
        "quartzite_in": ["ashen_stone", "gonluin", "limestone"],
        "gems": {},
        "plants_removed": [],
        "plants_added": [],
    },
    "1.21.8": {
        "pack_format": 81,
        "me": "middle-earth",
        "animal_ns": {"deer": "wild-things", "pheasant": "wild-things",
                      "swan": "wild-things", "snail": "wild-things"},
        "rocks": [
            "limestone", "dolomite", "blue_tuff", "green_tuff", "galonn",
            "izheraban", "zigilaban", "schist", "gneiss", "gabbro", "slate",
            "ironstone", "hematite", "ashenstone", "pumice", "chalk",
            "travertine", "khagalaban",
        ],
        "rare_rocks": {"gilded_green_tuff": 4, "old_limestone": 3, "old_dolomite": 3,
                       "old_galonn": 3, "old_izheraban": 3, "old_travertine": 3},
        "ore_sets": {
            "khagalaban": "khagalaban_", "blue_tuff": "khagalaban_",
            "limestone": "limestone_", "galonn": "limestone_", "izheraban": "limestone_",
            "ashenstone": "ashen_",
            "ironstone": "ironstone_", "hematite": "ironstone_",
            "slate": "slate_", "chalk": "chalk_", "gabbro": "gabbro_",
            "travertine": "travertine_",
            "dolomite": None, "green_tuff": None,
        },
        "quartzite_in": ["ashenstone", "khagalaban", "limestone"],
        # name -> (rocks, size, lo, hi, count); scattered like the mod does
        "gems": {
            "emerald": (["nurgon", "medgon"], 5, -61, 0, 2),
            "ruby": (["nurgon", "medgon"], 5, -61, -32, 2),
            "sapphire": (["nurgon", "medgon"], 5, -49, -11, 2),
            "adamant": (["medgon"], 3, -61, -42, 2),
        },
        "plants_removed": ["dry_grass", "horokaka"],
        "plants_added": [("meadowgrass", "TEMPERATE", 6, 32, 7),
                         ("sparse_grass", "TEMPERATE+HILLS", 6, 32, 7)],
    },
}

# ---------------------------------------------------------------------------
# Biome groups (vanilla Overworld biomes)
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
BADLANDS = ["badlands", "eroded_badlands", "wooded_badlands"]
GROUPS = {"TEMPERATE": TEMPERATE, "HILLS": HILLS}

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
    ("scorched_grass", BADLANDS, 6, 32, 7),
    ("scorched_tuft", BADLANDS, 8, 32, 7),
    ("scorched_shrub", BADLANDS, 8, 24, 6),
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

# Animals only (no faction NPCs, orcs, trolls, spiders, wargs, wights...).
ANIMALS = [
    # (entity, weight, min, max, biomes)
    ("deer", 8, 1, 4, FORESTS + ["meadow", "cherry_grove", "grove", "plains"]),
    ("pheasant", 6, 1, 2, TEMPERATE + ["savanna", "taiga"]),
    ("swan", 7, 1, 3, WET),
    ("snail", 5, 1, 3, FORESTS + JUNGLE + ["swamp", "mangrove_swamp", "lush_caves"]),
    ("broadhoof_goat", 4, 1, 3, HILLS + ["stony_peaks", "jagged_peaks", "frozen_peaks", "snowy_slopes"]),
]

# Old-chunk conversion
FLAG_BLOCK = "minecraft:reinforced_deepslate"
RETRO_RADIUS = 4        # chunks around each player that get checked
RETRO_BUDGET = 2        # old chunks converted per player per run
RETRO_INTERVAL = "10t"  # how often the loop runs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def target(test, state):
    return {"target": test, "state": {"Name": state}}


def height(kind, lo, hi):
    return {"type": "minecraft:height_range",
            "height": {"type": f"minecraft:{kind}",
                       "min_inclusive": {"absolute": lo},
                       "max_inclusive": {"absolute": min(hi, MAX_UNDERGROUND_Y)}}}


def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def zip_dir(out):
    zpath = out + ".zip"
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in sorted(os.walk(out)):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, out))
    return zpath


def fresh(out, version, description, readme):
    if os.path.exists(out):
        shutil.rmtree(out)
    dump(os.path.join(out, "pack.mcmeta"), {"pack": {
        "pack_format": VERSIONS[version]["pack_format"], "description": description}})
    with open(os.path.join(HERE, readme)) as f:
        text = f.read().replace("{VERSION}", version).replace("{ME}", VERSIONS[version]["me"])
    write_text(os.path.join(out, "README.txt"), text)


# ---------------------------------------------------------------------------
# Pack 1: Middle-earth rocks, ores, plants and animals in the vanilla Overworld
# ---------------------------------------------------------------------------
def build_overworld_pack(version):
    v = VERSIONS[version]
    ME = v["me"]

    def me(name):
        return f"{ME}:{name}"

    def block(name):
        return {"predicate_type": "minecraft:block_match", "block": me(name)}

    configured, placed = {}, {}
    underground = []

    def add_ore(name, targets, size, lo, hi, count=None, rarity=None, kind="trapezoid",
                feature="minecraft:ore"):
        configured[name] = {"type": feature, "config": {
            "size": size, "discard_chance_on_air_exposure": 0.0, "targets": targets}}
        mods = []
        if count is not None:
            mods.append({"type": "minecraft:count", "count": count})
        if rarity is not None:
            mods.append({"type": "minecraft:rarity_filter", "chance": rarity})
        mods += [{"type": "minecraft:in_square"}, height(kind, lo, hi), {"type": "minecraft:biome"}]
        placed[name] = {"feature": f"{NS}:{name}", "placement": mods}
        underground.append(name)

    # 1. Rock layers first, then pockets, then the ores that look for them.
    for rock in v["rocks"]:
        add_ore(f"rock_{rock}", [target(t, me(rock)) for t in BASE_STONES], 48, -24, 16, count=1)
    for rock, rarity in v["rare_rocks"].items():
        add_ore(f"rock_{rock}", [target(t, me(rock)) for t in BASE_STONES], 48, -24, 16, rarity=rarity)
    add_ore("rock_nurgon", [target(t, me("nurgon")) for t in BASE_STONES],
            64, -52, 0, count=6, kind="uniform")
    add_ore("rock_medgon", [target(t, me("medgon")) for t in BASE_STONES],
            64, -64, -28, count=7, kind="uniform")
    add_ore("nurgon_tuff", [target(block("nurgon"), "minecraft:tuff")], 32, -52, 0, count=2)
    add_ore("nurgon_smooth_basalt", [target(block("nurgon"), "minecraft:smooth_basalt")], 32, -52, 0, count=2)
    add_ore("medgon_blackstone", [target(block("medgon"), "minecraft:blackstone")], 32, -64, -28, count=2)

    # 2. Dirt / sand / moss pockets
    for p in COMMON_POCKETS:
        add_ore(f"pocket_{p}", [target(t, me(p)) for t in BASE_STONES], 33, -32, 16, rarity=2)

    # 3. Ores, following the mod's own ore lists
    def shallow(ore):
        out = [target(block(rock), me(prefix + ore) if prefix else f"minecraft:{ore}")
               for rock, prefix in v["ore_sets"].items()]
        out.append(target(CALCITE, me("calcite_" + ore)))
        return out

    add_ore("ore_coal", shallow("coal_ore"), 17, -24, 16, count=20)
    add_ore("ore_copper", shallow("copper_ore"), 15, -24, 16, count=16)
    tin = [target(block(rock), me((prefix or "") + "tin_ore")) for rock, prefix in v["ore_sets"].items()]
    tin += [target(CALCITE, me("calcite_tin_ore")),
            target(block("nurgon"), me("nurgon_tin_ore")),
            target(STONE_TAG, me("tin_ore")),
            target(DEEPSLATE_TAG, me("deepslate_tin_ore"))]
    add_ore("ore_tin", tin, 12, -48, 16, count=12)
    add_ore("ore_quartzite", [target(block(r), me("quartzite")) for r in v["quartzite_in"]]
            + [target(t, me("quartzite")) for t in BASE_STONES], 21, -32, 16, count=2)
    add_ore("ore_lead", [target(block("nurgon"), me("nurgon_lead_ore")),
                         target(block("medgon"), me("medgon_lead_ore")),
                         target(DEEPSLATE_TAG, me("deepslate_lead_ore"))], 12, -64, 0, count=10)
    for metal, size, lo, hi, count in [("iron", 10, -64, 4, 14), ("silver", 7, -64, 0, 6),
                                       ("gold", 5, -64, -8, 4)]:
        add_ore(f"ore_{metal}", [target(block(r), me(f"{r}_{metal}_ore")) for r in ("nurgon", "medgon")],
                size, lo, hi, count=count)
    add_ore("ore_jade", [target(block(r), me("jadeite")) for r in ("nurgon", "medgon")],
            16, -64, 0, count=3)
    for gem, (rocks, size, lo, hi, count) in v["gems"].items():
        add_ore(f"ore_{gem}", [target(block(r), me(f"{r}_{gem}_ore")) for r in rocks],
                size, lo, hi, count=count, feature="minecraft:scattered_ore")
    add_ore("ore_mithril", [target(block("medgon"), me("medgon_mithril_ore"))],
            3, -64, -32, count=3, kind="uniform", feature="minecraft:scattered_ore")

    # 4. Plants, flowers and wild crops
    plants = [p for p in PLANTS if p[0] not in v["plants_removed"]]
    for name, groups, rarity, tries, spread in v["plants_added"]:
        biomes = [b for g in groups.split("+") for b in GROUPS[g]]
        plants.append((name, biomes, rarity, tries, spread))
    vegetation, plant_biomes = [], {}
    for name, biomes, rarity, tries, spread in plants:
        ground = SANDY if (set(biomes) & set(DRY + COAST)) else GROUND
        pid = f"patch_{name}"
        configured[pid] = {"type": "minecraft:random_patch", "config": {
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
        placed[pid] = {"feature": f"{NS}:{pid}", "placement": [
            {"type": "minecraft:rarity_filter", "chance": rarity},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING"},
            {"type": "minecraft:biome"},
        ]}
        vegetation.append(pid)
        plant_biomes[pid] = set(biomes)

    # 5. Chunk flag: new chunks replace the corner bedrock (x0, -64, z0) with
    #    reinforced deepslate so the old-chunk loop knows they are done.
    configured["chunk_flag"] = {"type": "minecraft:simple_block", "config": {
        "to_place": {"type": "minecraft:simple_state_provider", "state": {"Name": FLAG_BLOCK}}}}
    placed["chunk_flag"] = {"feature": f"{NS}:chunk_flag", "placement": [
        {"type": "minecraft:height_range",
         "height": {"type": "minecraft:constant", "value": {"absolute": -64}}},
        {"type": "minecraft:block_predicate_filter",
         "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:bedrock"}},
        {"type": "minecraft:biome"},
    ]}

    # 6. Old-chunk versions of every feature. /place feature only takes
    #    configured features and a nested placed feature can't use the "biome"
    #    modifier, so each is a random_selector whose default is the placed
    #    feature minus that modifier; biomes are checked with biome tags.
    for name in underground + vegetation:
        mods = [m for m in placed[name]["placement"] if m["type"] != "minecraft:biome"]
        configured[f"retro_{name}"] = {"type": "minecraft:random_selector", "config": {
            "features": [], "default": {"feature": f"{NS}:{name}", "placement": mods}}}

    out = os.path.join(BUILD, f"middle-earth-overworld-{version}")
    fresh(out, version, f"Middle-earth rocks, ores, plants & animals in the Overworld (MC {version})",
          "overworld-README.txt")
    for name, data in configured.items():
        dump(os.path.join(out, "data", NS, "worldgen", "configured_feature", name + ".json"), data)
    for name, data in placed.items():
        dump(os.path.join(out, "data", NS, "worldgen", "placed_feature", name + ".json"), data)

    vanilla = os.path.join(HERE, f"vanilla-{version}-biomes")
    for fname in sorted(os.listdir(vanilla)):
        biome = fname[:-5]
        with open(os.path.join(vanilla, fname)) as f:
            data = json.load(f)
        features = data["features"]
        while len(features) <= TOP_LAYER_MODIFICATION:
            features.append([])
        features[UNDERGROUND_ORES] += [f"{NS}:{n}" for n in underground]
        features[VEGETAL_DECORATION] += [f"{NS}:{n}" for n in vegetation if biome in plant_biomes[n]]
        features[TOP_LAYER_MODIFICATION].append(f"{NS}:chunk_flag")
        creatures = data.setdefault("spawners", {}).setdefault("creature", [])
        for entity, weight, lo, hi, biomes in ANIMALS:
            if biome in biomes:
                ns = v["animal_ns"].get(entity, ME)
                creatures.append({"type": f"{ns}:{entity}", "weight": weight,
                                  "minCount": lo, "maxCount": hi})
        dump(os.path.join(out, "data", "minecraft", "worldgen", "biome", fname), data)

    for pid in vegetation:
        dump(os.path.join(out, "data", NS, "tags", "worldgen", "biome", pid + ".json"),
             {"values": [f"minecraft:{b}" for b in sorted(plant_biomes[pid])]})

    for name, lines in retrofit_functions(underground, vegetation).items():
        write_text(os.path.join(out, "data", NS, "function", name + ".mcfunction"), "\n".join(lines) + "\n")
    dump(os.path.join(out, "data", "minecraft", "tags", "function", "load.json"), {"values": [f"{NS}:load"]})
    return out


def retrofit_functions(underground, vegetation):
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
        "$execute unless block $(x) -64 $(z) minecraft:bedrock run return 0",
        f"$execute positioned $(x) 0 $(z) run function {NS}:retrofit/generate",
        f"$setblock $(x) -64 $(z) {FLAG_BLOCK}",
        "scoreboard players remove #budget me_ow 1",
    ]
    gen = [f"place feature {NS}:retro_{n} ~ ~ ~" for n in underground]
    gen += [f"execute if biome ~8 ~64 ~8 #{NS}:{n} run place feature {NS}:retro_{n} ~ ~ ~"
            for n in vegetation]
    f["retrofit/generate"] = gen
    f["retrofit/stop"] = ["scoreboard players set #enabled me_ow 0",
                          'tellraw @s {"text":"Middle-earth Overworld: converting old chunks is OFF","color":"yellow"}']
    f["retrofit/start"] = ["scoreboard players set #enabled me_ow 1",
                           'tellraw @s {"text":"Middle-earth Overworld: converting old chunks is ON","color":"green"}']
    return f


# ---------------------------------------------------------------------------
# Pack 2: the Overworld is the real Middle-earth map
# ---------------------------------------------------------------------------
def build_map_pack(version):
    ME = VERSIONS[version]["me"]
    out = os.path.join(BUILD, f"middle-earth-map-overworld-{version}")
    fresh(out, version, f"The Overworld generates as the Middle-earth map (MC {version})",
          "map-README.txt")
    # Same generator and dimension type the mod uses for its own dimension.
    dump(os.path.join(out, "data", "minecraft", "dimension", "overworld.json"), {
        "type": f"{ME}:middle_earth_type",
        "generator": {"type": f"{ME}:middle_earth",
                      "biome_source": {"type": "minecraft:fixed", "biome": "minecraft:plains"}}})
    x, y, z = MAP_SPAWN
    functions = {
        # World spawn moved once from the map corner (open ocean) to Hobbiton.
        "map/load": [
            "scoreboard objectives add me_map dummy",
            f"execute unless score #spawn_set me_map matches 1 run setworldspawn {x} {y} {z}",
            "scoreboard players set #spawn_set me_map 1",
        ],
    }
    for name, lines in functions.items():
        write_text(os.path.join(out, "data", NS, "function", name + ".mcfunction"), "\n".join(lines) + "\n")
    dump(os.path.join(out, "data", "minecraft", "tags", "function", "load.json"), {"values": [f"{NS}:map/load"]})
    return out


def main():
    os.makedirs(BUILD, exist_ok=True)
    for version in VERSIONS:
        for builder in (build_overworld_pack, build_map_pack):
            print(zip_dir(builder(version)))


if __name__ == "__main__":
    main()
