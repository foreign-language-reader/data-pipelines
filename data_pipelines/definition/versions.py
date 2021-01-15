class DefinitionVersions:
    def __init__(self, cedict):
        self.cedict = cedict


class DictionaryVersion:
    def __init__(self, version_name, link, entries=0):
        self.version_name = version_name
        self.link = link
        self.entries = entries
