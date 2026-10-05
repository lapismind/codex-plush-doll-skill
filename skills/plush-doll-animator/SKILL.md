---
name: plush-doll-animator
description: Use when a user wants a character image or existing doll turned into a transparent 3D plush, or asks for a squishy squash-and-stretch doll GIF with a fixed foot anchor and seamless loop. Supports chibi portraits and partial-body references.
---

# Q 弹布偶制作

把角色图转成透明底立体布偶，再按已确认参数导出连续循环。仅需静态图时完成图像阶段即可；用户的角色、表情和动作要求优先于默认预设。

## 确定角色与参考图的分工

- 判断图片是否属于同一角色。两张同一角色参考图制作一只布偶；不按图片数量推断角色数量。
- 原图提供身份、发型、服装、饰品和表情。默认保留原表情；用户明确说“可爱风”等时按要求更换。
- 半身插画或头像也可制作完整坐姿布偶：沿可见服装补齐小身体、手、短腿和布制脚，保留头身比例与角色特征。
- 场景中的南瓜、水壶等物品不自动成为玩偶配件。
- 自带 assets/plush-style-reference.png 只参考材质、光照和立体结构；不复制它的脸、表情或角色服装。用户给了其他风格参考时优先使用用户的参考。

## 生成正常形态的透明 PNG

如果已有符合要求的透明底 3D 布偶，且用户只要求动画，直接进入导出阶段，不重复生成图片。

读取 [references/image-prompt.md](references/image-prompt.md)，按实际角色填写身份和表情要求。用环境内置的 image_gen 图像工具进行生成或编辑，开启 transparent_background=true。本地参考图先用 view_image 查看。

生成一只完整、正常未变形的坐姿布偶，正方形构图，完整边缘及透明余量。将成品复制到用户项目，并保存实际提示词及每张参考图的作用。检查角色特征、表情和真实 alpha；动画阶段使用这张正常 PNG。

内置图像工具缺失或失败时报告限制，不擅自切换 API、模型或索取 API key。

## 导出动画

技能内脚本不依赖当前目录，也不需要原项目。用 Python 和 Pillow；缺少 Pillow 时在合适环境安装。调用前可运行 scripts/export_doll.py --help。

默认配置 assets/motion.json：
- 每圈 0.5 秒，20ms 采样，无限循环。
- 正常尺寸为 1；最高时横向 0.83、纵向 1.27；最扁时横向 1.12、纵向 0.62。
- 连续余弦曲线，脚底固定，不跳跃或上下平移，不插入等待帧，不重复追加首帧。
- 输出 560 × 560 透明 GIF。脚底按输入图片的可见底边定位，可用 --foot-ratio 修正。
- 所有帧使用共同色表及 disposal=2；GIF 仅支持二值透明，PNG 保留原 alpha。

调用 scripts/export_doll.py，使用绝对脚本路径和用户项目中的输入输出路径：

    python /skill-root/scripts/export_doll.py --input /project/doll.png --output /project/doll.gif --preview /project/preview.html --alt "角色布偶"

将 /skill-root 替换为本技能实际目录。输入应是正方形透明 PNG；非正方形先按原比例补透明边距，不直接拉伸角色。

脚本同时输出 GIF、记录配置和支点的 JSON，以及可离线打开的预览。预览内嵌 PNG；移动 HTML 时，连同其相对路径的 GIF 一起移动。为每个角色单独命名，除非用户指定替换，否则不覆盖已有角色产物。

用户要求对齐另一段视频时，读取 [references/video-matching.md](references/video-matching.md)，再通过 --config 传入项目内的配置副本。默认预设不是所有视频的通用测量结果。

## 验证与交付

1. 对照原图确认身份及用户要求的表情；最高与最扁状态都完整可见。
2. 运行 python /skill-root/scripts/verify_gif.py /project/doll.gif，检查透明、无限循环、整圈 500ms、固定底边和接缝。使用其他周期时传 --expected-ms；帧间隔变化时传 --sample-ms。
3. 浏览器查看预览；确认脚底在同一地面线上、没有上下位移，最高状态允许拉长。检查手机宽度和暂停控制。
4. 提供 PNG、GIF、预览和实际提示词路径；可在 Codex 中打开预览。说明图像用了内置 GPT Image，动画由代码生成。

确定性部分由 scripts/export_doll.py 和 assets/motion.json 完成。不要手工另写一套动画参数，导致 GIF 与预览不同。
