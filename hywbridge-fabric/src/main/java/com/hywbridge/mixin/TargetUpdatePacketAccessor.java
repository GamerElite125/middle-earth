package com.hywbridge.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import ydmsama.hundred_years_war.main.network.packets.TargetUpdatePacket;

import java.util.UUID;

@Mixin(value = TargetUpdatePacket.class, remap = false)
public interface TargetUpdatePacketAccessor {
    @Accessor("targetUUID")
    UUID hywbridge$getTargetUUID();
}
