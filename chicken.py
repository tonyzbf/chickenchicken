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

import asyncio
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

import simplejson as json
import aiohttp
from bs4 import BeautifulSoup

PREFIX = 'https://www.youtube.com/watch?v='
session: aiohttp.ClientSession = None

SVG = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1920px" height="1200px"
    viewBox="0 0 1920px 1200px">
    <style>
        .tile {
            fill: #245093;
            fill-opacity: 0;
        }
        .tile:hover {
            fill-opacity: 30%%;
        }
    </style>
    <image href="chicken_.png" WIDTH="1920" HEIGHT="1200" ALT="" />
    %(svg)s
</svg>
"""
TEMPLATE = """
<a href="%(url)s" target="_blank">
    <rect class="tile" width="%(dimension)dpx" height="%(dimension)dpx" x="%(x)dpx" y="%(y)dpx">
        <title>%(title)s</title>
    </rect>
</a>
"""

webpages = {}


def conform_url(u: str):
    s = urlsplit(u)
    if s.scheme:
        return u
    return f'{PREFIX}{u}'


async def load_title(info: dict):
    page = webpages.get(info['url'])
    if page:
        info['title'] = page['title']
        return
    async with session.get(info['url']) as res:
        text = await res.text()
        soup = BeautifulSoup(text, 'html.parser')
        info['title'] = title = soup.title.get_text().replace(' - YouTube', '').strip()
        webpages[info['url']] = {'title': title, 'tiles': [], 'count': 0}


def get_tile(line: str):
    x, y, url = line.split(',', 3)
    url = conform_url(url)
    return {'x': int(x), 'y': int(y), 'url': url}


def get_svg(info: dict, offset_x: int = 0, offset_y: int = 0):
    info['x'] += offset_x
    info['y'] += offset_y
    return (TEMPLATE % {**info, 'title': escape(info['title'])}).strip()


async def main():
    global session
    session = aiohttp.ClientSession()

    tiles = []
    for fi, dim in [('large', 240), ('medium', 160), ('small', 120)]:
        with open(f'{fi}-tiles.csv') as f:
            lines = f.read()
            tiles.extend({**get_tile(line), 'dimension': dim} for line in lines.split('\n'))

    jobs = [load_title(info) for info in tiles]
    await asyncio.gather(*jobs)

    for tile in tiles:
        page = webpages[tile['url']]
        page['count'] += 1
        page['tiles'].append([tile['x'], tile['y'], tile['dimension']])

    with open('metadata.json', 'w+') as f:
        json.dump(webpages, f)

    with open('map.svg', 'w+') as f:
        elements = [get_svg(tile, offset_y=720 if tile['dimension'] == 160 else 0) for tile in tiles]
        f.write(SVG % {'svg': '\n'.join(elements)})

    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
