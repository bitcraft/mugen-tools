#!/usr/bin/env python

"""
Mugen select.def file creator with template support.

Templates
---------

A "template" is simply a select.def file that this script will use to create
a new copy that includes new characters.

By default, the script will replace any lines that begin with "randomselect"
with a new line that defines a new character.

I have used this template system to quickly add characters to screenpacks that
have complex layouts.


Geometry (Advanced)
-------------------

The script is capable of creating new select.def files without a template.
By defining a geometry, the script will be able to create a layout that doesn't
have overlapping tiles or sprites.


Python Support
--------------

This script was developed and tested with python 2.7.3 on OS X.



leif theden, 2012
"""

import os, re, glob, collections, argparse
import pygame


# give the script friendly argument procesing
parser = argparse.ArgumentParser()

parser.add_argument('-o', metavar='output',
                    help='name of the config file to be written',
                    type=str,
                    default='select.def')

parser.add_argument('-t', metavar='template',
                    help='name of template file',
                    type=str,
                    default='template.def')

parser.add_argument('-f',
                    help='force characters to be added even if not enough space',
                    action='store_true',
                    default=False)

parser.add_argument('characters', metavar='char', type=str, nargs='+',
                    help='name of folder to scan for characters')


settings = parser.parse_args()

layout = True

rows = 70
columns = 53
spacing = 1

layout_rects = []
layout_rects.append(pygame.Rect(0,0,21,21))
layout_rects.append(pygame.Rect(30,20,21,21))


# modify this line to change how characters are added to template
character_line = "{0},,order=,music=,includestage=0;{1}\r\n"
#character_line = "{0},,includestage=0;{1}\r\n"


# if set, then characters will be added to the screenpack even if there is
# not enough room.
force_extra_characters = True

debugmsg_overfilled = ";below are extra characters that will not fit in screenpack"

char_dir = "chars"
data_dir = "data"
music_dir = "sound"
stage_dir = "stages"

characters_header = "[Characters]"
stages_header = "[ExtraStages]"

name_regex = re.compile("name\s*=.*?\"(.*?)\"", re.I)
strip_regex = re.compile('[\W_]+')
Character = collections.namedtuple('Character', ['name', 'chardef', 'path'])


def check_placement(pos):
    rect = pygame.Rect(pos, (1, 1))
    if rect.collidelist(layout_rects) >= 0:
        return False
    else:
        return True

def glob_chars(path):
    for name in os.listdir(path):
        new_path = os.path.join(path, name)
        if os.path.isdir(new_path):
            yield new_path

def glob_defs(path):
    defs = glob.glob("{0}/*def".format(path))
    return defs

def parse_def(filename):
    d = {}
    try:
        with open(filename) as fh:
            line = fh.readline()
            while not line == "":
                match = name_regex.match(line)
                if match:
                    name = match.groups()[0]
                    if name != "":
                        d['name'] = name

                line = fh.readline()

        return d

    except:
        return {}


def write_character(fh, character):
    name, chardef, path = character
    name = strip_regex.sub('', name)
    basename = os.path.basename(path)
    fh.write(character_line.format(basename, basename))


def get_characters(path):
    for char_path in glob_chars(path):
        for char_def in glob_defs(char_path):
            d = parse_def(char_def)
            try:
                yield Character(d['name'], char_def, char_path)
            except KeyError:
                pass
    
x = 0
y = 0
count = 0

def write_layout(fh, character):
    global x
    global y
    global count

    # we have a new character, figure out how to add it
    if layout:
        ok = check_placement((x, y))
        if ok:
            x += 1
            if x >= columns-1:
                y += 1
                x = 0
                print "."
            else:
                print ".",

        else:
            while not ok:
                x += 1
                if x >= columns-1:
                    y += 1
                    x = 0
                    print "X"
                else:
                    print "X",

                ok = check_placement((x, y))
                fh.write("blank\r\n")

        write_character(fh, character)

    elif line[:12] == "randomselect":
        write_character(fh, next(characters))

    count += 1

if __name__ == "__main__":
    new_config = open("select.def", "w")
    new_config.write("{0}\r\n".format(characters_header))

    characters = get_characters(char_dir)

    write_layout(new_config, Character('randomselect', '', 'randomselect'))


    # fill in the the characters
    with open("template.def") as fh:
        line = fh.readline()
        has_characters = True

        while not line == "":
            line = line.strip()

            # write the stages
            if line == stages_header:
                if force_extra_characters:
                    new_config.write("{0}\r\n".format(debugmsg_overfilled))
                    for character in characters:
                        write_layout(new_config, character)

                    new_config.write("\r\n")

                new_config.write("{0}\r\n".format(stages_header))
                for stage_def in glob_defs(stage_dir):
                    d = parse_def(stage_def)
                    try:
                        new_config.write("{0};{1}\r\n".format(stage_def, d['name']))
                    except KeyError:
                        pass

                # skip to the next section
                line = fh.readline()
                while not line == "":
                    line = fh.readline()
                    if line[0] == "[":
                        break

                continue

            # get the next template character to add to the select.dat file
            try:
                character = next(characters)
            except StopIteration:
                has_characters = False
                new_config.write("{0}\r\n".format(line))
            else:
                write_layout(new_config, character)


            line = fh.readline()

print
print count
