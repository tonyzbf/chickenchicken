# MIT License
#
# Copyright (c) 2020 Tony Wu <tony[dot]wu(at)nyu[dot]edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from xml.sax.saxutils import escape

import simplejson as json

SVG = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
    viewBox="0 0 1920 1200">
    <style>
        .tile {
            fill: #245093;
            fill-opacity: 0;
        }
        .tile:hover {
            fill-opacity: 30%%;
        }
    </style>
    <image href="doug.jpg" WIDTH="1920" HEIGHT="1200" ALT="" />
    %(svg)s
</svg>
"""
TEMPLATE = """
<a href="%(url)s" target="_blank" id="tile-%(x)d-%(y)d" class="entry"
    data-title="%(title)s" data-subscriber="%(subscriber)s">
    <rect class="tile" width="%(dimension)dpx" height="%(dimension)dpx" x="%(x)dpx" y="%(y)dpx">
        <title>%(title)s</title>
    </rect>
</a>
"""


def load(filename):
    with open(filename) as f:
        return json.load(f)


def metadata_to_rects(data: dict):
    rects = []
    for k, v in data.items():
        for sub, time in v['timestamps'].items():
            x, y, d = time['geometry']
            url = f'{k}&t={time["timestamp"]}s'
            rects.append({
                'url': url, 'title': v['title'],
                'x': x, 'y': y, 'dimension': d,
                'subscriber': sub,
            })
    return rects


def parse_smpte(code):
    parts = list(code.split(':'))
    while len(parts) < 4:
        parts.insert(0, 0)
    scale = [3600, 60, 1]
    time = 0
    for i, s in enumerate(scale):
        time += s * int(parts[i])
    return time


def combine(metadata, subscribers):
    for info in metadata.values():
        mapping = {}
        for x, y, d in info['tiles']:
            timestamp = subscribers[f'tile-{x}-{y}']
            name = timestamp['sub']
            time = parse_smpte(timestamp['time'])
            mapping[name] = {'geometry': [x, y, d], 'timestamp': time}
        info['timestamps'] = mapping
        del info['tiles']


def fix_metadata(data):
    for v in data.values():
        for tile in v['tiles']:
            if tile[2] == 160 and tile[1] < 720:
                tile[1] += 720


def dump(info, filename):
    with open(filename, 'w+') as f:
        json.dump(info, f)


def get_rect(info: dict, debug=False):
    ESCAPE = {'title', 'subscriber', 'url'}
    info = {k: escape(v, entities={'"': '&quot;'}) if k in ESCAPE else v for k, v in info.items()}
    if debug:
        info['url'] = 'javascript:'
    return (TEMPLATE % info).strip()


def get_svg(rects: list, debug=False):
    elements = [get_rect(rect, debug) for rect in rects]
    return SVG % {'svg': '\n'.join(elements)}


def update_rect(info: dict):
    info.setdefault('subscriber', '')


def main():
    metadata = load('metadata.json')
    subscribers = load('subscribers.json')
    combine(metadata, subscribers)
    rects = metadata_to_rects(metadata)
    with open('sources1.svg', 'w+') as f:
        f.write(get_svg(rects, False))
    dump(metadata, 'metadata1.json')


if __name__ == '__main__':
    main()
