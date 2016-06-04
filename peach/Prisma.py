# peach imports
import clr

clr.AddReference("Peach.Core")
from Peach.Core import Variant
from System import Array, Byte
# python imports
from urllib import unquote, quote
import random


def strFromHex(field):
    # uncomment next line in NON hex encoded mode
    # return field
    try:
        return str(field.InternalValue).replace(' ', '').decode('hex')
    except:
        return '-1337'


def strToHex(val):
    # uncomment next line in NON hex encoded mode
    # return val
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


def choose(Action, num):
    # val = self.dataModel.find('a1')
    # soLong = str(self.dataModel["a1"].InternalValue)
    soLong = str(Action.parent["randOut"].dataModel["a1"].InternalValue)
    f = open('woot', 'a')
    f.write('current rand: {}\n'.format(soLong))
    f.close()
    if soLong != '-1' and soLong != '':
        f = open('woot', 'a')
        f.write('randMan triggered\n')
        soLong = soLong.split(';;;')
        f.write('IDs: {}\n'.format(soLong))
        ID = random.choice(list(set(soLong)))
        f.write('chosen: {}\n'.format(ID))
        # val.DefaultValue = Variant(ID)
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(ID)
        f.close()
        return
    num = random.randint(0, num)
    # val.DefaultValue = Variant(num)
    Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
    return


def randChange(self, num):
    val = self.dataModel.find('a1')
    num = random.randint(0, num)
    val.DefaultValue = Variant(num)
    return


def set(Action):
    val = int(str(Action.dataModel["count"].InternalValue))
    val += 1
    Action.dataModel["count"].DefaultValue = Variant(val)


def fallback(Action, num):
    Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)


def randMan(Action, num=-1):
    if int(num) < 0:
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
        return
    f = open('woot', 'a')
    f.write('in randMan\n')
    soLong = str(Action.parent["randOut"].dataModel["a1"].InternalValue)
    f.write('soLong: {}\n'.format(soLong))
    if soLong == '-1':
        f.write('manipulating with num: {}\n'.format(num))
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(num)
    else:
        f.write('appending num: {}\n'.format(num))
        soLong += ';;;{}'.format(num)
        Action.parent["randOut"].dataModel["a1"].DefaultValue = Variant(soLong)
    f.write('\n')
    f.close()
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
    name(Action)


def updateHist(Action, ID=None):
    f = open('woot', 'a')
    f.write('updateHist\n')
    f.write(str(ID))
    f.write('\n')
    if ID == None:
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
    # here a hell of lot of logic to handle the hist correctly
    # the number MUST be 1 more than the horizon you would work on
    # thus a 5 horizon yields a 6!
    # below sample for 2 horizon:
    # field = Action.parent['theHist'].dataModel['ID-3']
    field = Action.parent['theHist'].dataModel['ID-X']

    field.DefaultValue = Variant(ID)
    return


def name(self):
    name = str(self.parent.name)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(name)
