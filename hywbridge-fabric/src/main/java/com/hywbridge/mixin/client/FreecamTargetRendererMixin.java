package com.hywbridge.mixin.client;

import com.hywbridge.util.NPCOwnerHelper;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import noppes.npcs.entity.EntityNPCInterface;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ydmsama.hundred_years_war.client.freecam.Freecam;
import ydmsama.hundred_years_war.client.freecam.selection.SelectionHandler;
import ydmsama.hundred_years_war.client.freecam.ui.wheel.CommandWheelHandler;
import ydmsama.hundred_years_war.client.renderer.FreecamTargetRenderer;

import java.util.List;

@Mixin(value = FreecamTargetRenderer.class, remap = false)
public class FreecamTargetRendererMixin {

    @Inject(method = "renderEntityTargets", at = @At("TAIL"))
    private static void injectCustomNPCTargets(PoseStack poseStack, Camera camera, Minecraft mc,
                                               CallbackInfo ci) {
        if (mc.level == null) return;

        boolean shouldRender = Freecam.isEnabled()
                || CommandWheelHandler.getInstance().shouldRenderCommandEffect();
        if (!shouldRender) return;

        SelectionHandler handler = SelectionHandler.getInstance();
        List<Entity> selected = handler.getSelectedEntities();
        Vec3 cameraPos = camera.getPosition();

        MultiBufferSource.BufferSource bufferSource = mc.renderBuffers().bufferSource();
        VertexConsumer vc = bufferSource.getBuffer(RenderType.lines());
        boolean drewAnything = false;

        for (Entity entity : mc.level.entitiesForRendering()) {
            if (!(entity instanceof EntityNPCInterface npc)) continue;
            if (!selected.contains(npc)) continue;
            if (!NPCOwnerHelper.isHywManagedNPC(npc)) continue;

            var targets = handler.getCombinedTargetMap().get(entity);
            if (targets == null || targets.isEmpty()) continue;

            Vec3 entityPos = entity.position().subtract(cameraPos);

            for (var target : targets) {
                String type = target.getType();
                if ("entityTarget".equals(type) || "followTarget".equals(type)) continue;

                BlockPos pos = target.getPosition();
                if (pos == null) continue;

                // Stop drawing once the NPC has arrived (within 2 blocks) and drop the target
                double distToTarget = entity.position().distanceTo(
                        new Vec3(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5));
                if (distToTarget < 2.0) {
                    handler.getCombinedTargetMap().remove(entity);
                    break;
                }

                Vec3 center = new Vec3(
                        pos.getX() + 0.5 - cameraPos.x,
                        pos.getY() + 1.1 - cameraPos.y,
                        pos.getZ() + 0.5 - cameraPos.z);

                float r, g, b;
                if ("target".equals(type) || "formTarget".equals(type)) {
                    r = 0.0F; g = 1.0F; b = 0.0F;
                } else {
                    r = 1.0F; g = 0.0F; b = 0.0F;
                }

                LevelRenderer.renderLineBox(poseStack, vc,
                        center.x - 0.5, center.y, center.z - 0.5,
                        center.x + 0.5, center.y, center.z + 0.5,
                        r, g, b, 1.0F);
                LevelRenderer.renderLineBox(poseStack, vc,
                        center.x - 0.3, center.y, center.z - 0.3,
                        center.x + 0.3, center.y, center.z + 0.3,
                        r, g, b, 1.0F);

                PoseStack.Pose pose = poseStack.last();
                vc.addVertex(pose, (float) entityPos.x, (float) entityPos.y, (float) entityPos.z)
                        .setColor(r, g, b, 1.0F)
                        .setNormal(pose, 0.0F, 1.0F, 0.0F);
                vc.addVertex(pose, (float) center.x, (float) center.y, (float) center.z)
                        .setColor(r, g, b, 1.0F)
                        .setNormal(pose, 0.0F, 1.0F, 0.0F);
                drewAnything = true;
            }
        }

        // This runs from a world-render callback; flush so the lines are not dropped
        if (drewAnything) bufferSource.endBatch(RenderType.lines());
    }
}
