from character import Character

import re, os


name_regex = re.compile('name\s*?=\s*?\"(.*?)\"', re.I)

# dirty hack to guess if a .def file is a proper character definition
def parse_def(filename):
    try:
        fh = open(filename)
    except:
        return {}

    d = {}
    line = fh.readline()
    while not line == "":
        match = name_regex.match(line)
        if match:
            name = match.groups()[0]
            if name != "":
                d['name'] = name

        line = fh.readline()

    return d


# returns a generator that returns any character found in all subfolders
# it is sorted by the parent folder and groups by folder
def get_characters(root):
    def glob_defs(filenames):
        return [i for i in filenames if i[-3:].lower() == "def"]

    # glob the characters and group by subdirectory
    def glob_chars(path):
        pushback = []
        
        paths = [os.path.join(path, i) for i in os.listdir(path)]
        dirnames = [i for i in paths if os.path.isdir(i)]
        dirnames.reverse()

        while dirnames:
            path = dirnames.pop()
            defs = glob_defs(os.listdir(path))
            paths = [os.path.join(path, i) for i in os.listdir(path)]
            subdirs = [i for i in paths if os.path.isdir(i)]

            if subdirs:
                pushback.append(path)

            while defs:
                yield os.path.join(path, defs.pop())

        while pushback:
            path = pushback.pop()
            for char in glob_chars(path):
                yield char

    for path in glob_chars(root):
        d = parse_def(path)
        try:
            yield Character(d['name'], path)
        except KeyError:
            pass

