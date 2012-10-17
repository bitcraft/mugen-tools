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

from construct import Struct, ULInt8, ULInt16, ULInt32, String, Padding, \
Adapter, Sequence, Byte, Enum, OnDemandPointer, Array, Rename, Switch, Pass, \
Pointer, String, Value, OnDemand, GreedyRange

from StringIO import StringIO


class RunLengthAdapter(Adapter):
    def _encode(self, obj, context):
        return len(obj), obj[0]
    def _decode(self, obj, context):
        length, value = obj
        return [value] * length

rle8pixel = RunLengthAdapter(
    Sequence("rle8pixel",
        Byte("length"),
        Byte("value")
    )
)


sff1_subfile_header = Struct('sff subfile header 1.01',
    ULInt32('next_subfile'),
    ULInt32('length'),
    ULInt16('axisx'),
    ULInt16('axisy'),
    ULInt16('groupno'),
    ULInt16('imageno'),
    ULInt16('index'),
    ULInt8('palette'),
)


sff1_subfile = Struct('sff1 subfile 1.01',
    sff1_subfile_header,
    Padding(14),
    OnDemand(Array(lambda ctx: ctx.length, Byte('data')))
)


sff1_file = Struct('ssf header 1.01',
    String('signature', 12),
    ULInt8('verhi'),
    ULInt8('verlo1'),
    ULInt8('verlo2'),
    ULInt8('verlo3'),
    ULInt32('group_total'),
    ULInt32('image_total'),
    ULInt32('next_subfile'),
    ULInt32('subfile_header_length'),
    ULInt8('palette type'),
    ULInt8('reserved0'),
    ULInt8('reserved1'),
    ULInt8('reserved2'),
    Padding(476),

    OnDemandPointer(lambda ctx: ctx.next_subfile,
        GreedyRange(sff1_subfile),
    )
)


sff2_sprite = Struct('sprite 2.00',
    ULInt16('groupno'),
    ULInt16('itemno'),
    ULInt16('width'),
    ULInt16('height'),
    ULInt16('axisx'),
    ULInt16('axisy'),
    ULInt16('index'),
    Enum(ULInt8('format'),
        raw = 0,
        invalid = 1,
        rle8 = 2,
        rle5 = 3,
        lz5 = 4,
    ),
    ULInt8('colordepth'),
    ULInt32('data_offset'),
    ULInt32('data_length'),
    ULInt16('palette_index'),
    ULInt16('flags'),

    # for whatever reason, the offset specified in this node is relative
    # to a position that is defined in the sff file heading.  that value
    # can either be ldata_offset of tdata_offset, depending on the flags here
    Switch('real_offset', lambda ctx: ctx.flags,
        {  
            0: Value('real_offset', lambda ctx: ctx._.ldata_offset)
        },
        Value('real_offset', lambda ctx: ctx._.tdata_offset)
    ),

    # pixel data
    OnDemandPointer(lambda ctx: ctx.real_offset + ctx.data_offset,
        Struct('compressed_image',
            ULInt32('uncompressed_size'),
            Switch("pixels", lambda ctx: ctx._.format,
                {
                    'invalid' : Pass,
                    'rle8': Array(lambda ctx: ctx._.data_length - 4, ULInt8('byte'))
                },
                default = Pass
            )
        )
    )
)




sff2_palette = Struct('palette header 2.00',
    ULInt16('groupno'),
    ULInt16('itemno'),
    ULInt16('numcols'),
    ULInt16('index'),
    ULInt32('data_offset'),
    ULInt32('data_length'),

    Rename('palette_data',
        OnDemandPointer(lambda ctx: ctx._.ldata_offset + ctx.data_offset,
            Array(lambda ctx: ctx.data_length,
                Sequence('chunk',
                    ULInt8('Red'),
                    ULInt8('Green'),
                    ULInt8('Blue'),
                    Padding(1)
                )
            )
        )
    )
)


sff2_file = Struct('ssf 2.00',
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
    Padding(436),

    Rename('palettes',
        OnDemandPointer(lambda ctx: ctx.palette_offset,
            Array(lambda ctx: ctx.palette_total, sff2_palette))
    ),

    Rename('sprites',
        OnDemandPointer(lambda ctx: ctx.sprite_offset,
            Array(lambda ctx: ctx.sprite_total, sff2_sprite)),
    )
)

