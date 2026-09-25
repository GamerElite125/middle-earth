scoreboard objectives add me_ow dummy
scoreboard players set #16 me_ow 16
execute unless score #enabled me_ow matches 0..1 run scoreboard players set #enabled me_ow 1
schedule function me_overworld:retrofit/loop 10t replace
