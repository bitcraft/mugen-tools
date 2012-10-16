#!/usr/bin/env python

"""
SSF Extract for python

This utility will read a Elecbyte SFF file (version 1.01 & 2) and write
all of the images to the current directory.


leif.theden@gmail.com
public domain
"""

from PIL import Image
from StringIO import StringIO
from libmugen import sff

filename = 'dc.sff'

fh = open(filename, 'rb')

header = sff.sff_header1.parse(fh.read(512))
fh.seek(header.next_subfile)
subfile = sff.sff_subfile_header.parse(fh.read(32))

while subfile:
    try:
        fh.seek(subfile.next_subfile)
        subfile = sff.sff_subfile_header.parse(fh.read(32))
    except:
        break

    if subfile.groupno == 9000 and subfile.imageno == 1:
        image = Image.open(StringIO(fh.read(subfile.length)))
        image.save("portrait.png") 
