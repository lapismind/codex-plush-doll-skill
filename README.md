# Codex Q 弹布偶 Skill

把角色图片制作成透明底 3D 布偶，再导出脚底固定、首尾连续的挤压拉伸 GIF。

支持现成玩偶、角色插画和半身头像。默认保留角色自己的表情；也可以明确要求改成可爱笑脸。两张图可以是同一角色的不同参考，不按图片数量决定生成几只玩偶。

![Q 弹布偶示例](examples/silverhair-cute.gif)

## 安装到 Codex

复制 `skills/plush-doll-animator` 整个文件夹到用户的 `.codex/skills/` 下。如果设置了 `CODEX_HOME`，使用其 `skills/` 目录。随后在新会话中调用：

```text
使用 $plush-doll-animator 把这张图片做成透明底 3D 布偶，保留原表情，并生成 Q 弹 GIF。
```

```text
使用 $plush-doll-animator 把这两张同一角色的半身插画做成一只坐姿布偶，表情改成可爱风。
```

Windows PowerShell 安装示例：

```powershell
git clone https://github.com/lapismind/codex-plush-doll-skill.git
Copy-Item -LiteralPath .\codex-plush-doll-skill\skills\plush-doll-animator -Destination "$env:USERPROFILE\.codex\skills\plush-doll-animator" -Recurse
```

## 环境

- 图像阶段：Codex 内置图像生成工具，支持图片参考和透明背景；不需要为此配置 API key。
- 动画阶段：Python 3 和 Pillow，可用 `python -m pip install -r requirements.txt` 安装。
- 输入导出脚本的图片应为正方形透明 PNG，保持正常未变形状态。

## 固定预设

正常尺寸为 1。最高状态为宽 0.83、高 1.27；最扁状态为宽 1.12、高 0.62。每圈 0.5 秒，脚底固定，连续余弦曲线，不跳跃、不等待。GIF 为 560 × 560，透明底、无限循环。

这是本项目确认过的预设。用户提供其他参考视频时，可重新测量，并使用 `--config` 指向另一份配置。

## 已有透明 PNG 的直接导出

```powershell
python skills/plush-doll-animator/scripts/export_doll.py --input /path/to/doll.png --output /path/to/doll.gif --preview /path/to/preview.html --alt "角色布偶"
```

预览内嵌 PNG，可以双击 HTML 离线查看。GIF 下载链接指向同目录或相对路径的 GIF，移动预览时需一起保留 GIF。脚本同时输出 JSON，记录实际脚底支点和动作配置。

```powershell
python skills/plush-doll-animator/scripts/verify_gif.py /path/to/doll.gif
python -m unittest discover -s tests -v
```

风格参考为 GPT Image 生成的布偶素材。原始角色输入、原视频和本机配置不包含在仓库中。
