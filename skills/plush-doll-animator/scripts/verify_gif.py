"""检查透明 Q 弹 GIF 的时长、接缝、底边及构图。"""
import argparse
import json
from pathlib import Path
from PIL import Image


def verify(path, expected_ms=500, sample_ms=20):
    with Image.open(path) as image:
        if image.format != 'GIF' or image.info.get('loop') != 0:
            raise ValueError('需要无限循环的 GIF。')
        frames, durations, bottoms = [], [], []
        for index in range(image.n_frames):
            image.seek(index)
            frame = image.convert('RGBA').copy()
            bounds = frame.getchannel('A').getbbox()
            if bounds is None or not (bounds[0] > 0 and bounds[1] > 0 and bounds[2] < frame.width and bounds[3] < frame.height):
                raise ValueError(f'第 {index} 帧为空或可能裁切。')
            if frame.getpixel((0, 0))[3] != 0:
                raise ValueError(f'第 {index} 帧背景不透明。')
            frames.append(frame)
            durations.append(image.info.get('duration', 0))
            bottoms.append(bounds[3])
        if len(frames) < 3 or sum(durations) != expected_ms:
            raise ValueError(f'循环时长为 {sum(durations)}ms，期望 {expected_ms}ms。')
        if max(bottoms) - min(bottoms) > 1:
            raise ValueError('GIF 可见底边漂移超过一个像素，需检查脚底支点。')
        # 按时间定位邻帧：GIF 编码器可能合并多个相同采样，不能按帧编号判断。
        if sample_ms <= 0 or sample_ms * 4 > expected_ms:
            raise ValueError('采样间隔与循环时长不一致。')
        def at_time(time):
            elapsed = 0
            for frame, duration in zip(frames, durations):
                elapsed += duration
                if time < elapsed:
                    return frame
            return frames[-1]
        left, right = at_time(sample_ms), at_time(expected_ms - sample_ms)
        # 忽略完全透明像素中不可见的 RGB 值。
        left_visible = Image.new('RGB', left.size)
        right_visible = Image.new('RGB', right.size)
        left_visible.paste(left, mask=left.getchannel('A'))
        right_visible.paste(right, mask=right.getchannel('A'))
        if (left.getchannel('A').tobytes() != right.getchannel('A').tobytes()
                or left_visible.tobytes() != right_visible.tobytes()):
            raise ValueError('首帧两侧邻帧不一致，检查接缝或曲线采样。')
        result = {'gif': str(Path(path).resolve()), 'frames': len(frames),
                  'duration_ms': sum(durations), 'size': image.size,
                  'foot_drift_px': max(bottoms) - min(bottoms), 'seamless': True}
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gif', type=Path)
    parser.add_argument('--expected-ms', type=int, default=500)
    parser.add_argument('--sample-ms', type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(verify(args.gif, args.expected_ms, args.sample_ms), ensure_ascii=False))
