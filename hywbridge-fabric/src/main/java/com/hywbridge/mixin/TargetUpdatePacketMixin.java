package com.hywbridge.mixin;

import com.hywbridge.HYWBridge;
import com.hywbridge.util.BridgeSelectionStorage;
import com.hywbridge.util.NPCOwnerHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import noppes.npcs.entity.EntityNPCInterface;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ydmsama.hundred_years_war.main.network.packets.TargetUpdatePacket;

import java.util.UUID;

@Mixin(value = TargetUpdatePacket.class, remap = false)
public class TargetUpdatePacketMixin {

    @Inject(method = "handle", at = @At("HEAD"))
    private static void injectAttackForCustomNPCs(ServerPlayer player, TargetUpdatePacket packet,
                                                  CallbackInfo ci) {
        if (player == null) return;
        if (BridgeSelectionStorage.isEmpty(player)) return;

        UUID targetUUID = ((TargetUpdatePacketAccessor) packet).hywbridge$getTargetUUID();
        if (targetUUID == null) return;

        Entity target = player.serverLevel().getEntity(targetUUID);
        if (!(target instanceof LivingEntity livingTarget)) return;

        for (Entity entity : BridgeSelectionStorage.getCustomEntities(player)) {
            if (entity instanceof EntityNPCInterface npc && NPCOwnerHelper.isHywManagedNPC(npc)) {
                npc.setTarget(livingTarget);
                HYWBridge.LOGGER.debug("Setting attack target {} for NPC {}",
                        livingTarget.getUUID(), npc.getUUID());
            }
        }
    }
}
