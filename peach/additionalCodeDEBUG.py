import clr

clr.AddReference("Peach.Core")
from Peach.Core import Variant
import random


def dataRule(Action):
    sXp = Action.setXpath.split('//')
    f = open('woot', 'a')
    f.write('\napplying data rule')
    f.write('\n')
    f.write(str(sXp[3]))
    f.write('\n')
    f.write(str(sXp[5]))
    f.write('\n')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    f.write(val)
    f.write('\n')
    val = val.split(';;;')
    i = random.randint(0, len(val) - 1)
    f.write(val[i])
    f.write('\n')
    field.DefaultValue = Variant(val[i])
    f.close()
    return


def copySeq(Action, change):
    sXp = Action.setXpath.split('//')
    f = open('woot', 'a')
    f.write('\napplying sequential rule')
    f.write('\n')
    f.write(str(sXp[3]))
    f.write('\n')
    f.write(str(sXp[5]))
    f.write('\n')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    f.write(str(field.InternalValue))
    f.write('\n')
    f.write(str(change))
    try:
        val = int(field.InternalValue)
    except TypeError:
        f.write('\n')
        f.write('UNSUCESSFUL')
        f.write('\n')
        return
    f.write('\n')
    f.write(str(val))
    val += change
    f.write('\n')
    f.write(str(val))
    field.DefaultValue = Variant(str(val))
    f.write('\n')
    f.close()
    return


def copyPart(Action, where, seperator):
    sXp = Action.setXpath.split('//')
    f = open('woot', 'a')
    f.write('\napplying partial rule')
    f.write('\n')
    f.write(str(sXp[3]))
    f.write('\n')
    f.write(str(sXp[5]))
    f.write('\n')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    f.write(val)
    f.write('\n')
    f.write(seperator)
    f.write('\n')
    val = val.split(seperator)
    if 'PREFIX' in where:
        val = val[0]
    else:
        val = val[1]
    f.write(val)
    f.write('\n')
    field.DefaultValue = Variant(val)
    f.close()
    return


def copyComp(Action, where, what):
    sXp = Action.setXpath.split('//')
    f = open('woot', 'a')
    f.write('\napplying complete rule')
    f.write('\n')
    f.write(str(sXp[3]))
    f.write('\n')
    f.write(str(sXp[5]))
    f.write('\n')
    field = Action.parent.actions['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    val = str(field.InternalValue)
    f.write(val)
    f.write('\n')
    what = what.split(';;;')
    f.write(what)
    f.write('\n')
    f.write(where)
    f.write('\n')
    i = random.randint(0, len(what) - 1)
    if where == 'PREFIX':
        val += what[i]
    else:
        val = what[i] + val
    f.write(val)
    f.write('\n')
    field.DefaultValue = Variant(val)
    f.close()
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
