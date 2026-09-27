package com.hywbridge.mixin;

import com.hywbridge.HYWBridge;
import com.hywbridge.util.BridgeSelectionStorage;
import com.hywbridge.util.NPCOwnerHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import noppes.npcs.entity.EntityNPCInterface;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ydmsama.hundred_years_war.main.network.packets.MoveCommandPacket;

@Mixin(value = MoveCommandPacket.class, remap = false)
public class MoveCommandPacketMixin {

    // HYW calls handle() from MinecraftServer.execute, so this already runs on the server thread
    @Inject(method = "handle", at = @At("HEAD"))
    private static void injectMoveForCustomNPCs(ServerPlayer player, MoveCommandPacket packet,
                                                CallbackInfo ci) {
        if (player == null) return;
        if (BridgeSelectionStorage.isEmpty(player)) return;

        HitResult hitResult = ((MoveCommandPacketAccessor) packet).hywbridge$getHitResult();
        if (hitResult == null) return;
        Vec3 target = hitResult.getLocation();

        for (Entity entity : BridgeSelectionStorage.getCustomEntities(player)) {
            if (entity instanceof EntityNPCInterface npc && NPCOwnerHelper.isHywManagedNPC(npc)) {
                npc.getNavigation().moveTo(target.x, target.y, target.z, 1.0);
                HYWBridge.LOGGER.debug("Moving NPC {} to {}", npc.getUUID(), target);
            }
        }
    }
}
