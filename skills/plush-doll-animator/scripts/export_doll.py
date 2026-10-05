"""从透明 PNG 导出固定脚底的循环 GIF，可同时生成独立网页预览。"""
import argparse
import base64
import html
import json
import math
import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def export(source_path, output_path, preview_path=None, alt='立体布偶', foot_ratio=None, config_path=None):
    config = json.loads((config_path or ROOT / 'assets/motion.json').read_text(encoding='utf-8'))
    duration = int(config['frame_duration_ms'])
    if duration <= 0 or duration % 10:
        raise ValueError('GIF 帧时长必须是正数且为 10ms 的倍数。')
    frame_count = round(config['cycle_seconds'] * 1000 / duration)
    if frame_count < 4 or abs(frame_count * duration - config['cycle_seconds'] * 1000) > 0.001:
        raise ValueError('循环至少需要四个采样帧，时长必须能被 GIF 帧时长整除。')
    original = Image.open(source_path).convert('RGBA')
    if original.width != original.height:
        raise ValueError('输入须为正方形透明 PNG；请先按原比例补透明边距，避免拉伸角色。')
    alpha = original.getchannel('A')
    threshold = config['alpha_threshold']
    bounds = alpha.point(lambda value: 255 if value >= threshold else 0).getbbox()
    if bounds is None or alpha.getextrema()[0] != 0:
        raise ValueError('输入必须有可见玩偶和真实透明背景。')
    if foot_ratio is None:
        foot_ratio = bounds[3] / original.height
    if not 0 < foot_ratio <= 1:
        raise ValueError('脚底支点比例须在 0～1 之间。')

    canvas = tuple(config['canvas_size'])
    target_foot = config['target_foot_y']
    # 把整只玩偶在形变极值时也放进画布；仅缩小显示尺寸，不改变角色比例。
    max_x = max(config['min_scale_x'], config['max_scale_x'])
    max_y = max(config['min_scale_y'], config['max_scale_y'])
    limits = [config['sprite_size']]
    horizontal = max(abs(bounds[0] / original.width - 0.5), abs(bounds[2] / original.width - 0.5)) * max_x
    above = (foot_ratio - bounds[1] / original.height) * max_y
    below = (bounds[3] / original.height - foot_ratio) * max_y
    if horizontal > 0:
        limits.append((canvas[0] / 2 - 12) / horizontal)
    if above > 0:
        limits.append((target_foot - 12) / above)
    if below > 0:
        limits.append((canvas[1] - target_foot - 12) / below)
    size = math.floor(min(limits))
    if size < 1:
        raise ValueError('配置没有足够空间容纳玩偶，请扩大画布或调整脚底目标位置。')
    foot_y = size * foot_ratio
    source = original.resize((size, size), Image.Resampling.LANCZOS)
    # 全部帧共用色表；0 号色留作透明，避免闪色和残影。
    quantized = source.convert('RGB').quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    colors = quantized.getpalette()[:765]
    reference = Image.new('P', (1, 1))
    reference.putpalette(colors + colors[:3])
    output_palette = [0, 0, 0] + colors
    remap = list(range(1, 256)) + [1]
    frames = []
    for index in range(frame_count):
        # 采样 [0, 2π)，不追加重复的首帧或等待帧。
        phase = 2 * math.pi * index / frame_count
        squash = (1 - math.cos(phase)) / 2
        sy = config['max_scale_y'] + (config['min_scale_y'] - config['max_scale_y']) * squash
        sx = config['min_scale_x'] + (config['max_scale_x'] - config['min_scale_x']) * squash
        transform = (1 / sx, 0, size / 2 - canvas[0] / (2 * sx),
                     0, 1 / sy, foot_y - target_foot / sy)
        rgba = source.transform(canvas, Image.Transform.AFFINE, transform,
                                resample=Image.Resampling.BICUBIC)
        rgb = rgba.convert('RGB').quantize(palette=reference, dither=Image.Dither.NONE)
        frame = rgb.point(remap)
        frame.putpalette(output_palette)
        transparent = rgba.getchannel('A').point(lambda value: 255 if value < threshold else 0)
        frame.paste(0, mask=transparent)
        frame.info['transparency'] = 0
        frames.append(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output_path, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, transparency=0, disposal=2, optimize=False)

    if preview_path is not None:
        template = (ROOT / 'assets/preview.template.html').read_text(encoding='utf-8')
        values = {
            'PNG_SRC': 'data:image/png;base64,' + base64.b64encode(source_path.read_bytes()).decode('ascii'),
            'GIF_SRC': html.escape(Path(os.path.relpath(output_path, preview_path.parent)).as_posix(), quote=True),
            'ALT': html.escape(alt, quote=True),
            'FOOT_PERCENT': format(foot_ratio * 100, '.6f'),
            'FOOT_PADDING': format(1 - foot_ratio, '.9f'),
            'CYCLE_LABEL': format(config['cycle_seconds'], '.2f'),
            'CYCLE_SECONDS': str(config['cycle_seconds']),
            'TEMPO_MIN': str(min(0.2, config['cycle_seconds'])),
            'TEMPO_MAX': str(max(3, config['cycle_seconds'])),
            'DESKTOP_SIZE': format(350 * size / config['sprite_size'], '.3f'),
            'MOBILE_SIZE': format(280 * size / config['sprite_size'], '.3f'),
        }
        values.update({key.upper(): str(config[key]) for key in
                       ['min_scale_y', 'max_scale_y', 'min_scale_x', 'max_scale_x']})
        for key, value in values.items():
            template = template.replace('{{' + key + '}}', value)
        if '{{' in template:
            raise ValueError('预览模板存在未填充参数。')
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_text(template, encoding='utf-8')

    manifest = {'source': str(source_path), 'gif': str(output_path),
                'preview': str(preview_path) if preview_path else None,
                'foot_ratio': foot_ratio, 'effective_sprite_size': size, 'motion': config}
    output_path.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--preview', type=Path)
    parser.add_argument('--alt', default='立体布偶')
    parser.add_argument('--config', type=Path, help='可选的动作配置 JSON；默认使用技能自带的已确认参数。')
    parser.add_argument('--foot-ratio', type=float, help='可选，手动指定脚底位置；默认按透明图片可见底边自动定位。')
    args = parser.parse_args()
    source_path = args.input.resolve()
    output_path = (args.output or source_path.with_name(source_path.stem + '-squash.gif')).resolve()
    result = export(source_path, output_path, args.preview.resolve() if args.preview else None, args.alt, args.foot_ratio, args.config.resolve() if args.config else None)
    print(json.dumps(result, ensure_ascii=False))
