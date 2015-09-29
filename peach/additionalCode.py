#peach imports
import clr
clr.AddReference("Peach.Core")
from Peach.Core import Variant
from System import Array, Byte
# python imports
from urllib import unquote
import random


def dataRule(Action):
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    val = val.split(';;;')
    i = random.randint(0, len(val) - 1)
    field.DefaultValue = Variant(typeFix(unquote(val[i])))
    return


def copySeq(Action, change):
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    try:
        val = int(str(field.InternalValue))
    except TypeError:
        return
    val += change
    field.DefaultValue = Variant(typeFix(val))
    return


def copyPart(Action, where, seperator):
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    val = val.split(seperator)
    if 'PREFIX' in where:
        val = val[0]
    else:
        val = val[1]
    field.DefaultValue = Variant(typeFix(val))
    return


def copyComp(Action, where, what):
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    what = what.split(';;;')
    i = random.randint(0, len(what) - 1)
    # ToDO: unquote what
    if where == 'PREFIX':
        val += what[i]
    else:
        val = what[i] + val
    field.DefaultValue = Variant(typeFix(val))
    return


def rand(self, num):
    num = random.randint(0, num)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(num)
    return


def typeFix(val):
    # make sure val is str
    # get ord of each char ..
    ar = map(lambda x: ord(x), str(val))
    # .. and put it in byte array
    # this is a Blob of type hex in Peach
    return Array[Byte](ar)


def updateHist(self):
    hist = self.parent.name
    val = self.dataModel.find('c1')
    val.DefaultValue = Variant(hist)
    return
