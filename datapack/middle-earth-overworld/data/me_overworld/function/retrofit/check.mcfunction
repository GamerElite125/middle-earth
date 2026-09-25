# Only chunks from before the pack (bedrock still at the corner).
$execute unless loaded $(x) 0 $(z) run return 0
$execute unless loaded $(xm) 0 $(zm) run return 0
$execute unless loaded $(xp) 0 $(zp) run return 0
$execute unless loaded $(xm) 0 $(zp) run return 0
$execute unless loaded $(xp) 0 $(zm) run return 0
$execute unless block $(x) -64 $(z) minecraft:bedrock run return 0
$execute positioned $(x) 0 $(z) run function me_overworld:retrofit/generate
$setblock $(x) -64 $(z) minecraft:reinforced_deepslate
scoreboard players remove #budget me_ow 1
