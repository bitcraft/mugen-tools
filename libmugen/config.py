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
import re

from libmugen.parse import MugenParser

match_timeout = 15
strip0_regex = re.compile(';.*?\n')
strip1_regex = re.compile(':.*\n')
strip2_regex = re.compile('[;:].*\n')


def get_config(path):
    # open the file, while ignoring encoding errors (usually comments)
    # errors="surrogateescape" is used to ignore unknown characters if the
    # encoding is incorrectly guessed.  Shift-JIS seems to give many errors
    encoding = 'ascii'
    with open(path, encoding=encoding, errors='surrogateescape') as fp:
        data = fp.read()

    config = MugenParser()
    config.read_string(data)

    return config


def strip_comments(data):
    # comments start with ; so strip them
    # for whatever S@#)$*! reason, : comments are also allowed
    return data
    # return re.sub(strip2_regex, "", data)


def is_mugen_config(entry):
    return entry.name.endswith('.def') and entry.is_file()


def guess_kind(config):
    """ Attempt to determine if file is a Character, Stage, or Scenedef.

    These share the same file extension and structure, and are
    often mixed in the same folder, so deep testing is needed to
    determine what they actually are used for.

    :type config: libmugen.parse.MugenParser
    :return: str
    """
    if config.has_section('info'):
        return 'character'
    elif config.has_section('scenedef'):
        return 'scenedef'
    elif config.has_section('StageInfo'):
        return 'stage'
    else:
        return None
