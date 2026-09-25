Middle-earth Overworld - datapack for Minecraft 1.21.1 (Fabric)
===============================================================

REQUIRES the Middle-earth mod for Fabric 1.21.1 (block/entity namespace "me")
plus Fabric API. A datapack cannot add new blocks by itself; it only tells the
Overworld generator to use the mod's blocks.

Install
-------
New world: Create New World -> More -> Data Packs -> drag in
           middle-earth-overworld.zip and move it to the "Selected" side.
Existing world: put the zip in  saves/<world>/datapacks/  and restart.
           Only NEW chunks get the new ores/plants (explore new areas).
Server:    put the zip in  world/datapacks/  before the world is created.

What is added
-------------
Underground only (all capped at Y=16, only replaces stone/deepslate, so
nothing shows on the surface, mountain tops, grass or dirt):
  * Every natural Middle-earth rock: limestone, dolomite, gonluin, blue tuff,
    green tuff, gilded green tuff, galonn, izheraban, zigilaban, schist,
    gneiss, gabbro, slate, ironstone, hematite, ashen stone, pumice, and the
    "old" limestone/dolomite/galonn/izheraban            (Y -24 .. 16)
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

Compatibility
-------------
This pack overrides the vanilla Overworld biome files. Other datapacks/mods
that also replace vanilla biome files (e.g. Terralith) will conflict; the
one loaded last wins.
