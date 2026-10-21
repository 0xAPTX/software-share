from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build


def release():
    return {
        'tag_name': 'itunes-12.6.3.6', 'draft': False, 'prerelease': False,
        'published_at': '2026-10-21T14:00:00Z',
        'assets': [{
            'id': 42, 'state': 'uploaded', 'name': 'iTunes-12.6.3.6-Windows-x64.exe',
            'size': 270075208, 'created_at': '2026-10-21T13:59:00Z',
            'digest': 'sha256:fc1af1adeb31b4dc3ba8c3b68a5b329d4dc5b21f3c8c251fd72b1f31bd0116e6',
            'browser_download_url': 'https://github.com/0xAPTX/software-share/releases/download/itunes-12.6.3.6/iTunes-12.6.3.6-Windows-x64.exe',
        }],
    }


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((build.ROOT / 'software.json').read_text())

    def test_public_uploaded_assets_and_api_pagination(self):
        draft = dict(release(), draft=True)
        prerelease = dict(release(), prerelease=True)
        unfinished = release()
        unfinished['assets'][0]['state'] = 'starter'
        items = build.catalog([[draft, prerelease], [unfinished, release()]], self.config)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['slug'], 'itunes')
        self.assertEqual(items[0]['platform'], 'Windows · 64 位')

    def test_new_software_needs_no_configuration(self):
        other = release()
        other['tag_name'] = 'tool-1.0'
        other['assets'][0].update(name='Tool.dmg', id=123)
        item = build.catalog([other], self.config)[0]
        self.assertEqual(item['slug'], 'tool-1-0-123')
        self.assertEqual(item['platform'], 'macOS')
        other['tag_name'] = '中文软件'
        self.assertEqual(build.catalog([other], self.config)[0]['slug'], 'download-123')

    def test_changed_file_and_untrusted_download_host_are_rejected(self):
        changed = release()
        changed['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaisesRegex(ValueError, 'checksum differs'):
            build.catalog([changed], self.config)
        changed['assets'][0]['browser_download_url'] = 'https://example.com/installer.exe'
        with self.assertRaisesRegex(ValueError, 'this repository'):
            build.catalog([changed], self.config)

    def test_duplicate_or_unsafe_download_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            build.catalog([release(), release()], self.config)
        self.config['items'][0]['slug'] = '../outside'
        with self.assertRaisesRegex(ValueError, 'Invalid download slug'):
            build.catalog([release()], self.config)

    def test_static_pages_point_to_exact_asset_and_escape_names(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build.build([release()], output)
            index = (output / 'index.html').read_text()
            download = (output / 'download/itunes/index.html').read_text()
            self.assertIn('download/itunes/', index)
            self.assertIn(release()['assets'][0]['browser_download_url'], download)
            self.assertIn('id="download-link"', download)
            self.assertTrue((output / 'download.js').exists())
            for filename in ['index.html', 'download/itunes/index.html']:
                HTMLParser().feed((output / filename).read_text())
        item = build.catalog([release()], self.config)[0]
        item['name'] = '<script>alert(1)</script>'
        self.assertNotIn('<script>', build.card(item))
        self.assertIn('&lt;script&gt;', build.card(item))


if __name__ == '__main__':
    unittest.main()
