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
"""
import asyncio
import contextlib
import os
import re
import tempfile
from os import scandir
from os.path import dirname, exists, normpath
from subprocess import call

import chardet

from libmugen.config import strip_comments
from libmugen.parse import MugenParser

filename_regex = re.compile(
    r'(\w*(\\|\/))*\w+?\.(cmd|cns|sff|air|snd|act|def|mp3|ogg)$', re.I)
name_regex = re.compile('name\s*?=\s*?\"(.*?)\"', re.I)


def notepad_alert(path):
    call(['notepad', path])


def open_folder(path):
    call(['explorer', path])


async def async_exists(path):
    """

    :param path:
    :return:
    """
    # print('check:', path)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, exists, path)


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


def open_guess_encoding(filename):
    with open(filename, 'rb') as fp:
        guess = chardet.detect(fp.read())

    return guess['encoding']


def verify_name_matches_def(name, path):
    folder, filename = os.path.split(path)
    assumed_name, ext = os.path.splitext(filename)
    return name == assumed_name


async def gather_required_files(context, path, config):
    """ Search a character.def and return all the files needed to use it
    This is useful to remove unused assets that are shipped with a character

    This is a recursive function, and will search more def files if found

    There will likely be some false positives, especially with stage defs,
    so check to make sure they exist before moving them, etc

    TODO: directory structure?
    """
    # go through each section and store any options that look like filenames
    required = set()

    for name, section in config.items():
        for value in section.values():
            if filename_regex.match(value):
                # submit
                filename = normpath(value)  # not sure why this is needed
                root = dirname(path)
                await context.find_asset(root, filename)

    # wait for all to be verified

    return required


@contextlib.contextmanager
def temp_dir_context():
    root = tempfile.mkdtemp()
    yield root
    os.unlink(root)


def get_config(path):
    # open the file, while ignoring encoding errors (usually comments)
    # errors="surrogateescape" is used to ignore unknown characters if the
    # encoding is incorrectly guessed.  Shift-JIS seems to give many errors
    encoding = 'ascii'
    with open(path, encoding=encoding, errors='surrogateescape') as fp:
        data = strip_comments(fp.read())

    try:
        config = MugenParser()
        config.read_string(data)
    except:
        print(path)
        print(data)
        raise

    return config


def is_path(text):
    """ Determine if path is a filename or a path

    :param text:
    :return: bool
    """
    if '/' in text or '\\' in text:
        return True
    else:
        return False
