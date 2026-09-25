schedule function me_overworld:retrofit/loop 10t replace
execute unless score #enabled me_ow matches 1 run return 0
execute as @a[gamemode=!spectator] at @s if dimension minecraft:overworld run function me_overworld:retrofit/player
