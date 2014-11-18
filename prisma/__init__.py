from .PrismaState import PrismaState
from .MarkovTransition import MarkovTransition
from .MarkovModel import MarkovModel
from .Template import Template
from .TemplateContainer import TemplateContainer
from .RulesContainer import RulesContainer
from .Rule import Rule
from .DataRule import DataRule
from .CopyRule import CopyRule
from .Hist import Hist

def markovParse(filehandle):
    model = MarkovModel()
    for line in filehandle:
        line = line.split(',',1)[0]
        left, right = line.split('->')
        curState = PrismaState(*left.split('|'))
        nextState = PrismaState(*right.split('|'))
        transition = MarkovTransition(curState,nextState)
        model.add(transition)
    return model

def templateParse(filehandle):
    templates = TemplateContainer()
    ntokens = 0
    for line in filehandle:
        if ntokens == 0:
            line = line.split()
            ID = int(line[1].split(':')[1])
            left, right = line[2].split(':')[1].split('|')
            state = PrismaState(left,right)
            count = int(line[3].split(':')[1])
            fields = line[5].split(':')[1].split(',')
            if fields == ['']:
                fields = []
            else:
                fields = list(map(int,fields))
            ntokens = int(line[4].split(':')[1])
            content = []
            if ntokens == 0:
                templates.add(Template(ID,state,count,fields,content))
        else:
            content.append(line.strip())
            ntokens -= 1
            if ntokens == 0:
                templates.add(Template(ID,state,count,fields,content))
    return templates

def ruleParse(filehandle):
    rules = RulesContainer()
    dataRules = RulesContainer()

    dataFlag = 0
    ptypeFlag = 0

    line1 = filehandle.readline()
    while line1:
        line2 = filehandle.readline()
        if 'DataRule' in line1:
            dataFlag = 1
        if 'CopyComplete' in line1:
            ptypeFlag = 1
        line = line1.split()
        hist = Hist(*list(map(int,line[1].split(':')[1].split(';'))))
        srcID = int(line[2].split(':')[1])
        srcField = int(line[3].split(':')[1])
        dstField = int(line[4].split(':')[1])
        #NOTE 
        dstID = hist.curTempID
        if dataFlag == 1:
            data = line2.split(':')[1].split(',')
            data[-1] = data[-1].strip()
            dataRules.add(DataRule(hist,srcID,srcField,dstID,dstField,data))
            dataFlag = 0
        #TODO handle ptype accurate
        elif ptypeFlag == 1:
            ptype = line2.split(':')[1]
            rules.add(CopyRule(hist,srcID,srcField,dstID,dstField,ptype))
            ptypeFlag = 0
        else: #assuming: dataFlag == 0 and ptypeFlag == 0:
            rules.add(Rule(hist,srcID,srcField,dstID,dstField))
        line1 = filehandle.readline()
    return rules, dataRules

