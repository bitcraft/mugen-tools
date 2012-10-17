#!/usr/bin/env python

"""
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
loaded and crashes are quickly recovered from.  


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


leif theden, 2012
public domain
"""

import pygame
import random, subprocess, os, re, collections, shutil, time
from StringIO import StringIO

from libmugen.config import MUGENConfigParser
from libmugen.utils import get_characters
from libmugen.character import Character
from libmugen import sff

from PIL import Image


launch_cmd = "wine mugen.exe -p1 {p1} -p2 {p2} -s {stage}"
char_dir = "all_chars"
temp_char_dir = "chars"
grace_time = 5



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
        return ''.join(str((x>>i)&1) for i in xrange(width-1,-1,-1))

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
def grab_image(data, groupno, itemno):
    for sprite in data.sprites.read():
        if sprite.groupno == groupno and sprite.itemno == itemno:
            pixels = decode(sprite.compressed_image.value.pixels)
            size = (sprite.width, sprite.height)
            palette = load_palette(data, sprite.palette_index)
            surface = pygame.image.fromstring(pixels, size, "P")
            surface.set_palette(palette)
            return surface

    return None    



def drawVS(surface):
        def get_value(section, name):
            for v in section.values:
                if v.name == name:
                    return v.value

        mugen_cfg = MUGENConfigParser()
        mugen_cfg.read(os.path.join('data', 'mugen.cfg'))
        motif_path = mugen_cfg.get('Options', 'motif')

        motif_cfg = MUGENConfigParser()
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
            if get_value(section, 'type') == 'normal':
                spriteno = get_value(section, 'spriteno')
                start = get_value(section, 'start').split(',')
                start = [int(i) for i in start]
                g, i = spriteno.split(',')
                image = grab_image(spr_data, int(g), int(i))
                if image:
                    surface.blit(image, start)

            elif get_value(section, 'type') == 'anim':
                pass



if __name__ == "__main__":
    start_time = None

    def show_versus(display_time):
        pygame.display.init()
        screen = pygame.display.set_mode((1200, 800))
        pygame.mouse.set_visible(0)

        drawVS(screen)
        pygame.display.flip()

        start_time = time.time()
        while time.time() < start_time + display_time:
            pygame.event.pump()
        pass

        pygame.mouse.set_visible(1)
        #pygame.display.quit()

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
    print "finding characters..."
    characters = list(get_characters(char_dir))

    redo = True
    while redo:
        players = random.sample(characters, 2)
        if any(map(test_illegal_name, players)):
            redo = True
        else:
            redo = False
    
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

    #start_time = time.time()
    #if start_time + grace_time > time.time():
    #    launch_mugen(match) 

    # clean up the temporary characters
    [shutil.rmtree(os.path.dirname(i.path)) for i in copies]

