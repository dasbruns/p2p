# peach imports
import clr

clr.AddReference("Peach.Core")
from Peach.Core import Variant
from System import Array, Byte
# python imports
from urllib import unquote, quote
import random


def strFromHex(field):
    try:
        return str(field.InternalValue).replace(' ', '').decode('hex')
    except:
        return '-1337'


def strToHex(val):
    try:
        ar = map(lambda x: ord(x), str(val))
        return Array[Byte](ar)
    except:
        return strToHex("-1")


def dataRule(Action, num=0):
    f = open('woot', 'a')
    f.write('DataRule\n')
    f.write(str(Action.parent.name))
    f.write('\n')
    sXp = Action.setXpath.split('//')
    f.write('split\n')
    f.write(str(sXp[3]))
    f.write('\n')
    f.write(str(sXp[5]))
    f.write('\n')
    if num:
        field = Action.parent['{}'.format(sXp[3])].dataModel['blockB']['{}'.format(sXp[5])]
    else:
        field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    f.write('field\n')
    # val = str(field.InternalValue)
    # val = str(field.InternalValue).replace(' ','').decode('hex')
    # f.write(str(field.InternalValue))
    val = strFromHex(field)
    # f.write(str(val))
    # f.write('\n')
    f.write('fromHex\n')
    val = val.split(';;;')
    f.write('split\n')
    choice = random.choice(val)
    f.write('chose\n')
    # i = random.randint(0, len(val) - 1)
    # choice = val[i]
    # f.write(str(choice))
    # f.write('\n Into TYPEFIX\n')
    try:
        # pimped = strToHex(unquote(str(choice)))
        f.write('trying to pimp..\n')
        pimped = strToHex(choice)
        f.write('pimped\n')
    except:
        f.write('something wrong here\n')
        pimped = choice
    # f.write(str(pimped))
    # f.write('\n out da TYPEFIX\n')
    f.write('\n')
    f.close()
    field.DefaultValue = Variant(pimped)
    # randMan(Action, randManipulator)
    return


def copySeq(Action, change):
    f = open('woot', 'a')
    f.write('seqRule\n')
    f.write(str(Action.parent.name))
    f.write('\n')
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    f.write('initial\n')
    # f.write(str(int(str(field.InternalValue))))
    # f.write('\n')
    # # f.write(str(int(str(field.InternalValue))))
    # f.write(quote(str(field.InternalValue).encode('utf-8').encode('hex')))
    # f.write('\n')
    try:
        # we know here only appear hex-strings
        # f.write(str(field.InternalValue))
        # f.write('\n')
        # val = int(str(field.InternalValue).replace(' ',''), 16)
        # val = int(str(field.InternalValue).decode('hex'))
        try:
            f.write('trying to read int\n')
            val = int(strFromHex(field))
            f.write('read int: {}\n'.format(val))
        except:
            f.write('something wrong\n')
            val = int('-1337')
        # val = int(str(field.InternalValue).replace(' ','').decode('hex'))
        f.write('cast done \n')
    except TypeError:
        field.DefaultValue = Variant(strToHex(-1))
        return
    f.write('{} --> {} \n'.format(val, val + change))
    val += int(change)
    f.write('change done \n\n')
    field.DefaultValue = Variant(strToHex(val))
    # randMan(Action, randManipulator)
    f.close()
    return


def copyPart(Action, where, separator):
    f = open('woot', 'a')
    f.write('partRule\n')
    f.write(str(Action.parent.name))
    f.write('\n')
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    # val = str(field.InternalValue).replace(' ','').decode('hex')
    f.write('read value\n')
    val = strFromHex(field)
    f.write('split value for {}\n'.format(separator))
    val = val.split(unquote(separator))
    f.write('split value {}\n'.format(str(val)))
    if 'PREFIX' in where:
        f.write('as prefix\n')
        val = val[0]
    else:
        f.write('as suffix\n')
        if len(val) > 1:
            val = val[1]
        else:
            f.write('as suffix failed\n')
            val = val[0]
    f.write('\n')
    f.close()
    field.DefaultValue = Variant(strToHex(val))
    # randMan(Action, randManipulator)
    return


