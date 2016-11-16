"""
see if a character works for a particular version of mugen

this high-tech, patented process uses advanced algorithms and
proprietary data structures resulting in time and money saved.
here's what it does:
  make list of all characters
  make match with first two characters in list
  if crashes, change player #1 with kfm
  if crashes, discard player #1
  if doesn't crash, change player #2 with kfm
  if crashes, discard player #2
  if it doesn't crash, then those two players have a problem
  repeat until no more characters

requires character 'kfm', since it is known to work 100%.
also, runs multiple copies of winmugen at once.


leif theden, 2012 - 2015
public domain
"""
import asyncio
import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from os.path import join, normpath

from libmugen import Match
from libmugen.path import get_characters, move_character
from libmugen.path import get_stages, move_stage

# On Windows, the default event loop is SelectorEventLoop which does not
# support subprocesses. ProactorEventLoop should be used instead.
if os.name == 'nt':
    loop_ = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop_)


max_parallel_matches = 8


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


@asyncio.coroutine
def match_in_thread(match):
    """Run a match to verify game doesn't crash
    :param match: TestMatch
    :return: boolean
    """
    result = yield from loop.run_in_executor(executor, match.run_subprocess)
    if result == 0:
        return match
    return None


@asyncio.coroutine
def test_characters():
    # sem is used to reduce number of running instances of mugen
    sem = asyncio.Semaphore(max_parallel_matches)
    characters_path = Match.mugen_folder + 'chars\\'
    working_path = normpath(join(characters_path, '..\\working_chars\\'))
    characters_list = get_characters(characters_path)
    running_tasks = set()

    try:
        os.mkdir(working_path)
    except FileExistsError:
        pass

    def done_cb(f):
        sem.release()
        running_tasks.remove(f)
        match = f.result()
        if match:
            move_character(match.player1, working_path)

    for player in list(characters_list):
        yield from sem
        match = Match(player1=player)
        task = asyncio.Task(match_in_thread(match))
        task.add_done_callback(done_cb)
        running_tasks.add(task)

        # this sleep is required to ensure the window gets focus.
        # without gaining focus, the game will never start
        yield from asyncio.sleep(1.5)

    # wait for all all processes to complete or be killed
    yield from asyncio.wait(running_tasks)


@asyncio.coroutine
def test_stages():
    # sem is used to reduce number of running instances of mugen
    semaphore = asyncio.Semaphore(max_parallel_matches)
    stages_path = Match.mugen_folder + 'stages\\'
    working_path = Match.mugen_folder + 'working_stages\\'
    running_tasks = set()

    try:
        os.mkdir(working_path)
    except FileExistsError:
        pass

    def done_cb(f):
        semaphore.release()
        running_tasks.remove(f)
        match = f.result()
        if match:
            move_stage(match.stage, working_path)

    for stage in list(get_stages(stages_path)):
        yield from semaphore
        match = Match(stage=stage)
        task = asyncio.Task(match_in_thread(match))
        task.add_done_callback(done_cb)
        running_tasks.add(task)

        # this sleep is required to ensure the window gets focus.
        # without gaining focus, the game will never start
        yield from asyncio.sleep(.5)

    # wait for all all processes to complete or be killed
    yield from asyncio.wait(running_tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_parallel_matches)
    loop.set_default_executor(executor)
    # loop.run_until_complete(test_characters())
    loop.run_until_complete(test_stages())
