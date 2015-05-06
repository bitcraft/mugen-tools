"""
leif theden, 2012 - 2015
public domain
"""
import collections
import os
from os.path import normpath, relpath
import subprocess
from apps.char_check import match_timeout


Character = collections.namedtuple('Character', 'name short_name path')
Stage = collections.namedtuple('Stage', 'name short_name path')


class Match:
    mugen_folder = 'z:\\Leif\\Dropbox\\mugen\\testing-build\\'
    mugen_exe = 'winmugen.exe'
    rounds = 1
    match_timeout = match_timeout
    default_character = None

    def __init__(self, player1=None, player2=None,
                 player1_ai=True, player2_ai=True, stage=None):

        self.generate_default_character()
        self.player1 = player1 if player1 else self.default_character
        self.player2 = player2 if player2 else self.default_character
        self.player1_ai = player1_ai
        self.player2_ai = player2_ai
        self.stage = stage

    def generate_default_character(self):
        if self.default_character is None:
            path = self.mugen_folder + 'kfm\\kfm.def'
            self.default_character = Character('Kung Fu Man', 'kfm', path)

    def fix_path(self, path):
        """mugen expects character names to be relative to mugen folder
        """
        return normpath(relpath(path, self.mugen_folder))

    def run_subprocess(self):
        args = self.generate_command_args()
        args.insert(0, self.mugen_exe)
        os.chdir(self.mugen_folder)
        try:
            return subprocess.call(args, timeout=self.match_timeout)
        except subprocess.TimeoutExpired:
            return -1

    def generate_command_args(self):
        p1_path = self.fix_path(self.player1.path)
        p2_path = self.fix_path(self.player2.path)
        p1_ai = '1' if self.player1_ai else '0'
        p2_ai = '1' if self.player2_ai else '0'
        stage = self.stage.short_name if self.stage else 'stage0'
        args = ['-p1', p1_path, '-p2', p2_path,
                '-p1.ai', p1_ai, '-p2.ai', p2_ai,
                '-rounds', str(self.rounds),
                '-stage', stage]
        return args
