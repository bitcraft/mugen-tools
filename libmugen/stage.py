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
from genericpath import exists
from os.path import basename

from libmugen.config import get_config
from libmugen.path import gather_required_files


class Stage:
    def __init__(self, name, short_name, path):
        self.name = name
        self.short_name = short_name
        self.path = path


def new_stage(config, path):
    """ Get some info from a def

    :type config: libmugen.parse.MugenParser
    """
    get = config['info'].get
    char = Stage(
        get('name'),
        basename(path)[:-4],
        path)
    return char


def load_stage(path):
    """ eh.

    :param path:
    :return:
    """
    config = get_config(path)
    return new_stage(config, path)


def move_stage(stage, dest):
    """ move a stage, and any files it references
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
