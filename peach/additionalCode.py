#import clr
#clr.AddReference("Peach.Core")
#from Peach.Core import Variant
import random

def prepend(self, pos, string):
    val = self.dataModel.find(pos)
    val.DefaultValue = Variant(string + str(val.InternalValue))

def manipulate(PeachState, task):
    print(task)
    tasks = task.split(';;;')
    for task in tasks:
        task = task.split(',',3)
        print(task)
        if task[0] == 'comp':
            print('in here')
            copyComplete(PeachState,task[1:])
            continue
        if task[0] == 'part':
            print('in here')
            partialCopy(PeachState, task[1:])
            continue


def copyComplete(self, l):
    #l = l.split(',',2)
    while l != []:
        sub = l[0:3]
        l = l[3:]
        #val = self.dataModel.find(sub[1])
        #cur = str(val.InternalValue)
        content = sub[2].split(':::')
        content = random.choice(content)
        print(sub, content)
        return
        if sub[0] == 'PREFIX':
            repl = Variant(cur + ' ' + content)
        else:
            repl = Variant(content + ' ' + cur)
        #val.DefaultValue = repl
        return

def partialCopy(self, l):
    print(l)

def rand(self,num):
    num = random.randint(0,num)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(num)

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
