import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/plush-doll-animator'


def load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load('export_doll')
verifier = load('verify_gif')


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.png'
        image = Image.new('RGBA', (160, 160))
        ImageDraw.Draw(image).rectangle((30, 20, 130, 140), fill=(90, 160, 210, 255))
        image.save(self.source)

    def test_export_loop_and_self_contained_preview(self):
        output = self.root / 'doll.gif'
        preview = self.root / 'preview.html'
        exporter.export(self.source, output, preview, '<角色>')
        result = verifier.verify(output)
        self.assertEqual(result['duration_ms'], 500)
        self.assertLessEqual(result['foot_drift_px'], 1)
        text = preview.read_text(encoding='utf-8')
        self.assertIn('data:image/png;base64,', text)
        self.assertIn('&lt;角色&gt;', text)
        self.assertNotIn('{{', text)
        manifest = json.loads(output.with_suffix('.json').read_text(encoding='utf-8'))
        self.assertAlmostEqual(manifest['foot_ratio'], 141 / 160)

    def test_custom_period(self):
        config = json.loads((SKILL / 'assets/motion.json').read_text(encoding='utf-8'))
        config['cycle_seconds'] = 0.8
        path = self.root / 'motion.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        output = self.root / 'custom.gif'
        exporter.export(self.source, output, config_path=path)
        self.assertEqual(verifier.verify(output, 800)['duration_ms'], 800)

    def test_rejects_opaque_or_stretched_input(self):
        for size, expected in [((160, 160), '真实透明'), ((100, 160), '正方形')]:
            Image.new('RGBA', size, (255, 255, 255, 255)).save(self.source)
            with self.assertRaisesRegex(ValueError, expected):
                exporter.export(self.source, self.root / 'invalid.gif')

    def test_full_height_doll_fits_without_changing_shape(self):
        image = Image.new('RGBA', (160, 160))
        ImageDraw.Draw(image).rectangle((40, 0, 120, 159), fill=(90, 160, 210, 255))
        image.save(self.source)
        output = self.root / 'full-height.gif'
        manifest = exporter.export(self.source, output, self.root / 'full-height.html')
        self.assertLess(manifest['effective_sprite_size'], 440)
        verifier.verify(output)

    def test_rejects_too_few_animation_samples(self):
        config = json.loads((SKILL / 'assets/motion.json').read_text(encoding='utf-8'))
        config['cycle_seconds'] = 0.04
        path = self.root / 'short.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '四个采样帧'):
            exporter.export(self.source, self.root / 'short.gif', config_path=path)

    def test_long_period_with_merged_identical_frames(self):
        config = json.loads((SKILL / 'assets/motion.json').read_text(encoding='utf-8'))
        config['cycle_seconds'] = 4
        path = self.root / 'long.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        output = self.root / 'long.gif'
        exporter.export(self.source, output, config_path=path)
        self.assertEqual(verifier.verify(output, 4000)['duration_ms'], 4000)


if __name__ == '__main__':
    unittest.main()
