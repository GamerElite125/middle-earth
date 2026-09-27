package com.hywbridge.client;

import com.hywbridge.HYWBridge;
import com.hywbridge.network.OwnerSyncPayload;
import com.hywbridge.util.NPCOwnerHelper;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;

public class HYWBridgeClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        // Fabric runs play-phase receivers on the client thread
        ClientPlayNetworking.registerGlobalReceiver(OwnerSyncPayload.TYPE, (payload, context) -> {
            if (payload.ownerUUID().isPresent()) {
                NPCOwnerHelper.cacheOwner(
                        payload.npcUUID(), payload.ownerUUID().get(), payload.relationToPlayer());
                HYWBridge.LOGGER.debug("Cached owner {} relation={} for NPC {}",
                        payload.ownerUUID().get(), payload.relationToPlayer(), payload.npcUUID());
            } else {
                NPCOwnerHelper.removeFromCache(payload.npcUUID());
            }
        });
    }
}
