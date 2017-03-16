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


Mugen select.def file creator with template support.


Features
--------

The script will search through a folder for characters and add them to a
new select.def file.  It will also search through stages and add them as well.

Characters will be grouped inside the select.def file by the subdirectory
they are in.  For example, characters in a "Street Fighter" folder will all
be together.  Headers are written in the file when a new group is started.

Template Support:
    The script can read in an existing select.def and add characters in the
    "randomselect" spots.


Usage
-----

* Copy this file into your MUGEN folder.
* Make a copy of select.def and move it to your MUGEN folder
* Rename the copy to "template.def"
* Run mkselectdef.py

mkselectdef.py will scan your chars folder and add any character it finds.
A new select.def file will be created in your MUGEN folder.

*** NOTE: duplicates are not checked ***


Rationale
---------

I have used this script to create massive screenpacks and to organize 42
gigs of mugen characters.  Existing tools were too complex or buggy.


Templates
---------

A "template" is simply a select.def file that this script will use to create
a new copy that includes new characters.

:: The template must be named "template.def"

By default, the script will replace any lines that begin with "randomselect"
with a new line that defines a new character.

I have used this template system to quickly add characters to screenpacks that
have complex layouts.


Limitations
-----------

This script does not check for duplicates and is not aware of any extra options
that may be needed for the screen, such as 'order', 'music', or 'includestage'.
You can add options below


Customization
-------------

This script includes a few variables that you may modify.  Look under
"OPTIONS" below.


Python Support
--------------

This script was developed and tested with python 3.4.3 on windows 8.1.


leif theden, 2012 - 2015
public domain
"""
import re
from os.path import relpath

from libmugen.character import gather_characters
from libmugen.stage import gather_stages

# =============================================================================
#  OPTIONS

# modify this line to change how characters are added to template
character_line = "{}, random, order=1"

# if set, then characters will be added even if there is not enough room.
force_extra_characters = True

# name of mugen folders
char_dir = "chars"
data_dir = "data"
music_dir = "sound"
stage_dir = "stages"

# this determines what is written to select.def to make space empty
empty_space = '-'

#
# =============================================================================

debugmsg_overfilled = ";below are characters that will not fit in the motif"
characters_header = "[characters]"
stages_header = "[extrastages]"

header_regex = re.compile(r"\[ *(?P<header>[^]]+?) *\]")
name_regex = re.compile("name\s*?=\s*?\"(.*?)\"", re.I)
strip_regex = re.compile('[\W_]+')
basename_regex = re.compile(char_dir)


def write_stages(fp, stages_path):
    print("{0}".format(stages_header), file=fp)
    for stage in gather_stages(stages_path):
        path = stage.path
        print("{0}".format(path), file=fp)


def write_character(fp, character):
    path = relpath(character.path, char_dir)
    print(character_line.format(path), file=fp)


def write_empty_space(fp):
    print(empty_space, file=fp)


def guess_character_space(line):
    return len(line) > 1


if __name__ == "__main__":
    import os
    from os.path import join

    root = 'z:\\Leif\\Dropbox\\mugen\\testing-build\\'
    os.chdir(root)

    new_select = open(join(root, 'data', 'select.def'), 'w')
    characters = gather_characters(char_dir)
    current_section = None
    exhausted_characters = False
    written_characters = False
    skip_section = False

    # fill in the characters
    with open(join(root, 'data', 'template.def')) as fp:
        for line in fp:
            line = line.strip()

            match = header_regex.match(line)
            if match:
                skip_section = False
                header = match.group('header').lower()
                current_section = '[' + header + ']'

            elif skip_section:
                continue

            if current_section == characters_header:

                if not written_characters:
                    written_characters = True
                    print(characters_header, file=new_select)

                if guess_character_space(line):
                    try:
                        character = next(characters)
                        write_character(new_select, character)
                    except StopIteration:
                        exhausted_characters = True
                        current_section = None
                else:
                    write_empty_space(new_select)

                continue

            elif written_characters and not exhausted_characters:
                exhausted_characters = True
                for character in characters:
                    write_character(new_select, character)

            if current_section == stages_header:
                write_stages(new_select, stage_dir)
                skip_section = True

            else:
                print(line, file=new_select)
