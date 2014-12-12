import clr
clr.AddReference("Peach.Core")
from Peach.Core import Variant
import random

def prepend(self, pos, string):
    val = self.dataModel.find(pos)
    val.DefaultValue = Variant(string + str(val.InternalValue))

def manipulate(self, string):
    string = string.split(':::')
    for sub in string:
        sub = sub.split(';;')
        val = self.dataModel.find(sub[1])
        cur = str(val.InternalValue)
        if sub[0] == 'a':
            repl = Variant(cur + sub[2])
        else:
            repl = Variant(sub[2] + cur)
        val.DefaultValue = repl

def rand(self,num):
    num = random.randint(0,num)
    val = self.dataModel.find('a1')
    val.DefaultValue = Variant(num)
