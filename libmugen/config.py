import re, collections


header_regex = re.compile('\[(.*)\]')
value_regex = re.compile('(.*?)\s*?\=\s*(.*)')
Section = collections.namedtuple('Section', ['name', 'values'])
Value = collections.namedtuple('Value', ['name', 'value'])


class MUGENConfigParser(object):
    def __init__(self):
        self.sections = []

    def read(self, filename):
        section = None
        fh = open(filename)
        line = fh.readline()
        while line:
            line = line.strip()
            if line:
                try:
                    if line[:3] == '\xef\xbb\xbf':
                        line = line[3:]
                except:
                    pass

                if not (line[0] == ";" or line[0] == "#"):
                    line = line.split(';', 1)[0].strip()
                    match = header_regex.match(line)
                    if match and section == None:
                        section = Section(match.group(1), [])
                    elif match:
                        self.sections.append(section)
                        section = Section(match.group(1), [])
                    elif not match:
                        match = value_regex.match(line)
                        if match:
                            value = Value(*match.groups())
                            section.values.append(value)
                        else:
                            section.values.append(line)
            line = fh.readline()

    def get(self, section_name, value_name):
        for section in self.sections:
            if section_name == section.name:
                for value in section.values:
                    if isinstance(value_name, str):
                        if value.name == value_name:
                            return value.value
