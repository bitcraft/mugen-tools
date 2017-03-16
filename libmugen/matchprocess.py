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
from __future__ import print_function

import os
import time
import subprocess
from os.path import join, normpath, relpath

from libmugen import match_timeout
from libmugen.win32 import list_windows, user32


class MatchProcess:
    match_timeout = match_timeout
    rounds = 1
    default_character = None
    default_stage = None

    def __init__(self, root, player1, player2, stage, player1_ai=True, player2_ai=True,
                 executable='winmugen.exe'):
        self.root = root
        self.executable = executable
        self.stage = stage
        self.player1 = player1
        self.player2 = player2
        self.player1_ai = '1' if player1_ai else '0'
        self.player2_ai = '1' if player2_ai else '0'
        self.process = None
        self.returncode = None

    def fix_path(self, path):
        """ mugen expects character names to be relative to mugen folder
        """
        return normpath(relpath(path, self.root))

    def start_process(self):
        """ Start then run

        :return:
        """
        args = self.generate_command_args()
        args.insert(0, self.executable)
        os.chdir(self.root)
        self.process = subprocess.Popen(args)
        self.returncode = None

    def wait_until_ready(self):
        while self.returncode is None:
            self.returncode = self.process.poll()

            try:
                pdict = {i.pid: i for i in list_windows()}
                handle = pdict[self.process.pid].handle
                user32.SetForegroundWindow(handle)
                top = user32.GetForegroundWindow()
                if handle == top:
                    break

            except KeyError:
                pass

            time.sleep(.5)

    def run_subprocess(self):
        """
        Best run this in a thread to avoid blocking everything

        :return:
        """
        while self.returncode is None:
            self.returncode = self.process.poll()
            time.sleep(.075)

    def generate_command_args(self):
        p1_path = self.fix_path(self.player1.path)
        p2_path = self.fix_path(self.player2.path)
        stage = self.stage.short_name
        args = ['-p1', p1_path,
                '-p2', p2_path,
                '-p1.ai', self.player1_ai,
                '-p2.ai', self.player2_ai,
                '-rounds', str(self.rounds),
                '-stage', stage]
        return args
