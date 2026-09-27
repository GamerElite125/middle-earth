Middle-earth Overworld - datapack for Minecraft {VERSION} (Fabric)
================================================================

REQUIRES the Middle-earth mod for Fabric {VERSION} (block namespace "{ME}")
plus Fabric API (and, on 1.21.8, the mod's required wild-things and
sevenstars-api mods). A datapack cannot add new blocks by itself; it only tells the
Overworld generator to use the mod's blocks.

Install
-------
New world: Create New World -> More -> Data Packs -> drag in
           middle-earth-overworld-{VERSION}.zip and move it to the "Selected" side.
Existing world: put the zip in  saves/<world>/datapacks/  and restart
           (or run /reload). Old chunks are converted automatically too,
           see "Existing chunks" below.
Server:    put the zip in  world/datapacks/  before the world is created.

What is added
-------------
Underground only (all capped at Y=16, only replaces stone/deepslate, so
nothing shows on the surface, mountain tops, grass or dirt):
  * Every natural Middle-earth rock of this mod version (limestone,
    dolomite, galonn, izheraban, zigilaban, schist, gneiss, gabbro, slate,
    ironstone, hematite, ashen stone, pumice, blue/green/gilded green tuff,
    gonluin on 1.21.1; chalk, travertine, khagalaban on 1.21.8) and the
    "old" variants                                       (Y -24 .. 16)
  * Nurgon layer blobs (with tuff & smooth basalt)       (Y -52 .. 0)
  * Medgon layer blobs (with blackstone)                 (Y -64 .. -28)
  * Ores, placed in the matching rock like the mod does:
      coal & copper   in ME rocks (gonluin_/limestone_/ashen_/ironstone_/
                      slate_/calcite_ variants)
      tin             stone, deepslate, ME rocks, nurgon
      quartzite       Y -32 .. 16
      lead            deepslate, nurgon, medgon
      iron, silver,
      gold, jadeite   nurgon, medgon
      mithril         medgon only, Y -64 .. -32 (rare)
      emerald, ruby,
      sapphire        nurgon, medgon (1.21.8 only)
      adamant         medgon only (1.21.8 only)
  * Pockets of ash, ashen dirt/gravel/sand, black/white/river sand, dry dirt,
    mire, turf, dirty roots, grassy/snowy dirt, old & lorien podzol,
    forest/corrupted moss blocks.

Surface:
  * All 14 wild crops (wheat, flax, pipeweed, tomato, bell pepper, cucumber,
    garlic, onion, lettuce, leek, potato, carrot, beetroot, tall wild wheat),
    berry bushes, Middle-earth flowers (elanor, mallos, ...), grasses,
    shrubs, heather, reeds, cattails and mushrooms, per biome.
  * Animals: deer, pheasant, swan, snail, broadhoof goat.
  * NO faction NPCs or monsters (no orcs, goblins, trolls, men, elves,
    dwarves, hobbits, wargs, spiders, barrow wights).

Mining the ores gives the mod's raw materials (raw tin, raw lead, raw
silver, raw mithril, ...) that you process with the mod's own smelting,
alloying and forging recipes.

Existing chunks
---------------
New chunks get everything while they generate. Chunks that existed before
the pack was added are converted automatically as players get near them
(within 4 chunks, about 4 chunks per second per player, Overworld only).
The same rocks, ores, pockets and plants are added to each old chunk once.

How it tracks this: the bottom bedrock block at each chunk's corner
(x0, Y=-64, z0) is replaced with reinforced deepslate as a "done" flag.
You will never see it unless you dig to the very bottom of the world.

Notes for old chunks:
  * Underground blobs replace natural stone/deepslate/granite/diorite/
    andesite below Y=16, so a build made of those blocks down there could
    get some patches. Cobblestone, bricks, planks etc. are never touched.
  * Plants only go on grass/dirt with air above, so they can show up on
    lawns near your base.
  * Animals already use the new spawn lists in old chunks.

Turn conversion off/on (op only):
  /function me_overworld:retrofit/stop
  /function me_overworld:retrofit/start

Compatibility
-------------
Do not use together with middle-earth-map-overworld (that pack replaces the
whole Overworld with the Middle-earth map, which already has all of this).

This pack overrides the vanilla Overworld biome files. Other datapacks/mods
that also replace vanilla biome files (e.g. Terralith) will conflict; the
one loaded last wins.
