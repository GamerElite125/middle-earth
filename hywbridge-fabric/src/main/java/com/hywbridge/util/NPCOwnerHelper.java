package com.hywbridge.util;

import com.hywbridge.HYWBridge;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.core.UUIDUtil;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import noppes.npcs.entity.EntityNPCInterface;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class NPCOwnerHelper {

    /**
     * Owner of a CustomNPC, saved with the entity. Replaces the Forge "persistent data"
     * tag "hyw_owner", which does not exist on Fabric.
     */
    public static final AttachmentType<UUID> OWNER = AttachmentRegistry.<UUID>builder()
            .persistent(UUIDUtil.CODEC)
            .buildAndRegister(ResourceLocation.fromNamespaceAndPath(HYWBridge.MOD_ID, "hyw_owner"));

    private static final Map<UUID, UUID> clientOwnerCache = new ConcurrentHashMap<>();
    private static final Map<UUID, Integer> clientRelationCache = new ConcurrentHashMap<>();

    /** Forces class loading so the attachment type is registered during mod init. */
    public static void init() {
    }

    public static void setOwner(EntityNPCInterface npc, UUID ownerUUID) {
        npc.setAttached(OWNER, ownerUUID);
        clientOwnerCache.put(npc.getUUID(), ownerUUID);
    }

    public static void setOwner(EntityNPCInterface npc, Player player) {
        setOwner(npc, player.getUUID());
    }

    public static UUID getOwnerUUID(EntityNPCInterface npc) {
        // Our own attachment first: it does not depend on the NPC's advanced/scenes data
        UUID stored = npc.getAttached(OWNER);
        if (stored != null) return stored;
        // Fallback: CustomNPCs' native owner, only once advanced data is initialized
        try {
            if (npc.advanced == null || npc.advanced.scenes == null) return null;
            LivingEntity owner = npc.getOwner();
            if (owner instanceof Player p) return p.getUUID();
        } catch (Exception e) {
            // advanced not yet initialized while loading
        }
        return null;
    }

    public static boolean isHywManagedNPCServer(EntityNPCInterface npc) {
        if (getOwnerUUID(npc) != null) return true;
        return npc.faction != null && !npc.faction.name.isEmpty();
    }

    public static boolean isHywManagedNPC(Entity entity) {
        if (!(entity instanceof EntityNPCInterface npc)) return false;
        if (clientOwnerCache.containsKey(npc.getUUID())) return true;
        if (clientRelationCache.containsKey(npc.getUUID())) return true;
        return getOwnerUUID(npc) != null;
    }

    public static UUID getOwnerUUIDClientSafe(EntityNPCInterface npc) {
        UUID cached = clientOwnerCache.get(npc.getUUID());
        if (cached != null) return cached;
        return getOwnerUUID(npc);
    }

    public static int getRelationToPlayer(UUID npcUUID) {
        return clientRelationCache.getOrDefault(npcUUID, -1);
    }

    public static void cacheOwner(UUID npcUUID, UUID ownerUUID, int relation) {
        if (ownerUUID != null) clientOwnerCache.put(npcUUID, ownerUUID);
        clientRelationCache.put(npcUUID, relation);
    }

    public static void removeFromCache(UUID npcUUID) {
        clientOwnerCache.remove(npcUUID);
        clientRelationCache.remove(npcUUID);
    }

    public static Player getOwnerPlayer(EntityNPCInterface npc, ServerLevel level) {
        UUID ownerUUID = getOwnerUUID(npc);
        if (ownerUUID == null) return null;
        return level.getServer().getPlayerList().getPlayer(ownerUUID);
    }
}
