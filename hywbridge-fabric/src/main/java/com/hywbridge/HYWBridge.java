package com.hywbridge;

import com.hywbridge.command.HYWBridgeCommands;
import com.hywbridge.network.OwnerSyncPayload;
import com.hywbridge.util.FactionSyncHandler;
import com.hywbridge.util.NPCOwnerHelper;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.MixinEnvironment;

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
        if (Boolean.getBoolean("hywbridge.audit")) {
            // CI smoke test: apply every pending mixin now, so a missing target fails the run, then stop
            ServerLifecycleEvents.SERVER_STARTED.register(server -> {
                MixinEnvironment.getCurrentEnvironment().audit();
                LOGGER.info("HYWBRIDGE_AUDIT_OK");
                server.halt(false);
            });
        }
        LOGGER.info("HYW Bridge initialized!");
    }
}
