import random

class append:
    def __init__(self,parent):
        self.parent = parent

    def fixup(self, element):
        #options: Value, InternalValue, DefaultValue
        return str(element.find("done.a").InternalValue).split()[1] + ", motherfucker"

class prepend:
    def __init__(self,parent):
        self.parent = parent

    def fixup(self, element):
        default  = '42'#str(element.name#find("Mdash.a1").DefaultValue)
        internal = ''#str(element.find("Mdash.a1").InternalValue)
        return default + ' ' + internal

