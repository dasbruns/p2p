import clr
clr.AddReference("Peach.Core")
from Peach.Core import Variant
import random

def prepend(self, pos, string):
    val = self.dataModel.find(pos)
    val.DefaultValue = Variant(string + str(val.InternalValue))

def manipulate(PeachState, task):
    tasks = task.split(';;;')
    for task in tasks:
        task = task.split(',',3)
        if task[0] == 'comp':
            copyComplete(PeachState,task[1:])
            continue
        if task[0] == 'part':
            partialCopy(PeachState, task[1:])
            continue
        if task[0] == 'seq':
            seqCopy(PeachState, task[1:])

def seqCopy(PeachState, task):
    field = PeachState.dataModel.find(task[0])
    val = int(field.InternalValue)
    field.DefaultValue = Variant(val + int(task[1]))

def partialCopy(PeachState, task):
    field = PeachState.dataModel.find(task[1])
    val = str(field.InternalValue)
    split = val.split(task[2],1)
    if len(split) != 2:
        val = ''
        field.DefaultValue = Variant(val)
        return
    if task[0] == 'SUFFIX':
        val = split[1]
    else:
        val = split[0]
    field.DefaultValue = Variant(val)

def copyComplete(self, l):
    #f = open('self','w')
    #f.write(str(self.dataModel.referenceName))
    #f.write(l)
    #f.close()
    #l = l.split(',',2)
    #while l != []:
    #    sub = l[0:3]
    #    l = l[3:]
    val = self.dataModel.find(l[1])
    cur = str(val.InternalValue)
    content = l[2].split(':::')
    content = random.choice(content)
    if l[0] == 'PREFIX':
        repl = Variant(cur + ' ' + content)
    else:
        repl = Variant(content + ' ' + cur)
    val.DefaultValue = repl

def rand(self,num):
    num = random.randint(0,num)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(num)

def updateHist(self):
    hist = self.parent.name
    val = self.dataModel.find('c1')
    val.DefaultValue = Variant(hist)

def test(self):
    f=open('self','a')
    f.write('self:\n')
    f.write(str((self.name)))
    f.write('\n\n')
   # #f.write('self.Options:\n')
   # f.write(str(dir(self)))
   # f.write('\n\n')
   # f.write('self.InputData:\n')
   # f.write(str((self.inputData))+'\n')
   # for i in list(self.inputData):
   #     f.write(str(dir(i))+'\n')
   #     f.write(str((i.allData)))
   # f.write('\n\n')
   # f.write('self.InputDataOptions:\n')
   # f.write(str(dir(self.inputData)))
   # f.write('\n\n')
   # f.write('self.Parent:\n')
   # f.write(str(self.parent.name))
   # f.write('\n\n')
   # f.write('self.ParentOptions:\n')
   # f.write(str(dir(self.parent)))
   # f.write('\n\n')
   # f.write('self.DataModel:\n')
   # f.write(str((self.dataModel.name))+', '+str(self.dataModel.referenceName))
   # f.write('\n\n')
   # f.write('self.DataModelOptions:\n')
   # f.write(str(dir(self.dataModel)))
   # f.write('\n\n')
   # f.write('self.Data:\n')
    #THE RECEIVED DATAMODELS NAME
    f.write(str((self.dataModel[0][0][0].referenceName)))#[0][0].InternalValue)))
    f.write('\n')
    f.write(str(str((self.dataModel[0][0][0].referenceName))=='M5'))#[0][0].InternalValue)))
    f.write('\n\n')
    #f.write('\n\nself.pretty:\n')
    #f.write(self.dataModel.prettyPrint())
    #f.write('\n\nself.shema:\n')
    #f.write(str(self.schemaData))
    #f.write('\n\nself.dataModel:\n')
    #f.write(str(dir(self.dataModel)))
    #f.write('\n\nself.dataModel.referenceName:\n')
    #f.write(self.dataModel.referenceName)
    #f.write('\n\nself.dataModel.FullName:\n')
    #f.write(str(self.dataModel.fullName))
    #f.write('\n\nself.dataModel.test:\n')
    #f.write(str(dir(self.dataModel))+'\n')
    #f.write(str(self.dataModel))#.GetType()))
    #f.write('\n=======================================\n\n')
    f.close()
