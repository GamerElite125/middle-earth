package com.hywbridge.network;

import com.hywbridge.HYWBridge;
import net.minecraft.core.UUIDUtil;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

import java.util.Optional;
import java.util.UUID;

/**
 * Server -> client: who owns a CustomNPC and how it relates to the receiving player.
 * relationToPlayer: 0 = neutral, 1 = friendly, 2 = hostile
 */
public record OwnerSyncPayload(UUID npcUUID, Optional<UUID> ownerUUID, int relationToPlayer)
        implements CustomPacketPayload {

    public static final Type<OwnerSyncPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(HYWBridge.MOD_ID, "owner_sync"));

    public static final StreamCodec<FriendlyByteBuf, OwnerSyncPayload> CODEC = StreamCodec.composite(
            UUIDUtil.STREAM_CODEC, OwnerSyncPayload::npcUUID,
            ByteBufCodecs.optional(UUIDUtil.STREAM_CODEC), OwnerSyncPayload::ownerUUID,
            ByteBufCodecs.VAR_INT, OwnerSyncPayload::relationToPlayer,
            OwnerSyncPayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
