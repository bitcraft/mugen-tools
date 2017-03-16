"""
    MUGEN Toolkit for python
    Copyright (C) 2012-2016  Leif Theden

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


MUGEN Random Battle Frontend


Features
--------

Creates a new gamemode for MUGEN that is specifically for party play.

Characters are chosen randomly and each match has only one round.

This mode is suitable for collections of all kinds of characters, including
joke characters and cheap ones.  It is a blast to play with lots of friends due
to the unpredictability and craziness!  Have fun!

Because of the instability of MUGEN and the penalty of loading after a crash,
this script creates custom files for each match so that only 2 characters are
loaded and crashes are recovered automatically.


Usage
-----

* Copy this file into your MUGEN folder.
* Rename your chars folder to "all_chars"
* Create a new folder called "chars"
* Run party.py


Rationale
---------

Party play with 3000+ characters makes loading very slow and MUGEN becomes
unstable.  This script will generate files so that only the required characters
are loaded and will automatically recover from errors.  It also bypasses the
main menu and character select screen.


How it Works
------------

The script finds 2 random characters in your "all_chars" folder and copies
them to "chars".  It then launches mugen with command line options for a
"quick match".  If the match lasts less than 5 seconds, it is considered a
crash, then it is lunched again.


Limitations
-----------

This script crudely emulates the drawing system for MUGEN scenes.  It may not
look exactly like it would in MUGEN.


Customization
-------------

This script includes a few variables that you may modify.  Look under
"OPTIONS" below.


Python Support
--------------

This script was developed and tested with:
python 2.7.3, OS X 10.8.2, pygame 1.9.1


leif theden, 2012 - 2015
public domain
"""

import os
import random
import re
import shutil
import subprocess
import time
from io import StringIO

import pyglet

from libmugen import sff
from libmugen.character import Character

base_dir = 'Z:\\Leif\\games\\mugen\\dist\\mugen-1\\'
# launch_cmd = "wine mugen.exe -p1 {p1} -p2 {p2} -s {stage}"
launch_cmd = "mugen.exe -p1 {p1} -p2 {p2} -s {stage}"
char_dir = 'chars'
temp_char_dir = "temp_chars"
grace_time = 5

image_db = {}


class MUGENGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
        self.air_queue = []

    def update(self, ticks):
        new_queue = []
        for (parent, air) in self.air_queue:
            air[4] = air[4] - 1
            if air[4] > 0:
                new_queue.append((parent, air))
            else:
                parent.apply_air(air)

        self.air_queue = new_queue


class MUGENSprite(pygame.sprite.Sprite):
    def update_image(self, image):
        self.image = image
        pos = self.rect.topleft
        self.rect = pygame.Rect(pos, image.size)

    def apply_air(self, air):
        g, i, x, y, ttl = air[:5]
        self.update_image(image_db[(g, i)])
        self.rect.move_ip((x, y))


class VersusScreen(object):
    pass


# older SFF v1.01
def grab_image(filename, groupno, imageno):
    fh = open(filename, 'rb')

    header = sff.sff_header1.parse(fh.read(512))
    fh.seek(header.next_subfile)
    subfile = sff.sff_subfile_header.parse(fh.read(32))

    while subfile:
        try:
            fh.seek(subfile.next_subfile)
            subfile = sff.sff_subfile_header.parse(fh.read(32))
        except:
            break

        if subfile.groupno == groupno and subfile.imageno == imageno:
            return pygame.image.load((StringIO(fh.read(subfile.length))))

    return None


# decode rle8 data
def decode(data):
    def _bin(x, width):
        return ''.join(str((x >> i) & 1) for i in range(width - 1, -1, -1))

    image = ""
    data.reverse()
    while data:
        byte = data.pop()
        if (byte & 0xC0) == 0x40:
            color = chr(data.pop())
            image += (color * (byte & 0x3F))
        else:
            image += chr(byte)

    return image


palettes = {}


