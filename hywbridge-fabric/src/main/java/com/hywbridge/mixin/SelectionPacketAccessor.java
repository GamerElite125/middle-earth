package com.hywbridge.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import ydmsama.hundred_years_war.main.network.packets.SelectionPacket;

import java.util.List;
import java.util.UUID;

@Mixin(value = SelectionPacket.class, remap = false)
public interface SelectionPacketAccessor {
    @Accessor("selectedEntityIds")
    List<UUID> hywbridge$getSelectedEntityIds();
}
