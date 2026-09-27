package com.hywbridge.mixin;

import com.hywbridge.util.BridgeSelectionStorage;
import com.hywbridge.util.NPCOwnerHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import noppes.npcs.entity.EntityNPCInterface;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ydmsama.hundred_years_war.main.network.packets.SelectionPacket;

import java.util.List;
import java.util.UUID;

@Mixin(value = SelectionPacket.class, remap = false)
public class SelectionSystemMixin {

    // handle() runs for every selection change, including an empty list (deselect)
    @Inject(method = "handle", at = @At("HEAD"))
    private static void injectHandleHead(ServerPlayer player, SelectionPacket packet, CallbackInfo ci) {
        if (player == null) return;
        BridgeSelectionStorage.clear(player);
    }

    @Inject(method = "handle", at = @At("TAIL"))
    private static void injectHandleTail(ServerPlayer player, SelectionPacket packet, CallbackInfo ci) {
        if (player == null) return;

        List<UUID> ids = ((SelectionPacketAccessor) packet).hywbridge$getSelectedEntityIds();
        if (ids == null || ids.isEmpty()) return;

        ServerLevel level = player.serverLevel();
        for (UUID uuid : ids) {
            Entity entity = level.getEntity(uuid);
            if (entity instanceof EntityNPCInterface npc && NPCOwnerHelper.isHywManagedNPCServer(npc)) {
                BridgeSelectionStorage.addEntity(player, npc);
            }
        }
    }
}
