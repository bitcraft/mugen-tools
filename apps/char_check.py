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

see if a character works for a particular version of mugen

this high-tech, patented process uses advanced algorithms and
proprietary data structures resulting in time and money saved.
here's what it does:
  make list of all characters
  make match with first two characters in list
  if crashes, change player #1 with kfm
  if crashes, quarantine player #1
  if doesn't crash, change player #2 with kfm
  if crashes, discard player #2
  if it doesn't crash, then those two players have a problem
  repeat until no more characters

requires character 'kfm', since it is known to work 100%.
also, runs multiple copies of winmugen at once.
"""
import os
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from os.path import join

from libmugen.character import load_character, move_character
from libmugen.matchprocess import MatchProcess
from libmugen.path import temp_dir_context
from libmugen.stage import load_stage, move_stage
from libmugen.context import MugenRoot

# On Windows, the default event loop is SelectorEventLoop which does not
# support subprocesses. ProactorEventLoop should be used instead.
if os.name == 'nt':
    loop_ = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop_)

max_parallel_matches = multiprocessing.cpu_count() // 2


async def match_in_thread(match):
    """ Run a match to verify game doesn't crash
    :param match: TestMatch
    :return: boolean
    """
    match.start_process()
    match.wait_until_ready()  # blocking
    await loop.run_in_executor(executor, match.run_subprocess)
    if match.returncode == 0:
        return match
    return None


def setup_environment(match, root):
    """ Setup environment for a match

    mugen needs:

    :return:
    """
    move_stage(match.stage, root)
    move_character(match.player1, root)
    move_character(match.player2, root)


def generate_default_character(root):
    char_root = join(root, 'chars', 'kfm')
    path = join(char_root, 'kfm.def')
    return load_character(char_root, path)


def generate_default_stage(root):
    path = join(root, 'stages', 'kfm.def')
    return load_stage(path)


@asyncio.coroutine
def clean_match(player1, player2, stage):
    with temp_dir_context() as temp_dir:
        match = MatchProcess(player1, player2, stage=stage)
        setup_environment(match, temp_dir)
        yield from match_in_thread(match)


def load_characters_lazy(root, player1=None, player2=None, stage=None):
    """ Load some chars and a stage.  Or not.  Whatev.

    :param root:
    :param player1:
    :param player2:
    :param stage:
    :return:
    """
    default_character = generate_default_character(root)
    return {'root': root,
            'player1': player1 if player1 else default_character,
            'player2': player2 if player2 else default_character,
            'stage': stage if stage else generate_default_stage(root)}


async def start_match(root, char):
    kwargs = load_characters_lazy(root, player1=char)
    match = MatchProcess(**kwargs)
    await match_in_thread(match)


async def load_context(root, context_cache="context.cache"):
    """ Load MugenRoot context, using cache if available.

    :rtype: MugenRoot
    """
    import pickle

    try:
        with open(context_cache, "rb") as fp:
            context = pickle.load(fp)

    except FileNotFoundError:
        context = MugenRoot(root)
        await context.scan_root()

        with open(context_cache, "wb") as fp:
            pickle.dump(context, fp)

    return context


async def test_characters():
    """

    :return:
    """
    root = join('z:\\', 'Dropbox', 'mugen', 'testing-build')
    context = await load_context(root)

    sem = asyncio.Semaphore(max_parallel_matches)
    for char in context.characters:
        await sem.acquire()
        task = asyncio.ensure_future(start_match(root, char))
        task.add_done_callback(lambda x: sem.release())


async def test_stages():
    pass


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.NOTSET)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    executor = ThreadPoolExecutor(max_parallel_matches)
    loop.set_default_executor(executor)
    loop.run_until_complete(test_characters())
    # loop.run_until_complete(test_stages())
