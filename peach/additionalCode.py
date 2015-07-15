import clr

clr.AddReference("Peach.Core")
from Peach.Core import Variant
import random


def dataRule(Action):
    sXp = Action.setXpath.split('//')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    val = val.split(';;;')
    i = random.randint(0, len(val) - 1)
    field.DefaultValue = Variant(val[i])
    return


def copySeq(Action, change):
    sXp = Action.setXpath.split('//')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = int(field.InternalValue)
    val += change
    field.DefaultValue = Variant(val)
    return


def copyPart(Action, where, seperator):
    sXp = Action.setXpath.split('//')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    val = val.split(seperator)
    if 'PREFIX' in where:
        val = val[0]
    else:
        val = val[1]
    field.DefaultValue = Variant(val)
    return


def copyComp(Action, where, what):
    sXp = Action.setXpath.split('//')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    what = what.split(';;;')
    i = random.randint(0, len(what) - 1)
    if where == 'PREFIX':
        val += what[i]
    else:
        val = what[i] + val
    field.DefaultValue = Variant(val)
    return


def rand(self, num):
    num = random.randint(0, num)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(num)
    return


def updateHist(self):
    hist = self.parent.name
    val = self.dataModel.find('c1')
    val.DefaultValue = Variant(hist)
    return
