"""
leif theden, 2012 - 2015
public domain
"""
import re
import os
import glob
import shutil
import chardet
from os.path import dirname, join, exists, normpath

from libmugen import Character, Stage
from libmugen.parse import MugenParser

filename_regex = re.compile(
    r'(\w*(\\|\/))*\w+?\.(cmd|cns|sff|air|snd|act|def|mp3|ogg)$', re.I)
name_regex = re.compile('name\s*?=\s*?\"(.*?)\"', re.I)


def open_guess_encoding(filename):
    with open(filename, 'rb') as fp:
        guess = chardet.detect(fp.read())

    return guess['encoding']


def parse_def(filename):
    """Get some info from a def
    Currently, only name paring is implemented
    """
    info = dict()
    encoding = open_guess_encoding(filename)
    # errors="surrogateescape" is used to ignore unknown characters if the
    # encoding is incorrectly guessed.  Shift-JIS seems to give many errors
    with open(filename, encoding=encoding, errors='surrogateescape') as fp:
        try:
            for line in fp:
                match = name_regex.match(line)
                if match:
                    name = match.groups()[0]
                    if name != "":
                        info['name'] = name
                        break

        except UnicodeDecodeError:
            print('unicode error: ', filename)

    return info


def gather_required_files(filename):
    """Search a character.def and return all the files needed to use it
    This is useful to remove unused assets that are shipped with a character

    This is a recursive function, and will search more def files if found

    There will likely be some false positives, especially with stage defs,
    so check to make sure they exist before moving them, etc

    TODO: directory structure?
    """
    # open the file, while ignoring encoding errors (usually comments)
    encoding = open_guess_encoding(filename)
    with open(filename, encoding=encoding, errors='surrogateescape') as fp:
        config = MugenParser()
        config.read_string(fp.read())

    # go through each section and store any options that look like filenames
    required = set()
    for section in config.sections():
        section = config[section]
        options = set(find_asset(normpath(v)) for k, v in section.items()
                      if filename_regex.match(v))
        required.update(options)

    # check other def files, then search them and add the results
    root = dirname(filename)
    for child_file in required.copy():
        name, ext = os.path.splitext(child_file)
        if ext.lower() == '.def':
            path = join(root, child_file)
            required.update(gather_required_files(path))

    # TODO: this is not implemented
    # mugen does checking against many paths, so we need
    # to emulate that the if we want to check for missing files
    # finally, go through the potential files and verify they exist
    # for child_file in required.copy():
    #     path = join(root, child_file)
    #     if not os.path.exists(path):
    #         required.remove(child_file)

    return required


def move_character(character, dest):
    """Move a character folder

    Its totally ok to stuff a few character variants in a single
    character folder, and use different .def's for each char, and
    its somewhat common.  Yet, when testing and moving, we want to
    isolate each char def.

    TODO: handle case when char already exists

    :param character:
    :param dest:
    :return:
    """
    character_path = dirname(character.path)
    shutil.move(character_path, dest)


def verify_name_matches_def(name, path):
    folder, filename = os.path.split(path)
    assumed_name, ext = os.path.splitext(filename)
    return name == assumed_name


def verify_name(name):
    """Verify that a short name is valid

    :param name: string
    :return: boolean
    """
    try:
        if name.index(' '):
            return False
    except ValueError:
        return True


def fix_name(name):
    if verify_name(name):
        return name
    else:
        return None


def find_asset(path, root=None):
    """emulate the awful, awful behavior of mugen file finding
    """
    if root is None:
        root = 'z:\\Leif\\Dropbox\\mugen\\testing-build\\'

    check = ('', 'data', 'stages', 'sound')
    for folder in (join(root, i) for i in check):
        candidate = join(folder, path)
        if exists(candidate):
            return candidate

    return "<NO PATH TO FILE>"


def get_stages(root):
    path = root + '/*.def'
    for filename in glob.iglob(path):
        short_name = os.path.split(os.path.splitext(filename)[0])[1]
        if not verify_name(short_name):
            continue
        yield Stage(None, short_name, filename)


def move_stage(stage, dest):
    """move a stage, and any files it references
    will return true if successful, false if it failed

    TODO: handle case when stage already exists
    TODO: handle properly moving assets with relative filename
    """
    files = gather_required_files(stage.path)
    files.add(stage.path)

    if all(exists(fn) for fn in files):
        for fn in files:
            shutil.move(fn, dest)
        return True

    return False


def get_characters(root):
    """Walk through a folder and return generator object of characters
    """
    def glob_defs(filenames):
        return [i for i in filenames if i[-3:].lower() == "def"]

    # glob the characters and group by subdirectory
    def glob_chars(path):
        pushback = []

        paths = [join(path, i) for i in os.listdir(path)]
        dirnames = [i for i in paths if os.path.isdir(i)]
        dirnames.reverse()

        while dirnames:
            path = dirnames.pop()
            defs = glob_defs(os.listdir(path))
            paths = [join(path, i) for i in os.listdir(path)]
            subdirs = [i for i in paths if os.path.isdir(i)]

            if subdirs:
                pushback.append(path)

            while defs:
                yield join(path, defs.pop())

        while pushback:
            path = pushback.pop()
            for char in glob_chars(path):
                yield char

    for path in glob_chars(root):
        d = parse_def(path)
        name = fix_name(os.path.split(dirname(path))[1])
        if not verify_name_matches_def(name, path):
            name = None
        try:
            yield Character(d['name'], name, path)
        except KeyError:
            pass
