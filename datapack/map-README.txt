Middle-earth Map Overworld - datapack for Minecraft {VERSION} (Fabric)
=====================================================================

The Overworld generates as the real Middle-earth map, using the Middle-earth
mod's own world generator: the Shire, Bree, Rivendell, the Misty Mountains,
Mirkwood, Rohan, Gondor, Mordor and everything else, with the mod's terrain,
biomes, rocks, ores, trees, plants and structures.

Everything that spawns in the mod's Middle-earth dimension spawns here too:
animals, monsters and faction NPCs (men, elves, dwarves, hobbits, orcs...).

REQUIRES the Middle-earth mod for Fabric {VERSION} (namespace "{ME}") plus
its dependencies. Without the mod the world cannot load.

NEW WORLDS ONLY
---------------
Minecraft saves the Overworld's generator in the world when the world is
created, so this pack only works on a brand-new world:
  Create New World -> More -> Data Packs -> add
  middle-earth-map-overworld-{VERSION}.zip -> Create.
Minecraft may warn that the world uses custom/experimental settings; that
is expected, click Proceed.
Server: put the zip in world/datapacks/ BEFORE the world is first created.

Spawn
-----
The map's corner (0, 0) is open ocean, so the pack moves the world spawn to
Hobbiton (about X 29856, Z 28800) the first time the world loads.
Change it any time with /setworldspawn.

Notes
-----
* The map has a fixed size (about 96,000 x 96,000 blocks); past its edges
  is ocean.
* The Nether and the End are unchanged.
* The mod's separate Middle-earth dimension still exists; this pack just
  makes the Overworld look like it.
* Do not use together with middle-earth-overworld (the ore/plant pack for
  the vanilla Overworld); it is not needed here.
