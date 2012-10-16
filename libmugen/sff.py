"""
Python/Pygame MUGEN SSF file support

This collection of classes is able to load and manipulate MUGEN SSF files in
python.  PIL is required for many loading the various formats.

Pygame support may be added in the future.

NOTE:
This library is very simple and is not optimized for use in a real-time
environment.  It exits for very simple uses.  Your mileage may vary.  Parental
discretion advised.  Not available in all areas.


leif theden, 2012
public domain
"""

from construct import Struct, ULInt8, ULInt16, ULInt32, String, Padding
from StringIO import StringIO



sff_header1 = Struct('ssf header 1.01',
    String('signature', 12),
    ULInt8('verhi'),
    ULInt8('verlo1'),
    ULInt8('verlo2'),
    ULInt8('verlo3'),
    ULInt32('group_total'),
    ULInt32('image_total'),
    ULInt32('next_subfile'),
    ULInt32('subfile header length'),
    ULInt8('palette type'),
    ULInt8('reserved0'),
    ULInt8('reserved1'),
    ULInt8('reserved2'),
    Padding(476)
)


sff_subfile_header = Struct('sff subfile header 1.01',
    ULInt32('next_subfile'),
    ULInt32('length'),
    ULInt16('axisx'),
    ULInt16('axisy'),
    ULInt16('groupno'),
    ULInt16('imageno'),
    ULInt16('index'),
    ULInt8('palette'),
)
#    Padding(14),
#    Padding(768) # pcx image data
#)


sff_header2 = Struct('ssf header 2.00',
    String('signature', 12),
    ULInt8('verlo3'),
    ULInt8('verlo2'),
    ULInt8('verlo1'),
    ULInt8('verhi'),
    ULInt32('reserved0'),
    ULInt32('reserved1'),
    ULInt8('compatverlo3'),
    ULInt8('compatverlo2'),
    ULInt8('compatverlo1'),
    ULInt8('compatverhi'),
    ULInt32('reserved2'),
    ULInt32('reserved3'),
    ULInt32('sprite_offset'), 
    ULInt32('sprite_total'),
    ULInt32('palette_offset'),
    ULInt32('palette_total'),
    ULInt32('ldata_offset'), 
    ULInt32('ldata_length'), 
    ULInt32('tdata_offset'), 
    ULInt32('tdata_length'), 
    ULInt32('reserved4'),
    ULInt32('reserved5'),
    Padding(436)
)

sprite_header2 = Struct('sprite header 2.00',
    ULInt16('groupno'),
    ULInt16('itemno'),
    ULInt16('width'),
    ULInt16('height'),
    ULInt16('axisx'),
    ULInt16('axisy'),
    ULInt16('index'),
    ULInt8('format'),
    ULInt8('colordepth'),
    ULInt32('data_offset'),
    ULInt32('data_length'),
    ULInt16('palette_index'),
    ULInt16('flags')
)
    

__all__ = [sff_header1, sff_header2, sff_subfile_header, sprite_header2]
