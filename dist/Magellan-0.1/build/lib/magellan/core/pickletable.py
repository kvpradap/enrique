class PickleTable(object):
    def __init__(self, table, properties):
        self.table = table
        self.properties = properties
        self.ltable_properties = None
        self.rtable_properties = None
        if properties.has_key('ltable'):
            ltable = table.get_property('ltable')
            self.ltable_properties = ltable.properties
        if properties.has_key('rtable'):
            rtable = table.get_property('rtable')
            self.rtable_properties = rtable.properties

