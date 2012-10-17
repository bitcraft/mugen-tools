#!/usr/bin/env python

"""
SSF Extract for python

This utility will read a Elecbyte SFF file (version 1.01) and write the
portrait to the current folder.

** this is just a test of the library, not meant to be a real tool, yet.


leif.theden@gmail.com
public domain
"""

from PIL import Image
from StringIO import StringIO
from libmugen import sff

filename = 'XP.sff'

header = sff.sff1_header.parse(fh.read())

while subfile:
    try:
        fh.seek(subfile.next_subfile)
        subfile = sff.sff1_subfile_header.parse(fh.read(32))
    except:
        break

    if subfile.groupno == 9000 and subfile.imageno == 0:
        image = Image.open(StringIO(fh.read(subfile.length)))
        image.save("portrait.png") 
