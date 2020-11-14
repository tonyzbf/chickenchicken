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

import simplejson as json
import aiohttp
from bs4 import BeautifulSoup

PREFIX = 'https://www.youtube.com/watch?v='
session: aiohttp.ClientSession = None

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

    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
