package com.hywbridge;

import com.hywbridge.command.HYWBridgeCommands;
import com.hywbridge.network.OwnerSyncPayload;
import com.hywbridge.util.FactionSyncHandler;
import com.hywbridge.util.NPCOwnerHelper;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HYWBridge implements ModInitializer {
    public static final String MOD_ID = "hywbridge";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        NPCOwnerHelper.init();
        PayloadTypeRegistry.playS2C().register(OwnerSyncPayload.TYPE, OwnerSyncPayload.CODEC);
        FactionSyncHandler.register();
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) ->
                HYWBridgeCommands.register(dispatcher));
        LOGGER.info("HYW Bridge initialized!");
    }
}
