#!/usr/bin/env python3
"""Build a new XCursor theme from the vector asset; never replace an existing theme."""
import argparse
import io
from pathlib import Path
import struct
import subprocess
from PIL import Image


def build(directory):
    directory = Path(directory)
    if directory.exists():
        raise ValueError('theme directory already exists; refusing overwrite')
    svg = Path(__file__).resolve().parents[1] / 'native/agent-cursor.svg'
    chunks = []
    for size in (24, 32, 48, 64):
        raw = subprocess.check_output(['rsvg-convert', '-w', str(size), '-h', str(size), str(svg)])
        image = Image.open(io.BytesIO(raw)).convert('RGBA')
        rgba = image.tobytes()
        pixels = [((a << 24) | ((r*a//255) << 16) | ((g*a//255) << 8) | (b*a//255))
                  for r,g,b,a in zip(rgba[0::4],rgba[1::4],rgba[2::4],rgba[3::4])]
        hotspot = round(size*18/64)
        chunks.append((size, struct.pack('<9I',36,0xfffd0002,size,1,size,size,hotspot,hotspot,0)
                       + struct.pack('<' + str(len(pixels)) + 'I', *pixels)))
    offset = 16 + len(chunks)*12
    toc = bytearray()
    for size, chunk in chunks:
        toc.extend(struct.pack('<3I',0xfffd0002,size,offset));offset += len(chunk)
    data = struct.pack('<4I',0x72756358,16,0x10000,len(chunks)) + toc + b''.join(c for _,c in chunks)
    cursors = directory / 'cursors'
    cursors.mkdir(parents=True)
    (cursors / 'left_ptr').write_bytes(data)
    aliases = {'default','arrow','text','pointer','hand1','hand2','watch','wait','crosshair','move','xterm'}
    reference = Path('/usr/share/icons/Adwaita/cursors')
    if reference.is_dir():aliases.update(p.name for p in reference.iterdir())
    for alias in sorted(aliases - {'left_ptr'}):
        (cursors / alias).symlink_to('left_ptr')
    (directory / 'index.theme').write_text('[Icon Theme]\nName=Computer Use Agent\nInherits=Adwaita\n')
    return directory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(build(parser.parse_args().directory))
