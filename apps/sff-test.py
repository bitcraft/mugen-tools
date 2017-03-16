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
