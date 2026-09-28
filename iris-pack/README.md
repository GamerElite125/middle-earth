# Middle-earth: an Iris world pack

A fantasy world generator pack **inspired by** Middle-earth, for the
[Iris](https://github.com/VolmitSoftware/Iris) world generator plugin on **Minecraft 26.2**. It works on
Spigot, Paper, Purpur and Folia, using Iris builds for 26.1.2 to 26.2.

It is not a copy of the real map. It generates an endless procedural world whose regions feel like
Tolkien's lands, and a road network connects all of them. It uses only vanilla blocks, so players do
not need to install any mods.

## What generates

| Region | Biomes |
|---|---|
| **Eriador** | The Shire, Bree-land, the Lone-lands (Arnor ruins), the Old Forest, the Trollshaws |
| **Angmar** | Wastes of Angmar (black ruined towers, dead trees, ash), Peaks of Carn Dûm, the Ettenmoors |
| **Misty Mountains** | Misty Mountains peaks, Misty Foothills, the High Pass |
| **Wilderland** | Mirkwood (giant dark trees, cobwebs, gloomy fog), Eaves of Mirkwood, Vales of Anduin, Dale, Erebor (the Lonely Mountain) |
| **Lothlórien** | The Golden Wood (huge golden mallorn trees), Cerin Amroth |
| **Rohan** | Plains of Rohan, Fangorn Forest, Emyn Muil |
| **Gondor** | Fields of Gondor (Númenórean ruins), Ithilien, the White Mountains |
| **Mordor** | Plateau of Gorgoroth (ash, spires, orc towers), Ephel Dúath, Orodruin, the Dead Marshes |
| **Harad** | Deserts of Harad, Near Harad savanna |
| Seas & coasts | Belegaer, Sea of Rhûn, Ice-bay of Forochel, Grey Havens shore, stony and ashen shores |

### Custom biomes (the generated datapack)
Each biome declares `customDerivitives`. From these, Iris writes a datapack of custom biomes into the
world. The datapack gives each land its own sky, fog, water, grass and leaf colours, plus ambient
particles:
- **Mordor** has a red-black sky with falling ash, and Orodruin gives off lava sparks.
- **Lothlórien** has golden leaves. Mallorn leaves are oak leaves tinted gold by the biome, on silver
  birch-wood trunks.
- **Mirkwood** and the **Dead Marshes** have dark green fog and drifting spores.
- **Angmar** and the **Misty Mountains** have cold grey skies, snow and white ash.

### Roads
All land biomes share an identical road surface layer, and Iris seeds that layer from the world's
terrain seed. As a result the roads form one continuous, connected network across every region and
biome border. Each land paints the roads in its own style:

| Land | Road style |
|---|---|
| Shire, Rohan, forests | dirt paths |
| Eriador wilds, Misty passes, Dale | cobbled or stone-brick roads |
| Gondor | polished stone roads |
| Lothlórien | mossy elven stone |
| Angmar | cobblestone |
| Mordor | blackstone roads |
| Dead Marshes | mud-brick causeways |
| Harad | sandstone |

Vanilla structures such as villages still generate, and Iris flattens the terrain under them.

## Install (plugin)

1. Put the Iris plugin jar in `plugins/` and start the server once.
2. Copy the `middleearth` folder from this directory to `plugins/Iris/packs/middleearth`.
3. **Restart the server.** Iris compiles the pack and registers its custom biome datapack on boot.
4. Create and enter the world:
   ```
   /iris create middleearth type=middleearth seed=1337
   /iris tp middleearth
   ```
5. Optional: pregenerate chunks with `/iris pregen start 5000 world=middleearth center=0,0`.

To look around and tweak the pack live, use `/iris studio open middleearth`.

## Tweaking

- **Roads.** Road settings live at the top of `build_pack.py`:
  - `ROAD_ZOOM` sets the spacing between junctions. Larger values put roads further apart.
  - `ROAD_PATH_WEIGHT` and `ROAD_VERGE_WEIGHT` set road and verge width.

  After editing, run `python3 build_pack.py middleearth` to regenerate the pack. Every land biome
  must keep an identical layer 0, or the roads stop connecting across biome borders. The script
  handles this for you.
- **Region size.** Set `regionZoom` in `dimensions/middleearth.json`. A larger value gives bigger lands.
- **Land vs. sea.** Set `landChance` in the dimension file.
- **Region frequency.** Set `rarity` in `regions/*.json`. A higher value makes a region rarer.
  Mordor, Angmar, the Misty Mountains and Harad are set to 2, and Lothlórien to 3.
