"""
MUGEN character and stage updating script


Features
--------


Usage
-----


Rationale
---------


Templates
---------


Limitations
-----------


Customization
-------------


Python Support
--------------

This script was developed and tested with python 2.7.3 on OS X.


leif theden, 2012 - 2015
public domain
"""

import os

from iniparse.config import Undefined
from iniparse import INIConfig

settings = dict()


# =============================================================================
#  OPTIONS

settings['overwrite'] = True


# =============================================================================
#  MISC REQUIRED THINGS

assert_flags = ('nostandguard', 'nocrouchguard', 'noairguard', 'noautoturn',
                'noshadow', 'nojugglecheck', 'nowalk', 'unguardable',
                'invisible')

nohitpause_list = ('AngleDraw', 'PlayerPush', 'Offset', 'ScreenBound', 'Trans',
                   'Width')

#
# =============================================================================


def scale_volume(value):
    # simple linear scaling of volume ranged (-255 to 255)
    return round((value + 255) / 512.0 * 100.0, 0)


def remove_3rd_index(text):
    return '{0:0}, {0:1}. {0:3}'.format(text.split(','))


def save(filename, data):
    if settings['overwrite']:
        with open(filename, 'w') as fh:
            fh.write(data)

    else:
        # rename file with 'backup' extension
        # write new file
        pass


def update_def(filename):
    cfg = INIConfig(open(filename))

    if cfg.Info.mugenversion == '1.0':
        raise Exception

    cfg.Info.mugenversion = '1.0'
    cfg.Info.localcoord = '320, 240'

    return cfg


def update_cns(filename):
    cfg = INIConfig(open(filename))

    # get a list of sections in the config file
    for name in list(cfg):
        section = getattr(cfg, name)

        # handle new volume change
        if 'volume' in list(section):
            section.volumescale = scale_volume(int(section.volume))
            del section.volume

        # strip the z value from velset
        if name[:8] == 'Statedef':
            if 'velset' in list(section):
                velset = section.velset.split(',')
                if len(velset) > 2:
                    section.velset = '{0}, {1}'.format(*velset[:2])

        # this block checks the type of the section
        s_type = section.type
        if not isinstance(s_type, Undefined):
            if s_type == 'HitDef':
                if 'pausetime' in list(section):
                    a, b = [int(i) for i in section.pausetime.split(",")]
                    section.pausetime = '{0}, {1}'.format(a - 1, b - 1)

                if 'snap' in list(section):
                    section.snap = remove_3rd_index(section.snap)

                if 'mindist' in list(section):
                    section.mindist = remove_3rd_index(section.mindist)

                if 'maxdist' in list(section):
                    section.maxdist = remove_3rd_index(section.maxdist)

            elif s_type in nohitpause_list:
                section.ignorehitpause = 1

            elif s_type == 'AssertSpecial' and section.flag in assert_flags:
                section.ignorehitpause = 1

    return cfg


handlers = {
    'def': update_def,
    'cns': update_cns,
}

if __name__ == '__main__':
    for dirpath, dirnames, filenames in os.walk('kengang'):
        for filename in filenames:
            ext = os.path.splitext(filename)[1][1:].lower()
            try:
                handler = handlers[ext]
            except:
                pass
            else:
                filename = os.path.join(dirpath, filename)
                save(filename, str(handler(filename)))
