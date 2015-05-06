"""
SSF Extract for python

This utility will read a Elecbyte SFF file (version 1.01) and write the
portrait to the current folder.


leif theden, 2012 - 2015
public domain
"""

from io import StringIO

from PIL import Image
from libmugen import sff


filename = 'sprite.sff'

fh = open(filename, 'rb')

header = sff.sff1_file.parse(fh.read(512))
print(header)

next_subfile = header.next_subfile
while next_subfile:
    fh.seek(next_subfile)
    subfile = sff.sff1_subfile_header.parse(fh.read(32))
    next_subfile = subfile.next_subfile
    try:
        image = Image.open(StringIO(fh.read(subfile.length)))
    except IOError:
        print("ioerror", subfile.groupno, subfile.imageno)
        pass
    else:
        image.save("g{0}-i{1}.png".format(subfile.groupno, subfile.imageno))
