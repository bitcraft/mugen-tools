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
import shutil
from os.path import basename, dirname

from libmugen.path import get_config


class Character:
    def __init__(self, name, displayname, shortname, root, path):
        """

        :param name:
        :param displayname:
        :param shortname:
        :param root: The main folder where assets are stored
        :param path: The complete path to the config file

        The root parameter dirname may not match the path parameter dirname.
        """
        self.name = name
        self.displayname = displayname
        self.shortname = shortname
        self.root = root
        self.path = path
        self.status = None


def new_character(config, root, path):
    """ Get some info from a def

    :type config: libmugen.parse.MugenParser
    """
    get = config['info'].get
    char = Character(
        get('name'),
        get('displayname'),
        basename(path)[:-4],
        root,
        path)
    return char


def load_character(root, path):
    """ Skip check if is character

    :param path:
    :return:
    """
    config = get_config(path)
    return new_character(config, root, path)


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
