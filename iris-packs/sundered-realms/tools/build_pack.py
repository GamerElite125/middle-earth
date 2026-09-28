"""Generate every JSON file of the Sundered Realms Iris pack.

usage: python3 build_pack.py --base <path to an Iris 'overworld' pack>

The base overworld pack supplies the dimension-wide systems we inherit unchanged
(hydrology, ores, deposits, cave profile, imported vanilla structures) plus the trees,
clutter objects and snippets referenced below. Run build_objects.py first so the
object manifest (with each structure's vertical offset) exists.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.normpath(os.path.join(HERE, "..", "pack"))
PACK_NAME = "sundered-realms"
MANIFEST = json.load(open(os.path.join(HERE, "objects-manifest.json")))
M = "minecraft:"
written = []


def out(rel, data):
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    written.append(rel)


def B(block, **data):
    d = {"block": block if ":" in block else M + block}
    if data:
        d["data"] = {k: str(v).lower() if isinstance(v, bool) else v for k, v in data.items()}
    return d


def W(block, weight, **data):
    d = B(block, **data)
    d["weight"] = weight
    return d


def layer(blocks, lo=1, hi=1, style=None, zoom=None, slope=None):
    lay = {"minHeight": lo, "maxHeight": hi, "palette": [b if isinstance(b, dict) else B(b) for b in blocks]}
    if style:
        lay["style"] = {"style": style}
    if zoom:
        lay["zoom"] = zoom
    if slope:
        lay["slopeCondition"] = slope
    return lay


def deco(blocks, chance, stack=None, part=None, style=None, zoom=None, top=None, variance=None, whitelist=None):
    d = {"chance": chance, "palette": [b if isinstance(b, dict) else B(b) for b in blocks]}
    if stack:
        d["stackMin"], d["stackMax"] = stack
    if part:
        d["partOf"] = part
    if style:
        d["style"] = {"style": style, "zoom": zoom or 1}
    if top:
        d["topPalette"] = [B(t) for t in top]
    if variance:
        d["variance"] = {"style": variance}
    if whitelist:
        d["whitelist"] = [B(w) for w in whitelist]
    return d


ROT = {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 270, "interval": 90}}


def trees(place, chance, density=1, ty=0, mode=None):
    p = {"place": place, "chance": chance, "density": density, "rotation": ROT}
    if ty:
        p["translate"] = {"y": ty}
    if mode:
        p["mode"] = mode
    return p


def structure(key, chance, mode=None, loot=None, vanilla=None, max_slope=None, clamp=None, extra=None):
    """Placement for one of our generated structures, seated so its y=0 layer replaces the surface."""
    info = MANIFEST[key]
    p = {"place": [key], "chance": chance, "density": 1, "rotation": ROT}
    if info["translateY"]:
        p["translate"] = {"y": info["translateY"]}
    p["mode"] = mode or ("CENTER_HEIGHT" if info["underground"] else "CENTER_STILT")
    if max_slope is not None:
        p["slopeCondition"] = {"minimumSlope": 0, "maximumSlope": max_slope}
    if clamp:
        p["clamp"] = clamp
    if loot:
        p["loot"] = [{"name": n, "weight": w} for n, w in loot]
    if vanilla:
        p["vanillaLoot"] = [{"name": n, "weight": w} for n, w in vanilla]
    if loot or vanilla:
        p["overrideGlobalLoot"] = True
    if extra:
        p.update(extra)
    return p


def custom(cid, category, grass, foliage, water="#3F76E4", water_fog="#050533", fog=None, sky=None,
           downfall="rain", temp=None, humidity=None, particle=None, rarity=100):
    c = {"id": cid, "category": category, "grassColor": grass, "foliageColor": foliage,
         "waterColor": water, "waterFogColor": water_fog, "downfallType": downfall}
    if fog:
        c["fogColor"] = fog
    if sky:
        c["skyColor"] = sky
    if temp is not None:
        c["temperature"] = temp
    if humidity is not None:
        c["humidity"] = humidity
    if particle:
        c["ambientParticle"] = {"particle": particle, "rarity": rarity}
    return c


def biome(key, name, color, derivative, cust, gens, layers, decorators=(), objects=(), procedural=None,
          terrain3d=None, children=(), rarity=1, effects=(), loot=None, spawners=(), wall=None, sea_layers=None,
          river=None, cave_profile=None):
    b = {"name": name, "color": color, "rarity": rarity, "derivative": derivative, "vanillaDerivative": derivative,
         "customDerivitives": [cust]}
    if children:
        b["children"] = list(children)
    b["generators"] = [{"generator": g, "min": lo, "max": hi} for g, lo, hi in gens]
    if wall:
        b["wall"] = wall
    b["layers"] = layers
    if sea_layers:
        b["seaLayers"] = sea_layers
    if objects:
        b["objects"] = list(objects)
    if decorators:
        b["decorators"] = list(decorators)
    if procedural:
        b["proceduralObjects"] = procedural
    if terrain3d:
        b["terrain3D"] = terrain3d
    if effects:
        b["effects"] = list(effects)
    if loot:
        b["loot"] = loot
    if spawners:
        b["entitySpawners"] = list(spawners)
    if river:
        b["riverPolicy"] = river
    if cave_profile:
        b["caveProfile"] = cave_profile
    out(f"biomes/sundered/{key}.json", b)
    return f"sundered/{key}"


def smoke(chance=1, interval=300, kind="CAMPFIRE_SIGNAL_SMOKE"):
    return {"particleEffect": kind, "chance": chance, "interval": interval, "particleCount": 0, "particleOffset": 0,
            "particleAltX": 0.001, "particleAltY": 0.13885, "particleAltZ": 0.001}


def ambient(kind, count=4, offset=10, interval=400, chance=3):
    return {"particleEffect": kind, "chance": chance, "interval": interval, "particleCount": count,
            "particleOffset": offset, "particleAltX": 0.3, "particleAltY": -0.2, "particleAltZ": 0.3}


def t3d(seed, amp, hscale=160, vscale=30, style="SIMPLEX", crack_depth=0, crack_width=0, crack_scale=380,
        crack_style="SIMPLEX", min_slope=0.2, fade=0.3):
    return {"enabled": True, "seed": seed, "amplitude": amp, "horizontalScale": hscale, "verticalScale": vscale,
            "densityStyle": {"style": style}, "crackDepth": crack_depth, "crackWidth": crack_width,
            "crackScale": crack_scale, "crackStyle": {"style": crack_style}, "minimumSlope": min_slope,
            "slopeFade": fade, "fluidClearance": 8, "fluidFade": 24}


def ptree(name, seed, chance, trunk, leaves, profile, hmin, hmax, width=1, density=1, lean=0, extra=None):
    t = {"name": name, "chance": chance, "density": density, "variants": 10, "seed": seed, "mode": "CENTER_HEIGHT",
         "rotation": {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 360, "interval": 45}},
         "trunk": trunk, "leaves": leaves, "profile": profile, "heightMin": hmin, "heightMax": hmax,
         "trunkWidth": width, "translate": {"y": 0}}
    if lean:
        t["leanAngle"] = lean
    if extra:
        t.update(extra)
    return t


def ruin(name, seed, chance, form, block, weathered, hmin, hmax, wmin=1, wmax=3, lmin=3, lmax=7, moss=0.45,
         erosion=0.3, accents=None, palette=None):
    r = {"name": name, "chance": chance, "density": 1, "variants": 8, "seed": seed, "mode": "MIN_HEIGHT",
         "rotation": {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 360, "interval": 90}},
         "form": form, "block": block, "weatheredBlock": weathered, "heightMin": hmin, "heightMax": hmax,
         "widthMin": wmin, "widthMax": wmax, "lengthMin": lmin, "lengthMax": lmax, "mossiness": moss,
         "erosion": erosion, "buriedFraction": 0.2}
    if palette:
        r["blockPalette"] = {"palette": [W(b, w) for b, w in palette]}
    if accents:
        r["accents"] = accents
    return r


def formation(name, seed, chance, form, block, hmin, hmax, bmin, bmax, top=0, cap=None, strata=None, extra=None,
              density=1):
    f = {"name": name, "chance": chance, "density": density, "variants": 12, "seed": seed, "mode": "CENTER_HEIGHT",
         "carvingSupport": "SURFACE_ONLY", "surfaceSupportBuffer": 1,
         "rotation": {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 360, "interval": 45}},
         "form": form, "block": block, "heightMin": hmin, "heightMax": hmax, "baseWidthMin": bmin,
         "baseWidthMax": bmax, "topWidth": top, "translate": {"y": -2}, "roughness": 0.15, "jitter": 0.03}
    if cap:
        f["capBlock"] = cap
    if strata:
        f["strataPalette"] = {"palette": [B(s) for s in strata]}
        f["strataThickness"] = 2
    if extra:
        f.update(extra)
    return f


# ============================================================================ loot tables
def loot_item(t, lo=1, hi=1, rarity=1, name=None, lore=None, ench=None, **kw):
    d = {"type": t, "minAmount": lo, "maxAmount": hi, "rarity": rarity, "slotTypes": "STORAGE"}
    if name:
        d["displayName"] = name
    if lore:
        d["lore"] = lore
    if ench:
        d["enchantments"] = [{"enchantment": e, "minLevel": a, "maxLevel": b, "chance": c} for e, a, b, c in ench]
    d.update(kw)
    return d


LOOT = {
    "azure-temple": ("Sun Serpent Hoard", 1, 3, 6, [
        loot_item("gold_ingot", 2, 9), loot_item("emerald", 1, 6, 2), loot_item("cocoa_beans", 2, 8),
        loot_item("gold_nugget", 5, 20), loot_item("prismarine_shard", 2, 8, 2), loot_item("diamond", 1, 2, 8),
        loot_item("golden_apple", 1, 1, 10), loot_item("enchanted_golden_apple", 1, 1, 60),
        loot_item("golden_sword", 1, 1, 14, "&6Fang of Kukul-Vaan", ["&7Forged in the sun-serpent's venom."],
                  [("sharpness", 3, 5, 1.0), ("fire_aspect", 1, 2, 0.6)]),
        loot_item("totem_of_undying", 1, 1, 40, "&aJade Idol of Rebirth"),
        loot_item("music_disc_pigstep", 1, 1, 90)]),
    "azure-pirate": ("Buccaneer's Chest", 1, 3, 6, [
        loot_item("gold_ingot", 1, 6), loot_item("emerald", 1, 4, 2), loot_item("honey_bottle", 1, 3, 2, "&6Bottle of Black Rum"),
        loot_item("gunpowder", 2, 8), loot_item("map", 1, 1, 3), loot_item("compass", 1, 1, 4),
        loot_item("heart_of_the_sea", 1, 1, 30), loot_item("nautilus_shell", 1, 2, 8),
        loot_item("iron_sword", 1, 1, 10, "&eCutlass of Captain Morrow", None, [("sharpness", 1, 3, 1.0), ("looting", 1, 2, 0.5)])]),
    "ashfang-warchest": ("Ashfang War-Chest", 1, 3, 6, [
        loot_item("rotten_flesh", 3, 12), loot_item("bone", 2, 8), loot_item("iron_ingot", 1, 6, 2),
        loot_item("iron_axe", 1, 1, 4, "&cOrc Cleaver", None, [("sharpness", 1, 3, 0.8)]),
        loot_item("crossbow", 1, 1, 6), loot_item("arrow", 4, 16, 2), loot_item("netherite_scrap", 1, 1, 30),
        loot_item("goat_horn", 1, 1, 12, "&4Warhorn of the Ashfang"),
        loot_item("netherite_axe", 1, 1, 80, "&4Skullsplitter", ["&8Wielded by Warlord Grom Bloodtusk."],
                  [("sharpness", 4, 5, 1.0), ("unbreaking", 2, 3, 1.0)])]),
    "dreadmire-crypt": ("Mire-Crypt Offering", 1, 3, 5, [
        loot_item("bone", 2, 10), loot_item("spider_eye", 1, 4), loot_item("slime_ball", 1, 5, 2),
        loot_item("glass_bottle", 1, 4), loot_item("redstone", 2, 10, 2), loot_item("glowstone_dust", 2, 8, 2),
        loot_item("potion", 1, 1, 6), loot_item("ender_pearl", 1, 2, 8),
        loot_item("golden_hoe", 1, 1, 25, "&2Hag's Sickle", ["&7It hums with swamp-rot."], [("sharpness", 3, 5, 1.0)]),
        loot_item("echo_shard", 1, 2, 30)]),
    "frontier-strongbox": ("Frontier Strongbox", 1, 3, 6, [
        loot_item("gold_nugget", 6, 24), loot_item("gold_ingot", 1, 5, 2), loot_item("raw_gold", 1, 6, 2),
        loot_item("leather", 2, 6), loot_item("saddle", 1, 1, 5), loot_item("lead", 1, 2, 4),
        loot_item("crossbow", 1, 1, 8, "&6Old Faithful", ["&7Six notches on the stock."], [("quick_charge", 2, 3, 1.0), ("piercing", 1, 3, 0.5)]),
        loot_item("tnt", 1, 4, 6), loot_item("golden_horse_armor", 1, 1, 20), loot_item("diamond", 1, 3, 15)]),
    "everbloom-arcane": ("Conclave Reliquary", 1, 3, 5, [
        loot_item("lapis_lazuli", 4, 16), loot_item("amethyst_shard", 2, 10), loot_item("book", 1, 4),
        loot_item("experience_bottle", 2, 8, 2), loot_item("glow_berries", 2, 8), loot_item("ender_eye", 1, 2, 10),
        loot_item("blaze_rod", 1, 3, 8), loot_item("book", 1, 1, 12, "&dTome of the First Bloom",
                                                  ["&7Pressed petals mark every page."]),
        loot_item("trident", 1, 1, 60, "&bTideweaver's Staff"), loot_item("elytra", 1, 1, 150, "&fWings of the Sylph")]),
    "crownlands-market": ("Merchant's Coffer", 1, 4, 7, [
        loot_item("bread", 2, 8), loot_item("wheat", 4, 16), loot_item("emerald", 1, 8, 2), loot_item("iron_ingot", 1, 4, 2),
        loot_item("white_wool", 2, 8), loot_item("red_dye", 1, 4), loot_item("paper", 2, 8), loot_item("apple", 2, 6),
        loot_item("name_tag", 1, 1, 12), loot_item("shield", 1, 1, 8, "&9Crownguard Shield")]),
    "warscar-spoils": ("Spoils of the Broken Oath", 1, 3, 6, [
        loot_item("iron_nugget", 4, 18), loot_item("arrow", 4, 20), loot_item("chainmail_helmet", 1, 1, 5),
        loot_item("chainmail_chestplate", 1, 1, 7), loot_item("iron_sword", 1, 1, 6, "&7Oathbreaker's Blade", None,
                                                               [("sharpness", 2, 4, 1.0)]),
        loot_item("shield", 1, 1, 4), loot_item("bone", 2, 8), loot_item("coal", 2, 10), loot_item("diamond", 1, 2, 18),
        loot_item("golden_apple", 1, 1, 15)]),
    "umbral-reliquary": ("Ossuary Reliquary", 1, 3, 5, [
        loot_item("bone", 4, 14), loot_item("wither_rose", 1, 2, 10), loot_item("candle", 2, 6),
        loot_item("soul_lantern", 1, 3, 3), loot_item("echo_shard", 1, 3, 10), loot_item("diamond", 1, 3, 10),
        loot_item("netherite_scrap", 1, 2, 25),
        loot_item("netherite_sword", 1, 1, 90, "&5Grief, Blade of the Hollow King", ["&8It drinks the light."],
                  [("sharpness", 4, 5, 1.0), ("smite", 3, 5, 0.5)]),
        loot_item("recovery_compass", 1, 1, 20, "&3Compass of the Lost")]),
}


def write_loot():
    for key, (name, rarity, lo, hi, items) in LOOT.items():
        out(f"loot/sundered/{key}.json", {"name": name, "rarity": rarity, "minPicked": lo, "maxPicked": hi,
                                          "maxTries": 24, "loot": items})


# ============================================================================ monsters
def ent(key, etype, name=None, helmet=None, chest=None, legs=None, boots=None, hand=None, surface="LAND", extra=None):
    e = {"type": M + etype, "reason": "NATURAL", "removable": True, "surface": surface}
    if name:
        e["customName"] = name
    for slot, item in (("helmet", helmet), ("chestplate", chest), ("leggings", legs), ("boots", boots), ("mainHand", hand)):
        if item:
            e[slot] = item if isinstance(item, dict) else {"type": item}
    if extra:
        e.update(extra)
    out(f"entities/sundered/{key}.json", e)
    return f"sundered/{key}"


def dyed(t, color):
    return {"type": t, "leatherColor": color}


def spawner(key, spawns, group="NORMAL", night=False, per_chunk=2, rate=6):
    s = {"group": group, "maximumRate": {"amount": rate, "per": {"seconds": 20}}, "maxEntitiesPerChunk": per_chunk,
         "weather": "ANY", "spawns": [{"entity": e, "rarity": r, "minSpawns": lo, "maxSpawns": hi} for e, r, lo, hi in spawns]}
    if night:
        s["timeBlock"] = {"startHour": 19, "endHour": 5}
    out(f"spawners/sundered/{key}.json", s)
    return f"sundered/{key}"


def write_monsters():
    E = {}
    E["orc"] = ent("ashfang-orc", "zombie", "&2Ashfang Orc", dyed("leather_helmet", "#3B2A1A"), dyed("leather_chestplate", "#4A3B22"),
                   hand="stone_axe")
    E["orc_brute"] = ent("ashfang-brute", "vindicator", "&4Ashfang Brute", {"type": "iron_helmet"}, hand="iron_axe")
    E["orc_archer"] = ent("ashfang-skirmisher", "pillager", "&6Ashfang Skirmisher", dyed("leather_helmet", "#5C1A1A"))
    E["direwolf"] = ent("ashfang-direwolf", "wolf", "&8Ashfang Direwolf", extra={"attributes": [{"attribute": "max_health", "name": "sundered-direwolf-health", "operation": "ADD_NUMBER", "minAmount": 10, "maxAmount": 14, "chance": 1}]})
    E["bog_wight"] = ent("bog-wight", "bogged", "&2Bog Wight")
    E["mire_hag"] = ent("mire-hag", "witch", "&aMire Hag")
    E["drowned"] = ent("fen-drowned", "drowned", "&3Fen-Drowned", surface="WATER")
    E["revenant"] = ent("dust-revenant", "husk", "&eDust Revenant", dyed("leather_helmet", "#6B4A2B"))
    E["outlaw"] = ent("desperado", "pillager", "&6Desperado", dyed("leather_helmet", "#2B2B2B"), dyed("leather_chestplate", "#7A5230"))
    E["sentinel"] = ent("temple-sentinel", "husk", "&aJade Sentinel", {"type": "golden_helmet"}, hand="golden_sword")
    E["sunken_pirate"] = ent("sunken-pirate", "drowned", "&bSunken Buccaneer", dyed("leather_helmet", "#111111"), hand="iron_sword",
                             surface="WATER")
    E["jaguar"] = ent("jaguar", "ocelot", surface="ANIMAL")
    E["parrot"] = "standard/passive/parrot"
    E["fallen"] = ent("fallen-soldier", "skeleton", "&7Fallen Soldier", {"type": "iron_helmet"}, {"type": "chainmail_chestplate"},
                      hand="iron_sword")
    E["deserter"] = ent("deserter", "vindicator", "&8Oathbreaker Deserter", {"type": "chainmail_helmet"})
    E["grave_knight"] = ent("grave-knight", "wither_skeleton", "&5Grave Knight", {"type": "chainmail_helmet"},
                            {"type": "netherite_chestplate"}, hand="stone_sword")
    E["revenant_frost"] = ent("hollow-revenant", "stray", "&3Hollow Revenant")
    E["wisp"] = ent("will-o-wisp", "allay", "&bWill-o'-Wisp", surface="ANIMAL", extra={"glowing": True})
    E["fae_fox"] = ent("fae-fox", "fox", surface="ANIMAL")
    E["merchant"] = ent("travelling-merchant", "wandering_trader", "&6Travelling Merchant", surface="ANIMAL")
    E["knight"] = ent("crown-sentry", "iron_golem", "&9Crown Sentry", surface="ANIMAL")
    S = {}
    S["azure"] = [
        spawner("azure-wildlife", [(E["jaguar"], 3, 1, 1), (E["parrot"], 2, 1, 3), ("standard/passive/turtle", 4, 1, 2),
                                   ("standard/neutral/panda", 8, 1, 1)], per_chunk=3),
        spawner("azure-night", [(E["sentinel"], 3, 1, 2), ("standard/hostile/zombie", 3, 1, 2), (E["sunken_pirate"], 5, 1, 2),
                                ("standard/neutral/spider", 4, 1, 1)], night=True),
        "tropical/water", "tropical/beach"]
    S["ashfang"] = [spawner("ashfang-warbands", [(E["orc"], 1, 2, 4), (E["orc_brute"], 4, 1, 1), (E["orc_archer"], 3, 1, 2),
                                                  (E["direwolf"], 5, 1, 2)], per_chunk=4, rate=8)]
    S["dreadmire"] = [spawner("dreadmire-haunts", [(E["bog_wight"], 1, 1, 3), (E["mire_hag"], 5, 1, 1), ("standard/hostile/slime", 2, 1, 3),
                                                    (E["drowned"], 3, 1, 2)], per_chunk=3),
                      "swamp/passive", "swamp/water"]
    S["frontier"] = [spawner("frontier-outlaws", [(E["outlaw"], 2, 1, 3), (E["revenant"], 2, 1, 3), ("standard/neutral/spider", 5, 1, 1)],
                             night=False, per_chunk=2),
                     spawner("frontier-herds", [("standard/passive/horse", 2, 2, 5), ("standard/passive/camel", 3, 1, 2),
                                                ("standard/passive/rabbit", 2, 1, 3), ("standard/passive/cow", 3, 2, 4)], per_chunk=3)]
    S["everbloom"] = [spawner("everbloom-fae", [(E["wisp"], 4, 1, 2), (E["fae_fox"], 2, 1, 3), ("standard/passive/rabbit", 2, 1, 3),
                                                 ("standard/passive/sheep", 3, 2, 4)], per_chunk=3),
                      spawner("everbloom-night", [("standard/hostile/zombie", 2, 1, 2), ("standard/neutral/spider", 3, 1, 1)], night=True)]
    S["crownlands"] = [spawner("crownlands-roads", [(E["merchant"], 12, 1, 1), (E["knight"], 20, 1, 1), ("standard/passive/cow", 2, 2, 4),
                                                     ("standard/passive/sheep", 2, 2, 4), ("standard/passive/horse", 4, 2, 3),
                                                     ("standard/passive/pig", 3, 1, 3)], per_chunk=3),
                       "temperate/hostile"]
    S["warscar"] = [spawner("warscar-restless", [(E["fallen"], 1, 1, 3), (E["deserter"], 4, 1, 2), ("standard/hostile/zombie", 2, 2, 4)],
                            per_chunk=4, rate=8)]
    S["umbral"] = [spawner("umbral-damned", [(E["grave_knight"], 3, 1, 2), (E["revenant_frost"], 2, 1, 3),
                                              ("standard/hostile/skeleton", 2, 1, 3), ("standard/neutral/enderman", 8, 1, 1)],
                           per_chunk=3, rate=7),
                   "tundra/passive"]
    return S


# ============================================================================ generators
def write_generators():
    out("generators/sundered/cay.json", {
        "surfaceDetail": 0.4, "seed": 810001,
        "interpolator": {"function": "BILINEAR_STARCAST_6", "horizontalScale": 22},
        "composite": [{"style": {"style": "SIMPLEX", "zoom": 1.4, "fracture": {"style": "FRACTAL_WATER", "zoom": 0.4, "multiplier": 12}},
                       "seed": 810011, "bezier": True, "exponent": 1.4}]})
    out("generators/sundered/volcano-cone.json", {
        "surfaceDetail": 0.6, "seed": 810002,
        "interpolator": {"function": "BILINEAR_STARCAST_6", "horizontalScale": 12},
        "composite": [
            {"style": {"style": "CELLULAR_HEIGHT", "zoom": 3.2}, "seed": 810021, "exponent": 1.8, "opacity": 1},
            {"style": {"style": "FRACTAL_RM_SIMPLEX", "zoom": 0.35}, "seed": 810022, "opacity": 0.18}]})
    out("generators/sundered/bog.json", {
        "surfaceDetail": 0.3, "seed": 810003,
        "interpolator": {"function": "BILINEAR_STARCAST_3", "horizontalScale": 8},
        "composite": [{"style": {"style": "FRACTAL_WATER", "zoom": 0.45}, "seed": 810031},
                      {"style": {"style": "SIMPLEX", "zoom": 0.12}, "seed": 810032, "opacity": 0.35}]})
    out("generators/sundered/mesa-terrace.json", {
        "surfaceDetail": 0.5, "seed": 810004,
        "interpolator": {"function": "BILINEAR_STARCAST_9", "horizontalScale": 30},
        "composite": [{"style": {"style": "IRIS_THICK", "zoom": 1.1, "fracture": {"style": "IRIS_HALF", "zoom": 0.3, "multiplier": 14}},
                       "seed": 810041, "bezier": True, "exponent": 1.1}],
        "cliffHeightMin": 22, "cliffHeightMax": 58,
        "cliffHeightGenerator": {"style": {"style": "NOWHERE"}, "seed": 810042, "zoom": 3.4, "octaves": 3, "enabled": True,
                                 "opacity": 1, "exponent": 1.1}})
    out("generators/sundered/craters.json", {
        "surfaceDetail": 0.5, "seed": 810005,
        "interpolator": {"function": "BILINEAR_STARCAST_6", "horizontalScale": 16},
        "composite": [{"style": {"style": "CRATER", "zoom": 0.9}, "seed": 810051, "opacity": 0.8},
                      {"style": {"style": "PERLIN_IRIS", "zoom": 1.2}, "seed": 810052, "opacity": 0.5}]})
    out("generators/sundered/gravespires.json", {
        "surfaceDetail": 0.7, "seed": 810006,
        "interpolator": {"function": "BILINEAR_STARCAST_6", "horizontalScale": 18},
        "composite": [{"style": {"style": "CELLULAR_HEIGHT_IRIS", "zoom": 1.6}, "seed": 810061, "exponent": 2.2},
                      {"style": {"style": "FRACTAL_RM_SIMPLEX", "zoom": 0.5}, "seed": 810062, "opacity": 0.3}]})


# ============================================================================ biomes
def grass_top(block="grass_block"):
    return layer([block])


SOIL = "snippet/biome-palette/soil/dirt-3-3-flat3"
STONE = "snippet/biome-palette/stone/andesite-blend-6-18"


def azure(S, sea_spawn):
    sp = S["azure"]
    temple_loot = [("sundered/azure-temple", 3)]
    temple_vanilla = [(M + "chests/jungle_temple", 2), (M + "chests/buried_treasure", 1)]
    trop = lambda cid, **kw: custom(cid, "jungle", kw.pop("grass", "#3DD62C"), kw.pop("foliage", "#29B51C"), water="#27D6C9",
                                    water_fog="#0E6E86", temp=0.95, humidity=0.9, **kw)
    palms = ptree("azure-palm", 71001, 0.55, M + "jungle_log", M + "jungle_leaves", "PALM", 7, 13, lean=18, density=2)
    palms_tall = ptree("azure-royal-palm", 71002, 0.35, M + "stripped_jungle_log", M + "jungle_leaves", "PALM", 11, 17, lean=10)
    L = {}
    L["palm-cays"] = biome("azure/palm-cays", "Palm Cays", "#F4E7B0", M + "beach",
                           trop("sundered_palm_cays", grass="#6BE04A", foliage="#43C92D"),
                           [("sundered/cay", 1, 9)],
                           [layer(["sand"], 1, 3), layer(["sandstone"], 2, 4), STONE],
                           decorators=[deco(["short_grass", "fern"], 0.12), deco(["dead_bush"], 0.01),
                                       deco(["sugar_cane"], 0.02, (1, 3)), "snippet/decorator/sea/tall-seagrass-c0-2"],
                           objects=[structure("sundered/azure/serpent-stela", 0.008),
                                    structure("sundered/azure/pirate-cove", 0.004, loot=[("sundered/azure-pirate", 3)],
                                              vanilla=[(M + "chests/shipwreck_treasure", 2)])],
                           procedural={"trees": [palms, palms_tall]}, spawners=sp)
    L["jungle-highlands"] = biome("azure/jungle-highlands", "Serpent Jungle Highlands", "#118A3B", M + "jungle",
                                  trop("sundered_serpent_jungle"),
                                  [("mountain", 25, 60)],
                                  [grass_top(), layer(["dirt", "coarse_dirt"], 2, 4), STONE],
                                  wall="snippet/biome-palette/wall/jungle-wood-leaves",
                                  decorators=["snippet/decorator/grass/jungle-undergrowth-c0-45",
                                              deco(["fern", "large_fern"], 0.2), "snippet/decorator/twigs/jungle-c0-01"],
                                  objects=[trees(["trees/jungle/cocogeneric2", "trees/jungle/cocogeneric3", "trees/jungle/lgeneric1",
                                                  "trees/jungle/lgeneric2", "trees/jungle/lgeneric3", "trees/jungle/lgeneric6"], 0.45, 2, -2),
                                           "snippet/object-placer/trees/jungle-sgeneric-organic-stilt-c0-45",
                                           structure("sundered/azure/sun-serpent-pyramid", 0.0035, loot=temple_loot,
                                                     vanilla=temple_vanilla, max_slope=4),
                                           structure("sundered/azure/jungle-shrine", 0.015, loot=temple_loot, max_slope=5),
                                           structure("sundered/azure/serpent-stela", 0.02)],
                                  procedural={"ruins": [
                                      ruin("serpent-pillar", 72001, 0.05, "PILLAR", M + "mossy_stone_bricks", M + "cracked_stone_bricks", 4, 11),
                                      ruin("jungle-arch", 72002, 0.02, "ARCH", M + "stone_bricks", M + "mossy_stone_bricks", 6, 10, 1, 2, 5, 8),
                                      ruin("plaza-slab", 72003, 0.03, "FLOOR_SLAB", M + "mossy_stone_bricks", M + "moss_block", 1, 1, 4, 8, 5, 10)]},
                                  terrain3d="snippet/terrain-3d/hilly/amp18-nowhere-crack416",
                                  effects=[ambient("TOTEM_OF_UNDYING", 2, 12, 600)], spawners=sp)
    L["cenote-jungle"] = biome("azure/cenote-jungle", "Cenote Jungle", "#1FA35A", M + "jungle",
                               trop("sundered_cenote_jungle", grass="#35C22A"),
                               [("rare-hills", 12, 30)],
                               [layer(["grass_block", "moss_block"], style="SIMPLEX", zoom=0.2),
                                layer(["dirt"], 2, 3), layer(["calcite", "smooth_basalt"], 1, 2, style="SIMPLEX"), STONE],
                               decorators=["snippet/decorator/grass/jungle-undergrowth-c0-45", deco(["moss_carpet"], 0.08),
                                           "snippet/decorator/plants/bamboo-c0-0049"],
                               objects=["snippet/object-placer/trees/jungle-coco-lgeneric-organic-stilt-c0-4-d2",
                                        structure("sundered/azure/cenote-temple", 0.006, loot=temple_loot, vanilla=temple_vanilla, max_slope=4),
                                        structure("sundered/azure/jungle-shrine", 0.01, loot=temple_loot)],
                               procedural={"trees": [palms_tall]}, spawners=sp)
    L["mangrove-lagoon"] = biome("azure/mangrove-lagoon", "Mangrove Lagoon", "#4F8A3A", M + "mangrove_swamp",
                                 trop("sundered_mangrove_lagoon", grass="#5FA33B", foliage="#6BB53C"),
                                 [("sundered/bog", -3, 3)],
                                 [layer(["mud", "mud", "muddy_mangrove_roots"], 1, 2), layer(["clay", "mud"], 1, 3), STONE],
                                 decorators=[deco(["lily_pad"], 0.12, part="SEA_SURFACE"), deco(["seagrass"], 0.3, part="SEA_FLOOR"),
                                             deco(["mangrove_propagule[age=4,hanging=false,stage=0,waterlogged=false]"], 0.02)],
                                 objects=[trees(["trees/mangrove/mangrove1", "trees/mangrove/mangrove2", "trees/mangrove/mangrove3",
                                                 "trees/mangrove/mangrove4", "trees/mangrove/mangrove5", "trees/mangrove/tree1",
                                                 "trees/mangrove/tree2", "trees/mangrove/tree3"], 0.6, 2, -1),
                                          structure("sundered/azure/pirate-cove", 0.004, loot=[("sundered/azure-pirate", 3)])],
                                 spawners=sp)
    L["volcanic-isle"] = biome("azure/volcanic-isle", "Emberpeak Volcano", "#8C1E1E", M + "stony_peaks",
                               custom("sundered_emberpeak", "extreme_hills", "#8A8F2A", "#7E8A28", fog="#C9723A", sky="#D9885A",
                                      downfall="none", temp=1.6, humidity=0.1, particle=M + "ash", rarity=40),
                               [("sundered/volcano-cone", 30, 170)],
                               [layer(["basalt[axis=y]", "blackstone", "tuff", "magma_block"], 1, 2, style="SIMPLEX", zoom=0.3),
                                layer(["blackstone"], 3, 9), layer(["tuff"], 1, 3)],
                               decorators=[deco(["fire"], 0.004), deco(["dead_bush"], 0.01)],
                               objects=[structure("sundered/azure/volcano-caldera", 0.12, mode="MAX_HEIGHT",
                                                  clamp={"minimumHeight": 170, "maximumHeight": 2048}),
                                        structure("sundered/azure/ember-temple", 0.004, loot=temple_loot,
                                                  vanilla=[(M + "chests/ruined_portal", 1), (M + "chests/bastion_treasure", 1)], max_slope=4)],
                               procedural={"formations": [formation("lava-vent-column", 73001, 0.2, "BASALT_COLUMN", M + "basalt", 4, 10, 2, 3,
                                                                    cap=M + "magma_block")]},
                               terrain3d=t3d(30137, 36, 144, 28, "HEXAGON", 5, 2, 336),
                               effects=[smoke(), smoke(1, 450, "LARGE_SMOKE")],
                               river={"placement": "PREFERRED_HEADWATER", "routing": "PREFER", "outletAdmission": True,
                                      "profiles": ["volcanic_lava"], "surfaceBiomes": [], "mouthBiomes": [], "shoreBiomes": [],
                                      "bankBiomes": [], "floodedCaveBiomes": [], "surfacePools": ["volcanic_pool"],
                                      "surfaceSourceDensity": 6.0, "surfaceSourceSpacing": 128, "surfaceTributaries": 2,
                                      "surfaceInlandOutlets": 3, "surfaceCoastalOutlets": 0, "widthMultiplier": 0.5,
                                      "depthMultiplier": 1.25, "routingMultiplier": 0.5, "bankMultiplier": 1.0, "shoreWidth": 1.0,
                                      "surfaceMinimumCourseLength": 128, "surfaceMaximumIncision": 24},
                               spawners=sp)
    L["ember-slopes"] = biome("azure/ember-slopes", "Ember Slopes", "#6E3B1E", M + "savanna",
                              custom("sundered_ember_slopes", "savanna", "#9FA83A", "#8F9E36", fog="#D5A57A", temp=1.4, humidity=0.3,
                                     particle=M + "white_ash", rarity=90),
                              [("mountain", 20, 55)],
                              [layer(["coarse_dirt", "grass_block", "tuff", "basalt[axis=y]"], 1, 1, style="SIMPLEX", zoom=0.4),
                               layer(["dirt", "tuff"], 2, 4), STONE],
                              decorators=["snippet/decorator/grass/dry-grass", deco(["dead_bush"], 0.03)],
                              objects=["snippet/object-placer/trees/acacia-savannas-c0-04",
                                       structure("sundered/azure/ember-temple", 0.004, loot=temple_loot, max_slope=4),
                                       structure("sundered/azure/serpent-stela", 0.01)],
                              procedural={"trees": [palms]},
                              terrain3d="snippet/terrain-3d/rugged/amp30-perlin-crack448", spawners=sp)
    shore = biome("azure/white-sand-beach", "White Sand Beach", "#FFF6D5", M + "beach",
                  trop("sundered_white_beach", grass="#7BE35A"), [("flat", 0, 3)],
                  [layer(["sand", "sand", "sand", "white_concrete_powder"], 2, 4, style="SIMPLEX", zoom=0.5), layer(["sandstone"], 2, 3)],
                  decorators=[deco(["sea_pickle[pickles=2,waterlogged=true]"], 0.02, part="SEA_FLOOR"),
                              deco(["turtle_egg[eggs=2,hatch=0]"], 0.002)],
                  procedural={"trees": [ptree("azure-beach-palm", 71003, 0.25, M + "jungle_log", M + "jungle_leaves", "PALM", 6, 11, lean=28)]},
                  spawners=sp)
    shallows = biome("azure/turquoise-shallows", "Turquoise Shallows", "#2EE6D6", M + "warm_ocean",
                     custom("sundered_turquoise_shallows", "ocean", "#6BE04A", "#43C92D", water="#2DEBD9", water_fog="#0B8FA6", temp=0.9),
                     [("sundered/cay", -14, 4)],
                     [layer(["sand", "sand", "white_concrete_powder"], 2, 4, style="SIMPLEX", zoom=0.4), layer(["sandstone"], 2, 3)],
                     decorators=["snippet/decorator/sea/tall-seagrass-c0-2", deco(["sea_pickle[pickles=3,waterlogged=true]"], 0.02, part="SEA_FLOOR"),
                                 "snippet/decorator/sea/fire-coral-c0-01",
                                 deco(["tube_coral", "brain_coral", "bubble_coral", "horn_coral", "fire_coral_fan", "tube_coral_fan"], 0.08,
                                      part="SEA_FLOOR")],
                     procedural={"coral": [
                         {"name": "azure-brain", "chance": 0.3, "density": 2, "variants": 8, "seed": 74001, "mode": "CENTER_HEIGHT",
                          "underwater": True, "waterlogged": True, "form": "BRAIN", "block": M + "brain_coral_block",
                          "heightMin": 2, "heightMax": 4, "brainRadius": 2},
                         {"name": "azure-branch", "chance": 0.4, "density": 2, "variants": 8, "seed": 74002, "mode": "CENTER_HEIGHT",
                          "underwater": True, "waterlogged": True, "form": "BRANCHING", "block": M + "tube_coral_block",
                          "tipBlock": M + "tube_coral", "heightMin": 3, "heightMax": 7},
                         {"name": "azure-fan", "chance": 0.3, "density": 1, "variants": 8, "seed": 74003, "mode": "CENTER_HEIGHT",
                          "underwater": True, "waterlogged": True, "form": "FAN", "block": M + "fire_coral_block",
                          "heightMin": 3, "heightMax": 6, "fanWidth": 4}],
                         "trees": [ptree("azure-islet-palm", 71004, 0.1, M + "jungle_log", M + "jungle_leaves", "PALM", 6, 10, lean=20)]},
                     spawners=[sea_spawn["azure"]])
    return {"land": list(L.values()), "shore": [shore], "sea": [shallows, "ocean/rich-oceans", "vanilla/deep_lukewarm_ocean"],
            "cave": ["carving/jungle", "carving/lush", "carving/volcanic", "carving/drip"], "color": "#1EC8A8",
            "name": "The Azure Isles"}


def ashfang(S):
    sp = S["ashfang"]
    loot = [("sundered/ashfang-warchest", 3)]
    vanilla = [(M + "chests/pillager_outpost", 2), (M + "chests/bastion_other", 1)]
    blight = lambda cid, **kw: custom(cid, kw.pop("cat", "desert"), kw.pop("grass", "#6B5A3A"), kw.pop("foliage", "#5A4A2E"),
                                      water="#4A2A2A", water_fog="#1A0808", fog=kw.pop("fog", "#6A3A2A"), sky=kw.pop("sky", "#7A3A30"),
                                      downfall="none", temp=1.2, humidity=0.0, **kw)
    camp = structure("sundered/ashfang/orc-warcamp", 0.012, loot=loot, vanilla=vanilla, max_slope=4)
    fort = structure("sundered/ashfang/skullgate-fortress", 0.003, loot=loot, vanilla=vanilla, max_slope=3)
    L = [
        biome("ashfang/blighted-wastes", "Blighted Wastes", "#5A4A3A", M + "badlands",
              blight("sundered_blighted_wastes", particle=M + "ash", rarity=120),
              [("plain", 6, 22)],
              [layer(["coarse_dirt", "soul_soil", "packed_mud", "gravel", "rooted_dirt"], 1, 2, style="CELLULAR", zoom=0.12),
               layer(["dirt", "coarse_dirt"], 2, 4), STONE],
              decorators=[deco(["dead_bush"], 0.05), deco(["crimson_roots"], 0.02),
                          deco(["bone_block[axis=y]"], 0.002, (1, 3)), "snippet/decorator/grass/dry-grass"],
              objects=[camp, fort, structure("sundered/ashfang/bone-totem", 0.02), structure("sundered/ashfang/blood-altar", 0.01),
                       trees(["trees/oak/dead1", "trees/oak/dead2", "trees/oak/dead3", "trees/oak/dead4"], 0.08),
                       "snippet/object-placer/clutter/bone-c0-006-d1-weathered"],
              effects=[ambient("CRIMSON_SPORE", 3, 10, 400)], spawners=sp),
        biome("ashfang/bloodrock-crags", "Bloodrock Crags", "#7A2A22", M + "eroded_badlands",
              blight("sundered_bloodrock", grass="#7A4A3A", fog="#8A3A2A"),
              [("cracked-cliffs", 20, 70)],
              [layer(["red_terracotta", "red_nether_bricks", "netherrack", "terracotta"], 1, 2, style="SIMPLEX", zoom=0.25),
               layer(["red_terracotta", "brown_terracotta", "terracotta"], 4, 12, style="STRATA", zoom=0.5), STONE],
              decorators=[deco(["crimson_roots", "crimson_fungus"], 0.03), deco(["dead_bush"], 0.02)],
              objects=[fort, structure("sundered/ashfang/blood-altar", 0.015),
                       "snippet/object-placer/clutter/bonespire-c0-003-d1-weathered"],
              procedural={"formations": [formation("blood-spire", 75001, 0.25, "SPIRE", M + "red_terracotta", 12, 30, 2, 4,
                                                   strata=["red_terracotta", "red_nether_bricks", "brown_terracotta"]),
                                         formation("blood-hoodoo", 75002, 0.15, "HOODOO", M + "red_terracotta", 8, 16, 2, 3,
                                                   cap=M + "nether_bricks", extra={"hoodooCapRadius": 3, "hoodooCapHeight": 2})]},
              terrain3d="snippet/terrain-3d/rugged/amp32-hexagon-crack392", spawners=sp),
        biome("ashfang/cinder-fields", "Cinder Fields", "#3A3A3A", M + "badlands",
              blight("sundered_cinder_fields", grass="#4A4A40", fog="#555050", sky="#5A4A48", particle=M + "white_ash", rarity=40),
              [("sundered/craters", 4, 26)],
              [layer(["basalt[axis=y]", "blackstone", "gray_concrete_powder", "tuff", "magma_block"], 1, 2, style="SIMPLEX", zoom=0.2),
               layer(["blackstone"], 3, 6), STONE],
              decorators=[deco(["fire"], 0.003), deco(["dead_bush"], 0.02),
                          "snippet/decorator/pebbles/blackstone-crimson-c0-009"],
              objects=[camp, structure("sundered/ashfang/bone-totem", 0.02),
                       "snippet/object-placer/clutter/magmaspire-carve-c0-21-d4"],
              effects=[smoke(1, 500)], spawners=sp),
        biome("ashfang/rotwood", "Rotwood Thicket", "#4A2A3A", M + "dark_forest",
              blight("sundered_rotwood", cat="forest", grass="#4F3A2A", foliage="#5A1A1A", fog="#4A2A2A",
                     particle=M + "crimson_spore", rarity=35),
              [("rare-hills", 10, 34)],
              [layer(["podzol", "coarse_dirt", "crimson_nylium", "rooted_dirt"], 1, 1, style="SIMPLEX", zoom=0.3),
               layer(["dirt"], 2, 4), STONE],
              decorators=[deco(["crimson_roots", "crimson_fungus", "dead_bush"], 0.12)],
              objects=[trees(["trees/crimson/blackgeneric1", "trees/crimson/blackgeneric2", "trees/crimson/blackgeneric3",
                              "trees/crimson/crimsonwood1", "trees/crimson/crimsonwood2", "trees/crimson/crimsonwood3",
                              "trees/crimson/bonehand1", "trees/crimson/bonehand2"], 0.55, 2, -1),
                       camp],
              procedural={"trees": [ptree("rot-oak", 76001, 0.4, M + "dark_oak_log", M + "nether_wart_block", "DARK_OAK", 8, 14, 2,
                                          extra={"plausible": False})]},
              spawners=sp),
    ]
    shore = biome("ashfang/ashen-strand", "Ashen Strand", "#555050", M + "stony_shore",
                  blight("sundered_ashen_strand", grass="#4A4A40"), [("flat", 0, 3)],
                  [layer(["gravel", "blackstone", "tuff"], 2, 3, style="SIMPLEX", zoom=0.3)],
                  decorators=[deco(["dead_bush"], 0.02)], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["ocean/dark-depth-ocean", "ocean/ocean"],
            "cave": ["carving/volcanic", "carving/ember-rifts", "carving/deepslate", "carving/sulfur"], "color": "#8A1E1E",
            "name": "Ashfang Reach"}


def dreadmire(S):
    sp = S["dreadmire"]
    loot = [("sundered/dreadmire-crypt", 3)]
    vanilla = [(M + "chests/simple_dungeon", 2), (M + "chests/ancient_city", 1)]
    mire = lambda cid, **kw: custom(cid, "swamp", kw.pop("grass", "#4C5A2E"), kw.pop("foliage", "#3F4F26"), water="#3A3F22",
                                    water_fog="#1E2012", fog=kw.pop("fog", "#6A7060"), sky=kw.pop("sky", "#7A8078"),
                                    temp=0.7, humidity=1.0, **kw)
    crypt = structure("sundered/dreadmire/sunken-crypt", 0.005, loot=loot, vanilla=vanilla, max_slope=4)
    hut = structure("sundered/dreadmire/stilt-witch-hut", 0.01, loot=loot)
    willow = trees(["trees/willow/w1", "trees/willow/w2", "trees/willow/w3", "trees/willow/w4", "trees/willow/w5",
                    "trees/willow/bt1", "trees/willow/bt2", "trees/willow/bt3"], 0.5, 2, -1)
    L = [
        biome("dreadmire/blackwater-bog", "Blackwater Bog", "#3A4A2A", M + "swamp",
              mire("sundered_blackwater_bog", particle=M + "spore_blossom_air", rarity=200),
              [("sundered/bog", -3, 4)],
              [layer(["mud", "moss_block", "muddy_mangrove_roots", "grass_block"], 1, 2, style="SIMPLEX", zoom=0.2),
               layer(["mud", "clay"], 2, 4), STONE],
              decorators=[deco(["lily_pad"], 0.2, part="SEA_SURFACE"), deco(["seagrass", "tall_seagrass"], 0.25, part="SEA_FLOOR"),
                          deco(["brown_mushroom", "red_mushroom"], 0.02), deco(["moss_carpet"], 0.1), "snippet/decorator/shrubs/firefly-bush"],
              objects=[hut, crypt, structure("sundered/dreadmire/hanging-gibbet", 0.01), willow],
              effects=[ambient("SPORE_BLOSSOM_AIR", 4, 10, 300)], spawners=sp),
        biome("dreadmire/murkwood", "Murkwood Swamp", "#2E3F24", M + "swamp",
              mire("sundered_murkwood", grass="#3E4A25", foliage="#34401F", fog="#5A6052"),
              [("plain", 0, 8)],
              [layer(["grass_block", "podzol", "mud"], 1, 1, style="SIMPLEX", zoom=0.3), layer(["dirt", "mud"], 2, 4), STONE],
              decorators=[deco(["fern", "large_fern", "short_grass"], 0.3), deco(["lily_pad"], 0.12, part="SEA_SURFACE"),
                          "snippet/decorator/shrubs/firefly-bush"],
              objects=[willow, trees(["trees/darkoak/smdeadwillow1", "trees/darkoak/generic1", "trees/darkoak/generic2",
                                      "trees/darkoak/generic3"], 0.4, 1, -1),
                       hut, structure("sundered/dreadmire/drowned-shrine", 0.012, loot=loot)],
              procedural={"trees": [ptree("murk-willow", 77001, 0.4, M + "mangrove_log", M + "mangrove_leaves", "WILLOW", 9, 15)]},
              spawners=sp),
        biome("dreadmire/drowned-fen", "Drowned Fen", "#56604E", M + "mangrove_swamp",
              mire("sundered_drowned_fen", grass="#6E7A66", foliage="#6A7564", fog="#8A9088", sky="#8D938C",
                   particle=M + "white_ash", rarity=160),
              [("sundered/bog", -5, 2)],
              [layer(["pale_moss_block", "mud", "moss_block"], 1, 1, style="SIMPLEX", zoom=0.25), layer(["mud"], 2, 4), STONE],
              decorators=[deco(["pale_moss_carpet"], 0.12), deco(["seagrass"], 0.2, part="SEA_FLOOR"),
                          deco(["lily_pad"], 0.08, part="SEA_SURFACE")],
              objects=["snippet/object-placer/trees/pale-oak-creaking-c0-1-d1",
                       crypt, structure("sundered/dreadmire/drowned-shrine", 0.015, loot=loot),
                       structure("sundered/dreadmire/hanging-gibbet", 0.015)],
              procedural={"trees": [ptree("fen-deadwood", 77002, 0.3, M + "pale_oak_log", M + "pale_oak_leaves", "DARK_OAK", 6, 10, 2)]},
              spawners=sp),
    ]
    shore = biome("dreadmire/mudflats", "Mudflats", "#5A4A3A", M + "swamp", mire("sundered_mudflats"), [("flat", -1, 2)],
                  [layer(["mud", "clay", "gravel"], 2, 3, style="SIMPLEX", zoom=0.3)],
                  decorators=[deco(["seagrass"], 0.2, part="SEA_FLOOR")], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["swamp/sea/lake", "swamp/sea/ocean"],
            "cave": ["carving/swamp", "carving/moss-pillars", "carving/spider-infestation", "carving/lush"], "color": "#3A5A2A",
            "name": "The Dreadmire"}


def frontier(S):
    sp = S["frontier"]
    loot = [("sundered/frontier-strongbox", 3)]
    vanilla = [(M + "chests/desert_pyramid", 1), (M + "chests/abandoned_mineshaft", 2)]
    dry = lambda cid, **kw: custom(cid, kw.pop("cat", "mesa"), kw.pop("grass", "#BFB755"), kw.pop("foliage", "#AEA42A"),
                                   fog=kw.pop("fog", "#E8C8A0"), sky=kw.pop("sky", "#8FC0E8"), downfall="none", temp=2.0,
                                   humidity=0.0, **kw)
    town = structure("sundered/frontier/frontier-town", 0.004, loot=loot, max_slope=2)
    mine = structure("sundered/frontier/abandoned-mine", 0.006, loot=loot, vanilla=vanilla, max_slope=6)
    L = [
        biome("frontier/cracked-flats", "Sunscorch Cracked Flats", "#C8A06A", M + "desert",
              dry("sundered_cracked_flats", cat="desert", particle=M + "white_ash", rarity=400),
              [("flat", 4, 10)],
              [layer(["packed_mud", "coarse_dirt", "smooth_sandstone", "terracotta", "mud_bricks", "packed_mud"], 1, 1,
                     style="CELLULAR", zoom=0.05),
               layer(["coarse_dirt", "packed_mud"], 1, 2), layer(["sandstone", "terracotta"], 2, 5), STONE],
              decorators=["snippet/decorator/mushrooms/dead-bush-mix-c0-03", deco(["short_dry_grass", "tall_dry_grass"], 0.04),
                          "snippet/decorator/plants/cactus-flowering-max2-c0-0005"],
              objects=[town, structure("sundered/frontier/longhorn-marker", 0.01), structure("sundered/frontier/sun-oracle", 0.003,
                                                                                            loot=loot, vanilla=vanilla, max_slope=3)],
              terrain3d=t3d(81001, 3, 120, 10, "CELLULAR", 6, 1, 90, "CELLULAR", 0.0, 0.1),
              spawners=sp),
        biome("frontier/red-mesa", "Red Mesa", "#B5522A", M + "badlands",
              dry("sundered_red_mesa", grass="#90814D", foliage="#9E814D"),
              [("sundered/mesa-terrace", 10, 60)],
              [layer(["red_sand"], 1, 2), layer(["orange_terracotta", "terracotta", "red_terracotta", "white_terracotta",
                                                 "yellow_terracotta", "brown_terracotta"], 8, 24, style="STRATA", zoom=0.35),
               "snippet/biome-palette/stone/stone3-andesite3-2-2"],
              decorators=["snippet/decorator/mushrooms/dead-bush-mix-c0-01", "snippet/decorator/plants/cactus-flowering-max5-c0-0005"],
              objects=[mine, structure("sundered/frontier/bandit-fort", 0.006, loot=loot, max_slope=3)],
              procedural={"formations": [
                  formation("mesa-hoodoo", 82001, 0.2, "HOODOO", M + "orange_terracotta", 8, 20, 2, 3, cap=M + "red_sandstone",
                            strata=["orange_terracotta", "red_terracotta", "white_terracotta", "terracotta"],
                            extra={"hoodooCapRadius": 3, "hoodooCapHeight": 2}),
                  formation("mesa-arch", 82002, 0.03, "ARCH", M + "red_terracotta", 14, 24, 3, 4,
                            strata=["orange_terracotta", "red_terracotta", "brown_terracotta"],
                            extra={"archSpan": 18, "archThickness": 4})]},
              spawners=sp),
        biome("frontier/sagebrush-prairie", "Sagebrush Prairie", "#A6A060", M + "savanna",
              dry("sundered_sagebrush", cat="savanna", grass="#B4AA5A", foliage="#A09A46"),
              [("rare-hills", 6, 20)],
              [layer(["grass_block", "coarse_dirt", "grass_block"], 1, 1, style="SIMPLEX", zoom=0.4), layer(["dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/grass/arid-mix-c0-018", "snippet/decorator/grass/dry-grass", "snippet/decorator/shrubs/bush",
                          deco(["short_dry_grass"], 0.1)],
              objects=["snippet/object-placer/trees/acacia-savannad-c0-07", town, structure("sundered/frontier/bandit-fort", 0.005, loot=loot),
                       structure("sundered/frontier/longhorn-marker", 0.015), "snippet/object-placer/clutter/savrock-c0-1"],
              spawners=sp),
        biome("frontier/deadwood-canyon", "Deadwood Canyon", "#9A5A3A", M + "wooded_badlands",
              dry("sundered_deadwood_canyon", grass="#9A8A50"),
              [("canyon-steep", 10, 70)],
              [layer(["coarse_dirt", "red_sand", "gravel"], 1, 1, style="SIMPLEX"),
               layer(["red_terracotta", "terracotta", "orange_terracotta", "light_gray_terracotta"], 10, 30, style="STRATA", zoom=0.4),
               STONE],
              decorators=["snippet/decorator/mushrooms/dead-bush-mix-c0-03"],
              objects=[mine, trees(["trees/oak/dead1", "trees/oak/dead2", "trees/oak/dead3", "trees/spruce/aridpine1",
                                    "trees/spruce/aridpine2"], 0.12)],
              terrain3d="snippet/terrain-3d/rugged/amp30-perlin-crack448", spawners=sp),
    ]
    shore = biome("frontier/dry-coast", "Dry Coast", "#D9B77A", M + "beach", dry("sundered_dry_coast", cat="beach"), [("flat", 0, 3)],
                  [layer(["sand", "red_sand"], 2, 3, style="SIMPLEX", zoom=0.3), layer(["sandstone"], 2, 3)],
                  decorators=[deco(["dead_bush"], 0.02)], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["ocean/warm", "ocean/ocean"],
            "cave": ["carving/sandstone", "carving/red-sandstone", "carving/mixed-sandstone", "carving/sand-hollows"],
            "color": "#D98A3A", "name": "The Sunscorch Frontier"}


def everbloom(S):
    sp = S["everbloom"]
    loot = [("sundered/everbloom-arcane", 3)]
    vanilla = [(M + "chests/stronghold_library", 2)]
    fae = lambda cid, **kw: custom(cid, "forest", kw.pop("grass", "#5CE07A"), kw.pop("foliage", "#4FD4A0"), water="#5AC8FA",
                                   water_fog="#1B4F8A", fog=kw.pop("fog", "#CDB6F2"), sky=kw.pop("sky", "#9FB8FF"),
                                   temp=0.7, humidity=0.8, **kw)
    tower = structure("sundered/everbloom/mage-tower", 0.004, loot=loot, vanilla=vanilla, max_slope=3)
    glowcap = {"name": "glowcap", "chance": 0.25, "density": 2, "variants": 8, "seed": 91001, "mode": "CENTER_HEIGHT",
               "rotation": {"enabled": True, "yAxis": {"enabled": True, "min": 0, "max": 360, "interval": 90}},
               "stem": M + "mushroom_stem", "cap": M + "red_mushroom_block",
               "capPalette": {"palette": [W("red_mushroom_block", 3), W("pink_wool", 1)]},
               "stemHeightMin": 4, "stemHeightMax": 8, "capShape": "DOME", "capRadiusMin": 2, "capRadiusMax": 4,
               "spotBlock": M + "shroomlight", "spotChance": 0.15}
    L = [
        biome("everbloom/glimmerwood", "Glimmerwood", "#4FD4A0", M + "flower_forest",
              fae("sundered_glimmerwood", particle=M + "firefly", rarity=90),
              [("rare-hills", 10, 30)],
              [layer(["grass_block", "moss_block", "grass_block"], 1, 1, style="SIMPLEX", zoom=0.3), layer(["dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/flowers/meadow-mix-c0-06", deco(["pink_petals[facing=north,flower_amount=4]"], 0.08),
                          "snippet/decorator/shrubs/firefly-bush",
                          deco(["azalea", "flowering_azalea"], 0.03)],
              objects=[trees(["trees/sakura/genericsak1", "trees/sakura/genericsak2", "trees/sakura/genericsak3",
                              "trees/sakura/mlarge1", "trees/sakura/mlarge2"], 0.3, 1, -1),
                       tower, structure("sundered/everbloom/fairy-ring", 0.02), structure("sundered/everbloom/moonwell", 0.008)],
              procedural={"trees": [ptree("glimmer-birch", 92001, 0.5, M + "birch_log", M + "azalea_leaves", "POPLAR", 12, 20),
                                    ptree("glimmer-cherry", 92002, 0.35, M + "cherry_log", M + "cherry_leaves", "CHERRY", 7, 11)],
                          "fungi": [glowcap]},
              effects=[ambient("END_ROD", 2, 10, 500)], spawners=sp),
        biome("everbloom/crystal-meadow", "Crystal Meadow", "#B38CFF", M + "meadow",
              fae("sundered_crystal_meadow", grass="#7DE88A", foliage="#6FD68A", particle=M + "end_rod", rarity=300),
              [("plain", 8, 20)],
              [layer(["grass_block"]), layer(["dirt", "calcite"], 2, 4), layer(["calcite", "amethyst_block"], 1, 2, style="SIMPLEX"), STONE],
              decorators=["snippet/decorator/flowers/wildflowers", "snippet/decorator/flowers/allium-mix-c0-03",
                          deco(["amethyst_cluster[facing=up,waterlogged=false]", "large_amethyst_bud[facing=up,waterlogged=false]"], 0.006)],
              objects=[structure("sundered/everbloom/arcane-henge", 0.01), tower, structure("sundered/everbloom/moonwell", 0.01)],
              procedural={"crystals": [{"name": "meadow-geode", "chance": 0.12, "density": 1, "variants": 8, "seed": 93001,
                                        "mode": "CENTER_HEIGHT", "growthSurface": "FLOOR", "block": M + "amethyst_block",
                                        "tipBlock": M + "amethyst_cluster", "glow": True, "glowBlock": M + "pearlescent_froglight",
                                        "baseBlock": M + "calcite", "shardCountMin": 3, "shardCountMax": 6, "shardLengthMin": 4,
                                        "shardLengthMax": 9, "translate": {"y": -1}}]},
              spawners=sp),
        biome("everbloom/elder-grove", "Elder Grove", "#2F7A3A", M + "old_growth_birch_forest",
              fae("sundered_elder_grove", grass="#3FBF5A", foliage="#2FA84A", fog="#B6D8C0"),
              [("rare-hills", 14, 40)],
              [grass_top(), layer(["dirt", "rooted_dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/grass/moss-fern-c0-1", "snippet/decorator/plants/leaf-litter", deco(["fern", "large_fern"], 0.2)],
              objects=[structure("sundered/everbloom/fairy-ring", 0.01), tower],
              procedural={"trees": [ptree("elder-oak", 94001, 0.6, M + "oak_log", M + "oak_leaves", "OAK", 22, 34, 3,
                                          extra={"rootStyle": "BUTTRESS", "rootFlare": 1.5}),
                                    ptree("elder-dark", 94002, 0.3, M + "dark_oak_log", M + "flowering_azalea_leaves", "DARK_OAK_FLAT_WIDE",
                                          16, 24, 2)],
                          "fungi": [glowcap]},
              spawners=sp),
    ]
    shore = biome("everbloom/fae-shore", "Fae Shore", "#E8F5FF", M + "beach", fae("sundered_fae_shore"), [("flat", 0, 3)],
                  [layer(["sand", "calcite"], 2, 3, style="SIMPLEX", zoom=0.3), layer(["sandstone"], 2, 3)],
                  decorators=["snippet/decorator/plants/sugar-cane-shore-c0-18"], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["temperate/sea/ocean", "ocean/rich-oceans"],
            "cave": ["carving/amethyst", "carving/lush", "carving/calcite", "carving/mushroom"], "color": "#B38CFF",
            "name": "The Everbloom"}


def crownlands(S):
    sp = S["crownlands"]
    loot = [("sundered/crownlands-market", 3)]
    fair = lambda cid, **kw: custom(cid, kw.pop("cat", "plains"), kw.pop("grass", "#8DD65A"), kw.pop("foliage", "#6CC24A"),
                                    temp=0.8, humidity=0.5, **kw)
    castle = structure("sundered/crownlands/castle-keep", 0.003, loot=[("sundered/warscar-spoils", 1), ("sundered/crownlands-market", 2)],
                       vanilla=[(M + "chests/village/village_weaponsmith", 2)], max_slope=2)
    L = [
        biome("crownlands/golden-fields", "Golden Fields", "#E0C85A", M + "plains", fair("sundered_golden_fields", grass="#B5D65A"),
              [("plain", 6, 16)],
              [grass_top(), layer(["dirt"], 2, 4), STONE],
              decorators=[deco(["wheat[age=7]"], 0.25, style="SIMPLEX", zoom=0.08), "snippet/decorator/flowers/meadow-mix-grass-c0-3",
                          "snippet/decorator/crops/carrots-c0-01", "snippet/decorator/crops/potatoes-c0-01", deco(["hay_block[axis=y]"], 0.001)],
              objects=[structure("sundered/crownlands/windmill", 0.012), structure("sundered/crownlands/market-crossroads", 0.006, loot=loot,
                                                                                     max_slope=2),
                       "snippet/object-placer/trees/oak-generic-c0-07"],
              spawners=sp),
        biome("crownlands/rolling-downs", "Rolling Downs", "#7CC24A", M + "meadow", fair("sundered_rolling_downs"),
              [("rare-hills", 10, 34)],
              [grass_top(), layer(["dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/flowers/meadow-mix-c0-2-simplex-z0-2", "snippet/decorator/grass/short-c0-6"],
              objects=[castle, structure("sundered/crownlands/crown-watchtower", 0.01, loot=loot),
                       "snippet/object-placer/trees/birch-antioch-c0-07-d4", "snippet/object-placer/trees/oak-toak-c0-18"],
              spawners=sp),
        biome("crownlands/kingswood", "Kingswood", "#3F8F3A", M + "forest", fair("sundered_kingswood", cat="forest", grass="#6CBF4A"),
              [("rare-hills", 10, 28)],
              [grass_top(), layer(["dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/grass/moss-fern-c0-1", "snippet/decorator/plants/leaf-litter",
                          "snippet/decorator/flowers/tulip-mix-c0-189"],
              objects=["snippet/object-placer/trees/oak-thoakgeneric-c0-18", "snippet/object-placer/trees/mixed-tredwood-c0-35",
                       structure("sundered/crownlands/crown-watchtower", 0.008, loot=loot)],
              spawners=sp),
    ]
    shore = biome("crownlands/harbor-coast", "Harbor Coast", "#E8DDB0", M + "beach", fair("sundered_harbor_coast", cat="beach"),
                  [("flat", 0, 3)], [layer(["sand", "gravel"], 2, 3, style="SIMPLEX", zoom=0.3), layer(["sandstone"], 2, 3)],
                  objects=[structure("sundered/crownlands/lighthouse", 0.01, max_slope=3)], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["temperate/sea/ocean", "temperate/sea/ocean-deep"],
            "cave": ["carving/rocky-cavebiome", "carving/drip-lite", "carving/deep", "carving/chalk-gardens"], "color": "#E0C85A",
            "name": "The Crownlands"}


def warscar(S):
    sp = S["warscar"]
    loot = [("sundered/warscar-spoils", 3)]
    grim = lambda cid, **kw: custom(cid, kw.pop("cat", "plains"), kw.pop("grass", "#7A7A52"), kw.pop("foliage", "#6A6A45"),
                                    fog=kw.pop("fog", "#9A948A"), sky=kw.pop("sky", "#8A8A90"), temp=0.6, humidity=0.3, **kw)
    keep = structure("sundered/warscar/ruined-keep", 0.005, loot=loot, vanilla=[(M + "chests/simple_dungeon", 1)], max_slope=3)
    L = [
        biome("warscar/scorched-battlefield", "Scorched Battlefield", "#6A5A4A", M + "plains",
              grim("sundered_scorched_battlefield", particle=M + "ash", rarity=150),
              [("sundered/craters", 4, 16)],
              [layer(["coarse_dirt", "gravel", "grass_block", "soul_soil", "rooted_dirt"], 1, 1, style="SIMPLEX", zoom=0.15),
               layer(["dirt", "coarse_dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/grass/dry-grass", deco(["dead_bush"], 0.03), deco(["short_grass"], 0.1),
                          deco(["poppy"], 0.01)],
              objects=[structure("sundered/warscar/broken-trebuchet", 0.012), structure("sundered/warscar/war-graves", 0.015),
                       keep, trees(["trees/oak/dead1", "trees/oak/dead2", "trees/oak/dead3"], 0.1)],
              procedural={"ruins": [ruin("siege-rubble", 95001, 0.15, "RUBBLE", M + "cobblestone", M + "mossy_cobblestone", 1, 3, 3, 6, 3, 6),
                                    ruin("battle-wall", 95002, 0.05, "WALL", M + "stone_bricks", M + "cracked_stone_bricks", 3, 7, 1, 2, 5, 11,
                                         erosion=0.45)]},
              effects=[smoke(1, 700)], spawners=sp),
        biome("warscar/ruined-marches", "Ruined Marches", "#7A7A62", M + "plains", grim("sundered_ruined_marches"),
              [("rare-hills", 8, 26)],
              [layer(["grass_block", "coarse_dirt"], 1, 1, style="SIMPLEX", zoom=0.3), layer(["dirt"], 2, 4), STONE],
              decorators=["snippet/decorator/grass/short-c0-6", "snippet/decorator/flowers/meadow-rubble-mix-c0-025"],
              objects=[keep, structure("sundered/warscar/burned-house", 0.02, loot=loot), structure("sundered/warscar/war-graves", 0.01),
                       "snippet/object-placer/trees/oak-dead-c0-4-d2"],
              procedural={"ruins": [ruin("march-arch", 95003, 0.03, "ARCH", M + "stone_bricks", M + "cracked_stone_bricks", 7, 11, 1, 2, 5, 9),
                                    ruin("march-pillar", 95004, 0.06, "PILLAR", M + "stone_bricks", M + "mossy_stone_bricks", 4, 9),
                                    ruin("march-foundation", 95005, 0.04, "FLOOR_SLAB", M + "cobblestone", M + "mossy_cobblestone",
                                         1, 1, 5, 9, 6, 10)]},
              spawners=sp),
        biome("warscar/ashen-woods", "Ashen Woods", "#4A4A44", M + "dark_forest",
              grim("sundered_ashen_woods", cat="forest", grass="#5A5A48", foliage="#4A4A3E", particle=M + "white_ash", rarity=80),
              [("rare-hills", 8, 24)],
              [layer(["podzol", "coarse_dirt", "gravel"], 1, 1, style="SIMPLEX", zoom=0.3), layer(["dirt"], 2, 4), STONE],
              decorators=[deco(["dead_bush"], 0.05), "snippet/decorator/plants/leaf-litter"],
              objects=[trees(["trees/darkoak/smdeadwillow1", "trees/oak/dead1", "trees/oak/dead2", "trees/oak/dead3",
                              "trees/spruce/genericdead1", "trees/spruce/genericdead2", "trees/spruce/genericdead3"], 0.5, 2),
                       structure("sundered/warscar/burned-house", 0.015, loot=loot)],
              procedural={"trees": [ptree("charred-oak", 96001, 0.3, M + "stripped_dark_oak_log", M + "dark_oak_leaves", "OAK", 7, 12,
                                          extra={"plausible": False})]},
              spawners=sp),
    ]
    shore = biome("warscar/grey-strand", "Grey Strand", "#8A8A80", M + "stony_shore", grim("sundered_grey_strand", cat="beach"),
                  [("flat", 0, 3)], [layer(["gravel", "stone", "cobblestone"], 2, 3, style="SIMPLEX", zoom=0.3)], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["ocean/ocean", "temperate/sea/ocean"],
            "cave": ["carving/deepslate", "carving/rocky-cavebiome", "carving/deep"], "color": "#7A6A5A", "name": "The Warscar Marches"}


def umbral(S):
    sp = S["umbral"]
    loot = [("sundered/umbral-reliquary", 3)]
    vanilla = [(M + "chests/ancient_city", 1), (M + "chests/stronghold_corridor", 2)]
    dark = lambda cid, **kw: custom(cid, kw.pop("cat", "taiga"), kw.pop("grass", "#4A5A52"), kw.pop("foliage", "#3A4A42"),
                                    water="#2A3A5A", water_fog="#0A1020", fog=kw.pop("fog", "#3A3A4A"), sky=kw.pop("sky", "#2A2A3A"),
                                    downfall=kw.pop("downfall", "snow"), temp=-0.3, humidity=0.4, **kw)
    cathedral = structure("sundered/umbral/hollow-cathedral", 0.0035, loot=loot, vanilla=vanilla, max_slope=3)
    gate = structure("sundered/umbral/necropolis-gate", 0.005, loot=loot, vanilla=vanilla, max_slope=4)
    L = [
        biome("umbral/gravespire-peaks", "Gravespire Peaks", "#2A2A3A", M + "jagged_peaks",
              dark("sundered_gravespire", cat="extreme_hills", particle=M + "white_ash", rarity=60),
              [("sundered/gravespires", 40, 190)],
              [layer(["snow_block", "powder_snow"], 1, 2, slope={"minimumSlope": 0, "maximumSlope": 1.2}),
               layer(["deepslate", "tuff", "blackstone", "cobbled_deepslate"], 2, 6, style="SIMPLEX", zoom=0.3),
               layer(["deepslate"], 6, 20)],
              wall="snippet/biome-palette/wall/stone-andesite-cobble",
              decorators=[deco(["snow[layers=2]"], 0.2)],
              objects=[structure("sundered/umbral/soulfire-obelisk", 0.01), structure("sundered/umbral/gibbet-cage", 0.01)],
              procedural={"formations": [formation("grave-spire", 97001, 0.2, "SPIRE", M + "deepslate", 16, 38, 2, 4,
                                                   strata=["deepslate", "tuff", "blackstone"], cap=M + "snow_block")]},
              terrain3d="snippet/terrain-3d/rugged/amp40-nowhere-crack416", spawners=sp),
        biome("umbral/deadpine-vale", "Deadpine Vale", "#2F3A34", M + "old_growth_spruce_taiga",
              dark("sundered_deadpine", fog="#4A4A55"),
              [("rare-hills", 14, 40)],
              [layer(["podzol", "coarse_dirt", "snow_block", "pale_moss_block"], 1, 1, style="SIMPLEX", zoom=0.3),
               layer(["dirt"], 2, 4), STONE],
              decorators=[deco(["fern", "dead_bush"], 0.08), deco(["snow[layers=1]"], 0.3), deco(["pale_moss_carpet"], 0.03)],
              objects=[trees(["trees/spruce/genericdead1", "trees/spruce/genericdead2", "trees/spruce/genericdead3",
                              "trees/spruce/levergreen1", "trees/spruce/levergreen2", "trees/spruce/levergreen3"], 0.7, 2, -1),
                       gate, structure("sundered/umbral/gibbet-cage", 0.015), structure("sundered/umbral/soulfire-obelisk", 0.008)],
              procedural={"trees": [ptree("dread-pine", 98001, 0.4, M + "spruce_log", M + "spruce_leaves", "SPRUCE", 18, 30, 1,
                                          extra={"plausible": False})]},
              spawners=sp),
        biome("umbral/cathedral-heights", "Cathedral Heights", "#3A3548", M + "snowy_slopes",
              dark("sundered_cathedral_heights", cat="icy", particle=M + "ash", rarity=180),
              [("mountain", 30, 70)],
              [layer(["snow_block", "coarse_dirt", "deepslate_tiles", "cobbled_deepslate"], 1, 1, style="SIMPLEX", zoom=0.25),
               layer(["deepslate"], 3, 9), STONE],
              decorators=[deco(["snow[layers=3]"], 0.25), deco(["wither_rose"], 0.004)],
              objects=[cathedral, gate, structure("sundered/umbral/soulfire-obelisk", 0.012)],
              procedural={"ruins": [ruin("gothic-arch", 99001, 0.04, "ARCH", M + "deepslate_bricks", M + "cracked_deepslate_bricks", 9, 14,
                                         1, 2, 5, 9),
                                    ruin("gothic-pillar", 99002, 0.07, "PILLAR", M + "polished_deepslate", M + "cracked_deepslate_tiles", 6, 14)]},
              terrain3d="snippet/terrain-3d/hilly/amp22-nowhere-crack448",
              effects=[ambient("SOUL", 2, 12, 700)], spawners=sp),
    ]
    shore = biome("umbral/black-shingle", "Black Shingle", "#2A2A2A", M + "stony_shore", dark("sundered_black_shingle"),
                  [("flat", 0, 3)], [layer(["gravel", "blackstone", "cobbled_deepslate"], 2, 3, style="SIMPLEX", zoom=0.3)], spawners=sp)
    return {"land": L, "shore": [shore], "sea": ["ocean/dark-depth-ocean", "ocean/deep"],
            "cave": ["carving/standard-deepdark", "carving/dark-depths", "carving/deepslate", "carving/deepravine"], "color": "#3A2A5A",
            "name": "The Umbral Peaks"}


def region(key, z, rarity, loot_tables, zoom=4.5, cave_zoom=3.2):
    r = {"name": z["name"], "color": z["color"], "rarity": rarity, "landBiomes": z["land"], "shoreBiomes": z["shore"],
         "seaBiomes": z["sea"], "caveBiomes": z["cave"], "landBiomeZoom": zoom, "seaBiomeZoom": 4, "caveBiomeZoom": cave_zoom,
         "shoreHeightMin": 2.8, "shoreHeightMax": 8.5, "shoreHeightZoom": 2.14,
         "loot": {"mode": "FALLBACK", "multiplier": 0.6, "tables": loot_tables}}
    out(f"regions/sundered/{key}.json", r)
    return f"sundered/{key}"


def main():
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
    if not base or not os.path.isfile(os.path.join(base, "dimensions", "overworld.json")):
        sys.exit("pass --base <overworld pack folder> (the folder that contains dimensions/overworld.json)")
    write_generators()
    write_loot()
    S = write_monsters()
    sea_spawn = {"azure": spawner("azure-reef", [("standard/passive/tropicalfish", 1, 3, 6), ("standard/neutral/dolphin", 4, 1, 3),
                                                 ("standard/passive/turtle", 5, 1, 2), ("standard/passive/pufferfish", 5, 1, 1)],
                                  group="UNDERWATER", per_chunk=4)}
    zones = [
        ("azure-isles", azure(S, sea_spawn), 1, ["tropical/food", "sundered/azure-pirate"], 5.0),
        ("ashfang-reach", ashfang(S), 2, ["sundered/ashfang-warchest"], 4.5),
        ("dreadmire", dreadmire(S), 2, ["swamp/food"], 4.0),
        ("sunscorch-frontier", frontier(S), 2, ["hot/food", "sundered/frontier-strongbox"], 4.5),
        ("everbloom", everbloom(S), 2, ["forest/food"], 4.0),
        ("crownlands", crownlands(S), 2, ["temperate/food", "sundered/crownlands-market"], 4.5),
        ("warscar-marches", warscar(S), 2, ["temperate/clutter"], 4.0),
        ("umbral-peaks", umbral(S), 2, ["cold/food"], 4.5),
    ]
    regions = [region(key, z, rarity, loot, zoom) for key, z, rarity, loot, zoom in zones]

    dim = json.load(open(os.path.join(base, "dimensions", "overworld.json")))
    d = copy.deepcopy(dim)

    def scrub(node):  # keys the current engine no longer reads (Gson ignores them; keep our copy tidy)
        if isinstance(node, dict):
            for k in ("axialFracturing", "minCarveCells", "recoveryThresholdBoost"):
                node.pop(k, None)
            for v in node.values():
                scrub(v)
        elif isinstance(node, list):
            for v in node:
                scrub(v)
    scrub(d)
    d["name"] = "Sundered Realms"
    d["regions"] = regions
    # Continents: fewer, larger landmasses separated by open (but crossable) seas.
    d["landChance"] = 0.52
    d["continentZoom"] = 1.9
    d["regionZoom"] = 24.0
    d["regionStyle"] = {"style": "CELLULAR_IRIS_DOUBLE",
                        "fracture": {"style": "FRACTAL_WATER", "zoom": 0.15, "multiplier": 9,
                                     "fracture": {"style": "STATIC", "multiplier": 1}}}
    d["loot"] = {"mode": "FALLBACK", "tables": ["global-clutter"]}
    out(f"dimensions/{PACK_NAME}.json", d)
    print(f"wrote {len(written)} json files")


if __name__ == "__main__":
    main()
