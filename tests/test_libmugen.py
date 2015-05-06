"""
Tests for libmugen


leif theden, 2012 - 2015
public domain
"""
from unittest import TestCase, skip
from libmugen import Character, Stage
from libmugen.path import gather_required_files
from libmugen.path import get_characters
from libmugen.path import verify_name_matches_def
from libmugen.path import verify_name
from libmugen.path import move_stage


class WalkTest(TestCase):
    mugen_folder = 'z:\\Leif\\Dropbox\\mugen\\testing-build\\'

    @skip
    def test_get_characters(self):
        characters_path = self.mugen_folder + 'chars\\'
        for char in get_characters(characters_path):
            pass

    def test_gather_files(self):
        path = self.mugen_folder + 'chars\\kfm\\kfm.def'
        files = gather_required_files(path)
        print(files)

        path = self.mugen_folder + 'stages\\kfm.def'
        files = gather_required_files(path)
        print(files)

    def test_verify_name(self):
        self.assertTrue(verify_name('good_name'))
        self.assertFalse(verify_name('bad name'))

    def test_verify_name_matches_def(self):
        name = 'kfm'
        good_path = '/chars/kfm/kfm.def'
        bad_path = '/chars/kfm/kfmex.def'
        self.assertTrue(verify_name_matches_def(name, good_path))
        self.assertFalse(verify_name_matches_def(name, bad_path))

    @skip
    def test_move_stage(self):
        path = self.mugen_folder + 'stages\\2003japan.def'
        stage = Stage(None, 'kfm', path)
        move_stage(stage, None)
