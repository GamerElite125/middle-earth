package com.hywbridge.mixin;

import net.minecraft.world.phys.HitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import ydmsama.hundred_years_war.main.network.packets.MoveCommandPacket;

@Mixin(value = MoveCommandPacket.class, remap = false)
public interface MoveCommandPacketAccessor {
    @Accessor("hitResult")
    HitResult hywbridge$getHitResult();
}
