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
import os
import asyncio
import logging
from collections import defaultdict
from os.path import dirname, join, basename

from libmugen.path import async_exists, gather_required_files, is_path, scantree
from libmugen.character import get_config, move_character, new_character
from libmugen.stage import move_stage, new_stage
from libmugen.config import guess_kind, is_mugen_config


class MugenRoot:
    """ Directory context for a MUGEN installation
    """
    extended_asset_folders = 'data', 'stages', 'sound'
    mugen_assets = '.air', '.cmd', '.cns', '.sff', '.snd', '.mp3', '.act'

    logger = logging.getLogger('MugenRoot')

    def __init__(self, root):
        self._stages = set()
        self._characters = set()
        self.root = root
        self.files_in_context = defaultdict(set)
        self.extended_asset_cache = dict()

        # config
        self.factories = {
            'character': self.process_character,
            'stage': self.process_stage,
            'scenedef': None
        }

    @property
    def characters(self):
        return self._characters

    @property
    def stages(self):
        return self._stages

    async def scan_root(self):
        """ Find what characters and stages are available

        :return:
        """
        self.logger.debug('starting scan of mugen folder...')
        tasks = set()

        # first do a deep scan of all the files in the mugen root
        # i'm not sure, but it seems that mugen doesn't care where
        # certain files are, as long as they exist somewhere
        # for entry in scantree(self.root):
        #     path = entry.path
        #     ext = entry.path[-4:]
        #     if ext in self.mugen_assets:
        #         filename = basename(path)
        #         if filename in self.files_in_context:
        #             pass
        #         self.files_in_context[filename].add(path)

        path = os.path.join(self.root, 'chars')
        for entry in filter(is_mugen_config, scantree(path)):
            config = get_config(entry.path)
            kind = guess_kind(config)
            factory = self.factories.get(kind)
            if factory is None:
                # print(entry.path, factory)
                # print(config.sections())
                continue

            root = None # TODO THIS
            task = factory(config, root, entry.path)
            tasks.add(task)

        # wait for all of the scans to finish
        await asyncio.gather(*tasks)

    async def process_character(self, config, root, path):
        character = new_character(config, root, path)
        await self.register_character(character)

    async def process_stage(self, config, path):
        stage = new_stage(config, path)
        await self.register_stage(stage)

    async def register_character(self, character):
        if await self.verify_character(character):
            self._characters.add(character)
        else:
            pass

    async def verify_character(self, character):
        config = get_config(character.path)
        try:
            await gather_required_files(self, character.path, config)
            character.status = "good"
            return True
        except FileNotFoundError:
            character.status = "broken"
            return False

    async def register_stage(self, stage):
        return

    def migrate_root(self, root):
        """ Move this instance of mugen to a new working folder

        This is useful for isolating buggy characters and stages

        :param root:
        :return:
        """
        for char in self.characters:
            move_character(char, root)

        for stage in self.stages:
            move_stage(stage, root)

    async def find_asset(self, root, filename):
        """ Emulate the awful, awful behavior of mugen file finding

        Here is what I have determined so far:
        * paths can be relative to the "character root"; "chars/kfm"
        * paths can be found in other main places; "stages, data, sound"
        * when defs are found in high level than "character root", don't load

        :type root: string
        :type filename: string
        """
        # search the obvious place first
        # the filename is likely to be relative to the root of
        # the actual config file.
        candidate = join(root, filename)
        if await async_exists(candidate):
            return candidate

        # check if the filename/path is relative to the path of the def
        # not found, so check if it is a path or raw filename
        if is_path(filename):
            # it is a path, so check around for it in other places

            # maybe it was an absolute path, (from mugen root?)
            candidate = join(self.root, filename)
            if await async_exists(candidate):
                return candidate

        else:
            # just a filename, so look in the extended folders
            # do an extended search across all content folders
            folders = [join(self.root, i) for i in self.extended_asset_folders]
            for folder in folders:
                candidate = join(folder, filename)

                try:
                    if self.extended_asset_cache[candidate]:
                        return candidate

                except KeyError:
                    exists = await async_exists(candidate)
                    self.extended_asset_cache[candidate] = exists
                    if exists:
                        return candidate

        print('missing', root, filename)
        raise FileNotFoundError
