# 角色转布偶提示词

替换角色特征及表情要求后交给内置图像工具。原图可以是头像或插画，不要求已有玩偶造型。

```text
Use case: style-transfer.
Asset type: one complete seated 3D stuffed plush doll, transparent PNG, normal undeformed pose for a later squash/stretch animation.

Image 1: primary character identity reference. Preserve its recognizable hair, eye color, costume, ornaments and proportions.
Additional character references: describe each image's role explicitly. Multiple pictures of the same character should produce ONE doll.
Plush style reference: use only fabric texture, stuffed rounded construction, soft upper-left lighting and rendering quality. Do not copy its character identity, face, expression or outfit.

Expression: [preserve the source gaze, eyelids, brows and mouth / user explicitly requested a cute small closed smile and relaxed lively eyes].

Translate the character into a high-quality padded fabric plush: huge softly rounded stuffed head, tiny seated body, thick padded fabric hair, plump limbs, fine short-pile textile, restrained seams, embroidered or printed facial details, gentle internal shadows.

When only an upper-body reference is available, complete a coherent small seated body using the visible costume: tiny relaxed hands, short seated legs, matching simple fabric feet and a conservative continuation of the garment. Do not invent unrelated costume motifs.

One complete doll, seated with feet forward, centered on a square canvas. Preserve all visible identity details. Leave transparent margins; highest hair near 8% and feet near 94% of image height. Keep hair, accessories, hands and feet uncropped.

True transparent alpha outside the doll and through gaps. Remove the source background and source labels. No scene, ground, external shadow plane, text, watermark or extra characters. Decorative scene props are not doll accessories unless requested. No shiny plastic or human skin. Keep the doll undeformed; animation is applied separately by code.
```

对于可爱风，采用小幅闭嘴微笑、放松的眉毛和明亮眼神，保持角色原有眼睛颜色。用户没有指定更换表情时，不默认改成笑脸。
