scoreboard players operation #cx me_ow = #px me_ow
scoreboard players operation #cx me_ow += #dx me_ow
scoreboard players operation #cx me_ow *= #16 me_ow
execute store result storage me_overworld:tmp c.x int 1 run scoreboard players get #cx me_ow
execute store result storage me_overworld:tmp c.xm int 1 run scoreboard players remove #cx me_ow 16
execute store result storage me_overworld:tmp c.xp int 1 run scoreboard players add #cx me_ow 32
scoreboard players operation #cz me_ow = #pz me_ow
scoreboard players operation #cz me_ow += #dz me_ow
scoreboard players operation #cz me_ow *= #16 me_ow
execute store result storage me_overworld:tmp c.z int 1 run scoreboard players get #cz me_ow
execute store result storage me_overworld:tmp c.zm int 1 run scoreboard players remove #cz me_ow 16
execute store result storage me_overworld:tmp c.zp int 1 run scoreboard players add #cz me_ow 32
function me_overworld:retrofit/check with storage me_overworld:tmp c
