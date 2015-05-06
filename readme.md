MUGEN Tools for Python
======================

Small project that adds some python code for performing mugen related tasks.


Features
--------

* character checker; see below
* character file checker: make sure all sff, air, mp3, etc are available
* character migration: old winmugen => mugen 1.0/1.1
* select.def creator with template support
* SSF reading and image extraction
* frontend with random matchups, requires pygame


Character Checker
-----------------

Automated checking of mugen characters.

Given a working mugen folder, create matchups between characters in the
chars folder.  if mugen crashes instantly, then each character is tested
against a known working char, 'kfm'.  If the matchup doesn't crash, then
the characters' folders are moved (not copied) to another folder.

The net result of this process is that the chars folder will only contain
characters that do not work with your version of mugen, and another folder
will contain all the working folders.

By default, 8 pairs of characters are tested at one time.  This means that
your computer will be running at most, 8 copies of mugen.  You will need
a computer that is capable of handling all the concurrent mugen processes,
or you can lower or raise the number.


Rationale
---------

I like python and some of the tools available in the community are just not
my style.


Python Support
--------------

This package was developed and tested with:
python 3.4.3, windows 8.1, pygame 1.9.2


all files in this repository are public domain, except for parse.py

leif theden, 2012-2015
