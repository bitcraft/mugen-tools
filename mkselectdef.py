#!/usr/bin/env python

"""
Mugen select.def file creator with template support.


Features
--------

The script will search through a folder for characters and add them to a
new select.def file.  It will also search through stages and add them as well.

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

I have used this script to create massive screenpacks and to organize 6 gigs of
mugen characters.  Existing tools were too complex or buggy. 


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


Customization
-------------

This script includes a few variables that you may modify.  Look under
"OPTIONS" below.


Python Support
--------------

This script was developed and tested with python 2.7.3 on OS X.



leif theden, 2012
public domain
"""

import os, re, glob, collections


# =============================================================================
#  OPTIONS

# modify this line to change how characters are added to template
character_line = "{0},,order=,music=,includestage=0;{1}\r\n"

# if set, then characters will be added even if there is not enough room.
force_extra_characters = True

# name of mugen folders
char_dir = "chars"
data_dir = "data"
music_dir = "sound"
stage_dir = "stages"

#
# =============================================================================

debugmsg_overfilled = ";below are extra characters that will not fit in screenpack"
characters_header = "[Characters]"
stages_header = "[ExtraStages]"

name_regex = re.compile("name\s*=.*?\"(.*?)\"", re.I)
strip_regex = re.compile('[\W_]+')
Character = collections.namedtuple('Character', ['name', 'chardef', 'path'])

count = 0


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
    global count

    count += 1

    name, chardef, path = character
    name = strip_regex.sub('', name)

    print "Adding character: {0} ({1})".format(name, path)

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



    
if __name__ == "__main__":
    new_config = open("select.def", "w")
    characters = get_characters(char_dir)

    # fill in the characters
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
                        write_character(new_config, character)

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

            # see if we have a open (randomselect) space
            randomselect = False
            try:
                if line[:12].lower() == 'randomselect':
                    randomselect = True                    
            except IndexError:
                pass

            if randomselect:
                # get the next template character to add to the select.dat file
                try:
                    character = next(characters)
                except StopIteration:
                    has_characters = False
                    new_config.write("{0}\r\n".format(line))
                else:
                    write_character(new_config, character)
            else:
                new_config.write("{0}\r\n".format(line))



            line = fh.readline()

print "\nAdded {0} characters.".format(count)