def copyComp(Action, where, what):
    f = open('woot', 'a')
    f.write('compRule\n')
    f.write(str(Action.parent.name))
    f.write('\n')
    sXp = Action.setXpath.split('//')
    field = Action.parent['{}'.format(sXp[3])].dataModel['{}'.format(sXp[5])]
    # val = str(field.InternalValue).replace(' ','').decode('hex')
    val = strFromHex(field)
    f.write(val)
    f.write('\n')
    f.write(what)
    f.write('\n')
    f.write(where)
    f.write('\n')
    what = what.split(';;;')
    # if len(what) == 1:
    #     f.write('bullshit\n')
    #     field.DefaultValue = Variant(strToHex(val))
    #     return 
    i = random.randint(0, len(what) - 1)
    add = unquote(what[i])
    if where == 'PREFIX':
        f.write('as prefix\n')
        val += add
    else:
        f.write('as suffix\n')
        val = add + val
    f.write(val)
    f.write('\n')
    f.close()
    field.DefaultValue = Variant(strToHex(val))
    # randMan(Action, randManipulator)
    return


def rand(self, num):
    val = self.dataModel.find('a1')
    soLong = self.dataModel["a1"].InternalValue
    if soLong != '-1':
        f = open('woot', 'a')
        f.write('randMan triggered\n')
        soLong = soLong.split(';;;')
        f.write('IDs: {}\n'.format(soLong))
        ID = random.choice(list(set(soLong)))
        f.write('chosen: {}\n'.format(ID))
        val.DefaultValue = Variant(ID)
        return
    num = random.randint(0, num)
    val.DefaultValue = Variant(num)
    return


# def randMan(Action, num):
# 	if int(num) < 0:
# 		return
# 	Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
# 	return


def set(Action, modelsIDs):
    Action.dataModel["a1"].DefaultValue = Variant(modelsIDs)


def choose(Action, num):
    soLong = str(Action.parent["randOut"].dataModel["a1"].InternalValue)
    if ';;;' in soLong:
        soLong = soLong.split(';;;')
        num = random.choice(soLong)
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
        return
    if soLong == '-1':
        try:
            modelwithoutfields = str(Action.parent["fallback"].dataModel["a1"].InternalValue).split(';')
            modelwithoutfields = random.choice(modelwithoutfields)
            modelwithoutfields = int(modelwithoutfields)
            if modelwithoutfields != -1:
                f = open('woot', 'a')
                f.write('fallback triggered')
                f.close()
                Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(modelwithoutfields)
                return
        except:
            pass

        num = random.randint(0, num)
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
        return
    return


def randMan(Action, num=-1):
    # if int(num) < 0:
    #     Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
    #     return
    soLong = str(Action.parent["randOut"].dataModel["a1"].InternalValue)
    if soLong == '-1':
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
    else:
        soLong += ';;;{}'.format(num)
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(soLong)
    return


def end(Action):
    f = open('passedStates', 'a')
    f.write(str(Action.parent.name))
    f.write(' ')
    f.write('END ')
    f.close()


def start(Action):
    f = open('passedStates', 'a')
    f.write('NEWSESSION ')
    f.close()


def init(self):
    # name = self.parent.name
    # stateModel = self.parent.parent
    # stateModel.states[initial][name].when = "1 == 0"
    # self.parent["isInit"].dataModel["a1"].DefaultValue = Variant(1)
    self.when = "1 == 0"
    end(self)
    return


def updateHist(Action, ID=None):
    f = open('woot', 'a')
    f.write('updateHist\n')
    f.write(str(ID))
    f.write('\n')
    if not ID:
        try:
            ID = Action.dataModel[0][0][0].referenceName
        except:
            f.write('no message received')
            f.write('\n')
            ID = -1

    f.close()
    f = open('passedStates', 'a')
    f.write(str(Action.parent.name))
    f.write(';;;')
    f.write(str(ID))
    f.write(' ')
    f.close()
    field = Action.parent['theHist'].dataModel['ID-3']
    # f = open('opts','a')
    # f.write(str(dir(field)))
    # f.write('\n\n')
    # f.write(str(field.GetDefaultValue()))
    # f.write('\n\n')
    # f.close()
    field.DefaultValue = Variant(ID)
    return
    # hist = self.parent.name
    # val = self.dataModel.find('c1')
    # val.DefaultValue = Variant(hist)
    # return


def name(self):
    name = str(self.parent.name)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(name)
