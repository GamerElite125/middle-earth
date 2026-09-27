package com.hywbridge.util;

import com.hywbridge.HYWBridge;
import com.hywbridge.network.OwnerSyncPayload;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import noppes.npcs.controllers.FactionController;
import noppes.npcs.controllers.data.Faction;
import noppes.npcs.controllers.data.PlayerData;
import noppes.npcs.entity.EntityNPCInterface;
import ydmsama.hundred_years_war.main.utils.RelationSystem;
import ydmsama.hundred_years_war.main.utils.TeamRelationData;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public class FactionSyncHandler {

    private static final Map<String, Integer> factionMapping = new HashMap<>();
    private static int tickCounter = 0;
    private static final int SYNC_INTERVAL = 100;

    public static void register() {
        ServerEntityEvents.ENTITY_LOAD.register((entity, level) -> {
            if (!(entity instanceof EntityNPCInterface npc)) return;
            for (ServerPlayer player : level.getServer().getPlayerList().getPlayers()) {
                syncSingleNPC(npc, player);
            }
        });

        ServerTickEvents.END_SERVER_TICK.register(server -> {
            tickCounter++;
            if (tickCounter < SYNC_INTERVAL) return;
            tickCounter = 0;
            for (ServerPlayer player : server.getPlayerList().getPlayers()) {
                syncPlayerFactions(player);
                syncNPCOwners(player);
            }
        });

        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
            ServerPlayer player = handler.getPlayer();
            syncPlayerFactions(player);
            syncNPCOwners(player);
        });
    }

    private static void syncSingleNPC(EntityNPCInterface npc, ServerPlayer player) {
        // Players without the bridge installed client-side cannot receive the payload
        if (!ServerPlayNetworking.canSend(player, OwnerSyncPayload.TYPE)) return;
        try {
            UUID ownerUUID = NPCOwnerHelper.getOwnerUUID(npc);
            int relation = resolveRelation(npc, player);

            if (ownerUUID == null) {
                String factionName = (npc.faction != null && !npc.faction.name.isEmpty())
                        ? npc.faction.name
                        : "neutral_npc";
                ownerUUID = UUID.nameUUIDFromBytes(factionName.getBytes(StandardCharsets.UTF_8));
            }

            ServerPlayNetworking.send(player,
                    new OwnerSyncPayload(npc.getUUID(), Optional.of(ownerUUID), relation));
        } catch (Exception e) {
            HYWBridge.LOGGER.error("Error syncing single NPC {}", npc.getUUID(), e);
        }
    }

    private static void syncPlayerFactions(ServerPlayer player) {
        try {
            String hywTeam = getPlayerTeam(player);
            if (hywTeam == null) return;

            FactionController fc = FactionController.instance;
            if (fc == null) return;

            for (Map.Entry<String, Integer> entry : factionMapping.entrySet()) {
                String teamName = entry.getKey();
                int factionId = entry.getValue();

                Faction faction = fc.factions.get(factionId);
                if (faction == null) continue;

                PlayerData pd = PlayerData.get(player);
                if (pd == null) continue;

                pd.factionData.factionData.put(factionId, hywTeam.equals(teamName) ? 2000 : -1000);
            }
        } catch (Exception e) {
            HYWBridge.LOGGER.error("Error syncing factions for player {}",
                    player.getName().getString(), e);
        }
    }

    public static void syncNPCOwners(ServerPlayer player) {
        try {
            ServerLevel level = player.serverLevel();
            level.getAllEntities().forEach(entity -> {
                if (entity instanceof EntityNPCInterface npc) syncSingleNPC(npc, player);
            });
        } catch (Exception e) {
            HYWBridge.LOGGER.error("Error syncing NPC owners", e);
        }
    }

    public static int resolveRelation(EntityNPCInterface npc, ServerPlayer player) {
        try {
            if (npc.faction != null && !npc.faction.name.isEmpty()) {
                String factionName = npc.faction.name;
                Map<UUID, TeamRelationData> teamMap = RelationSystem.getAllTeams();
                if (teamMap != null) {
                    for (Map.Entry<UUID, TeamRelationData> entry : teamMap.entrySet()) {
                        if (entry.getValue().getTeamName().equalsIgnoreCase(factionName)) {
                            RelationSystem.RelationType rel =
                                    RelationSystem.getRelation(player.getUUID(), entry.getKey());
                            if (rel == RelationSystem.RelationType.HOSTILE) return 2;
                            if (rel == RelationSystem.RelationType.CONTROL
                                    || rel == RelationSystem.RelationType.FRIENDLY) return 1;
                            return 0;
                        }
                    }
                }
            }
        } catch (Exception e) {
            HYWBridge.LOGGER.error("Error resolving relation for NPC {}", npc.getUUID(), e);
        }
        return 0;
    }

    private static String getPlayerTeam(ServerPlayer player) {
        var team = player.getTeam();
        if (team != null) return team.getName();
        UUID teamUUID = RelationSystem.getPlayerTeamUUID(player.getUUID());
        if (teamUUID == null) return null;
        TeamRelationData data = RelationSystem.getTeamRelationData(teamUUID);
        return data != null ? data.getTeamName() : null;
    }

    public static void registerFactionMapping(String hywTeamName, int cnpcFactionId) {
        factionMapping.put(hywTeamName, cnpcFactionId);
        HYWBridge.LOGGER.info("Registered faction mapping: {} -> {}", hywTeamName, cnpcFactionId);
    }
}