def load_palette(data, palette_index):
    palette = data.palettes.read()[palette_index]
    return palette.palette_data.read()


# new SFF v2.00
def load_image(data, groupno, itemno):
    for sprite in data.sprites.read():
        if sprite.groupno == groupno and sprite.itemno == itemno:
            pixels = decode(sprite.compressed_image.value.pixels)
            size = (sprite.width, sprite.height)
            palette = load_palette(data, sprite.palette_index)
            surface = pygame.image.fromstring(pixels, size, "P")
            surface.set_palette(palette)
            image_db[(groupno, itemno)] = surface
            return


air_regex = re.compile("(),(),(),(),()[HV],[AS]", re.I)

"""
Construct??

DecNumber('groupno'),
DecNumber('imageno'),
DecNumber('xaxis'),
DecNumber('yaxis'),
DecNumber('ttl'),
"""

import configparser

MUGENConfig = configparser.ConfigParser


def drawVS(surface):
    mugen_cfg = MUGENConfig()
    mugen_cfg.read(os.path.join('data', 'mugen.cfg'))
    motif_path = mugen_cfg.get('Options', 'motif')

    motif_cfg = MUGENConfig()
    motif_cfg.read(motif_path)

    spr_filename = motif_cfg.get('Files', 'spr')
    filename = os.path.join(os.path.dirname(motif_path), spr_filename)

    spr_data = sff.sff2_file.parse_stream(open(filename, 'rb'))

    sections = []
    for s in motif_cfg.sections:
        try:
            if s.name[:8] == 'VersusBG':
                sections.append(s)
        except:
            pass

    for section in sections:
        try:
            s_type = section.type
        except AttributeError:
            continue

        if s_type == 'normal':
            start = section.start.split(',')
            start = [int(i) for i in start]
            g, i = [int(i) for i in section.spriteno.split(',')]
            load_image(spr_data, g, i)
            surface.blit(image_db[(g, i)], start)

        elif s_type == 'anim':
            pass


if __name__ == "__main__":
    start_time = None

    os.chdir(base_dir)

    group = MUGENGroup()


    def show_versus(display_time):
        pygame.display.init()
        screen = pygame.display.set_mode((1200, 800))
        pygame.mouse.set_visible(0)

        drawVS(screen)

        start_time = time.time()
        clock = pygame.time.Clock()
        while time.time() < start_time + display_time:
            group.draw(screen)
            pygame.event.pump()
            pygame.display.flip()
            group.update(1)
            clock.tick(60)

        pygame.mouse.set_visible(1)
        # pygame.display.quit()


    def copy(path, destination):
        new_path = os.path.join(destination, os.path.basename(path))
        rel_path = os.path.relpath(path, destination)

        try:
            shutil.copytree(path, new_path)
        except OSError as e:
            # error 17 means that the folder exists.  just silently ignore it
            if e.errno == 17:
                pass

        return new_path


    def test_illegal_name(char):
        if char.name.find(" ") > -1:
            return True
        return False


    def launch_mugen(match):
        start_time = time.time()
        return subprocess.call(launch_cmd.format(**match).split())


    # get all of our characters (takes a while)
    print("finding characters...")
    characters = list(get_characters(char_dir))

    redo = True
    players = None
    while 1:
        players = random.sample(characters, 2)
        if any(map(test_illegal_name, players)):
            continue
        else:
            break

    stage = 'stage0'

    copies = []
    for char in players:
        new_dir = copy(os.path.dirname(char.path), temp_char_dir)
        new_path = os.path.join(new_dir, os.path.basename(char.path))
        copies.append(Character(char.name, new_path))

    match = {'p1': copies[0].path,
             'p2': copies[1].path,
             'stage': stage}

    show_versus(5)

    # start_time = time.time()
    # if start_time + grace_time > time.time():
    #    launch_mugen(match)

    # clean up the temporary characters
    [shutil.rmtree(os.path.dirname(i.path)) for i in copies]
