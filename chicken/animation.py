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
import sys
from itertools import chain
from pathlib import Path

import simplejson as json

sem = None


def make_complex(tiles: dict):
    pipe = []
    i = 0
    for geometry in tiles:
        x, y, d = geometry
        pipe.append(f'[0:v]fps=15,crop={d}:{d}:{x}:{y},scale=iw/2:-1,'
                    f'split[s{i}0][s{i}1];[s{i}0]palettegen[p{i}];[s{i}1][p{i}]paletteuse[out{i}]')
        i += 1
    return pipe


async def main():
    source = Path(sys.argv[1])
    global sem
    sem = asyncio.Semaphore(1)
    with open('metadata.json') as f:
        metadata = json.load(f)
    tiles = [tuple(info['geometry']) for video in metadata.values() for info in video['timestamps'].values()]
    pipes = make_complex(tiles)
    maps = [('-map', f'[out{i}]', '-t', '5.0', source.with_name(f'tile-{g[0]}-{g[1]}.gif').resolve()) for i, g in enumerate(tiles)]  # noqa: ECE001
    proc = await asyncio.create_subprocess_exec(
        *['ffmpeg', '-y', '-ss', '1:02.5', '-i', str(source),
          '-filter_complex', ';'.join(pipes), *chain(*maps)],
    )
    await proc.wait()
