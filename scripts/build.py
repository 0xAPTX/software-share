"""Build a static catalog and stable download links from public Release assets."""
import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
from string import Template
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = '0xAPTX/software-share'


def catalog(releases, config, repository=REPOSITORY):
    # gh --paginate --slurp returns an array of API response pages.
    if releases and isinstance(releases[0], list):
        releases = [release for page in releases for release in page]
    overrides = {(item['release'], item['asset']): item for item in config['items']}
    items, seen = [], set()
    for release in releases:
        if release.get('draft') or release.get('prerelease'):
            continue
        for asset in release.get('assets', []):
            if asset.get('state') != 'uploaded':
                continue
            url = asset.get('browser_download_url', '')
            parsed = urlparse(url)
            if (parsed.scheme != 'https' or parsed.netloc != 'github.com'
                    or not parsed.path.startswith('/' + repository + '/releases/download/')):
                raise ValueError('Release asset must belong to this repository')
            extra = overrides.get((release['tag_name'], asset['name']), {})
            slug = extra.get('slug') or re.sub(r'[^a-z0-9-]+', '-', release['tag_name'].lower()).strip('-') + '-' + str(asset['id'])
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
                raise ValueError('Invalid download slug: ' + slug)
            if slug in seen:
                raise ValueError('Duplicate download slug: ' + slug)
            seen.add(slug)
            digest = asset.get('digest') or ''
            checksum = digest.removeprefix('sha256:') if digest.startswith('sha256:') else ''
            expected = extra.get('sha256', '')
            if expected and checksum and expected != checksum:
                raise ValueError('Uploaded file checksum differs from software.json')
            checksum = checksum or expected
            if checksum and not re.fullmatch(r'[0-9a-f]{64}', checksum):
                raise ValueError('Invalid SHA-256')
            suffix = Path(asset['name']).suffix.lower()
            platform = extra.get('platform') or {'.exe': 'Windows', '.msi': 'Windows', '.dmg': 'macOS', '.pkg': 'macOS', '.apk': 'Android', '.appimage': 'Linux'}.get(suffix, '通用文件')
            items.append({
                'slug': slug, 'name': extra.get('name', asset['name']),
                'version': extra.get('version', release['tag_name']),
                'platform': platform, 'category': extra.get('category', '软件与文件'),
                'description': extra.get('description', '已发布的共享文件，可直接下载安装包。'),
                'note': extra.get('note', ''), 'sha256': checksum,
                'url': url, 'filename': asset['name'], 'size': asset['size'],
                'publishedAt': release.get('published_at') or asset['created_at'],
                'releaseUrl': 'https://github.com/' + repository + '/releases/tag/' + release['tag_name'],
            })
    return sorted(items, key=lambda item: item['publishedAt'], reverse=True)


def size_label(size):
    if size >= 1024 ** 3:
        return f'{size / 1024 ** 3:.2f} GiB'
    return f'{size / 1024 ** 2:.1f} MiB'


def date_label(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')


def render(template, **values):
    return Template((ROOT / 'web' / template).read_text()).substitute(values)


def card(item):
    values = {key: escape(str(value), quote=True) for key, value in item.items()}
    values.update(size=size_label(item['size']), date=date_label(item['publishedAt']))
    values['extension'] = escape(Path(item['filename']).suffix.lstrip('.').upper() or 'FILE')
    values['checksum'] = ('<details class="checksum"><summary>查看 SHA-256 校验值</summary><code>' + item['sha256'] + '</code></details>') if item['sha256'] else ''
    values['note'] = ('<p class="compatibility">' + values['note'] + '</p>') if item['note'] else ''
    return render('card.html', **values)


def build(releases, output=ROOT / 'dist'):
    config = json.loads((ROOT / 'software.json').read_text())
    repository = os.environ.get('GITHUB_REPOSITORY', REPOSITORY)
    items = catalog(releases, config, repository)
    output.mkdir(parents=True, exist_ok=True)
    for asset in ['style.css', 'catalog.js', 'download.js', 'icon.svg']:
        shutil.copyfile(ROOT / 'web' / asset, output / asset)
    (output / '.nojekyll').write_text('')
    (output / 'catalog.json').write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n')
    content = ''.join(card(item) for item in items) or '<p class="empty">首个软件正在准备中，稍后再来看看。</p>'
    (output / 'index.html').write_text(render('index.html', cards=content, count=len(items), repo=repository))
    for item in items:
        page = output / 'download' / item['slug']
        page.mkdir(parents=True, exist_ok=True)
        values = {key: escape(str(value), quote=True) for key, value in item.items()}
        values['size'] = size_label(item['size'])
        (page / 'index.html').write_text(render('download.html', **values))
    print(f'Built {len(items)} download entries into {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--releases', required=True, type=Path)
    args = parser.parse_args()
    build(json.loads(args.releases.read_text()))
