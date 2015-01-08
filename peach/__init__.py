from .InterState import InterState
from .InterStateContainer import InterStateContainer
from .PIT import PIT
from lxml import etree as ET
from .additionalCode import manipulate

def dataModel(templates):
    pit = PIT()
    written = []
    root = pit.tree.getroot()
    for ID in templates.keys():
        for hist in templates[ID].hists:
            if hist not in written:
                written.append(hist)
                dataModel = ET.Element('DataModel', name= str(hist))
                #is multimodel
                if len(hist.curTempID) > 1:
                    #create all models the multimodel is referencing
                    choice = multimodel(root,ID,hist,written,templates)
                    dataModel.append(choice)
                else:
                    createContent(ID,dataModel,templates)
                root.append(dataModel)
    #create random datModel
    dataModel = ET.Element('DataModel', name= 'rand')
    dataModel.append(ET.Element('String', name= 'a1', attrib={'mutable':'false'}))
    root.append(dataModel)
    return pit

def multimodel(root, ID, hist, written, templates):
    choice = ET.Element('Choice', name='c', attrib={'minOccurs':'1', 'maxOccurs':'1'})
    count = 0
    for ID in hist.curTempID:
        dataModel = ET.Element('DataModel', name=str(ID))
        createContent(ID,dataModel,templates)
        choice.append(ET.Element('Block', name='o'+str(count), attrib={'ref':str(ID)}))
        count += 1
        if ID not in written:
            written.append(ID)
            root.append(dataModel)
    return choice

def createContent(ID, dataModel, templates):
    count = 0
    for cont in templates[ID].content:
        data = ET.Element('String', name='c'+str(count), attrib={'value':cont})
        dataModel.append(data)
        count += 1
    #if empty dataModel, insert empty String
    #later used as discriminative feature
    #if count == 0:
    #    dataModel.append(ET.Element('String', name='c0', attrib={'value':''}))
    return dataModel


def stateModel(pit, done, templates):
    #pit = PIT()
    pit.tree.getroot().append(ET.Element('StateModel', name='StateModel'))
    stateModel = pit.tree.getroot().find('StateModel')
    for state in done.values():
        #set initialState of StateModel
        if state.isinitial == True:
            stateModel.attrib.update({'initialState':str(state.hist)})
        actionCounter = 0
        peachState = ET.Element('State', name=str(state.hist))
        #implement slurp actions
        if state.IOAction == 'output' and state.rules:
            theRules = slurpActions(state,done)
            for rule in theRules:
                peachState.append(rule)
            actionCounter += len(theRules)
        #implement COPY actions
        #if state.copyRules != None and state.IOAction == 'output':
            #cpRules = assembleCopyRules(state, done)
        #implement IOactions
        #print(state.hist)
        if state.IOAction == 'input':
            inputAction = ET.Element('Action', name='rec', attrib={'type':'input'})
            inputAction.append(ET.Element('DataModel', name='read', attrib={'ref':str(state.hist)}))
            peachState.append(inputAction)
            actionCounter += 1
        if state.IOAction == 'output':
            #insert s here in onStart
            if state.copyRules != None:
                call = assembleCopyRules(state)
                outputAction = ET.Element('Action', name='out', attrib={'type':'output','onStart':'{}'.format(call)})
            else:
                outputAction = ET.Element('Action', name='out', attrib={'type':'output'})
            dataModel = ET.Element('DataModel', name='write', attrib={'ref':str(state.hist)})
            #look for DATA to be applied by DataRules
            if state.dataRules != None:
                dataModel = data(dataModel, state)
            outputAction.append(dataModel)
            peachState.append(outputAction)
            actionCounter += 1
        postHist = beatTehRandomness(state,templates)
        #implement random number
        if state.nextStates != None and len(postHist) > 1:
            randomAction = ET.Element('Action', name='rand', attrib={'type':'output','publisher':'null', 'onStart':'additionalCode.rand(self,{})'.format(len(postHist)-1)})
            randomAction.append(ET.Element('DataModel', attrib={'ref':'rand'}))
            peachState.append(randomAction)
        #impement changeState actions
        if postHist != None:
            change = computeChangeState(state, postHist, actionCounter)
            #prob = len(postHist) - 1
            #for ID,nextState in postHist.items():
            #    if len(nextState) > 1:
            #        for ns in nextState:
            #            changeState = ET.Element('Action', attrib={'type':'changeState', 'ref':str(ns), 
            #                'when':'(int(StateModel.states[{0}].actions[{1}].dataModel["a1"].InternalValue) == int({2})) and (dataModel.field[0] == {3}) '.format(state.hist,actionCounter,prob,templates[ID].content[0])})
            #            peachState.append(changeState)
            #        prob -= 1
            #    else:   changeState = None
            for ch in change:
                peachState.append(ch)
        stateModel.append(peachState)
    return pit

def assembleCopyRules(state):
    call = ''
    for rule in state.copyRules:
        print(rule.typ)
        if 'Complete' in rule.typ:
            print('complete rule')
            s = ''
            print(rule.content)
            for cont in rule.content:
                s+=(cont+':::')
            s = s[:-3]
            #s = "additionalCode.copyComplete(self,{0},c{1},{2})".format(rule.ptype,state.fields[rule.dstField],s)
            s = "comp,{0},c{1},{2}".format(rule.ptype,state.fields[rule.dstField],s)
            s = s + ';;;'
            call += s
        if 'Partial' in rule.typ:
            print('partial rule')
            #rule.cont here is seperator
            s = "part,{0},c{1},{2}".format(rule.ptype,state.fields[rule.dstField],rule.content)
            s += ';;;'
            print(s)
            #additionalCode.partialCopy(state,s)
            call += s
        if 'Seq' in rule.typ:
            print('sequential rule')
            s = "seq,{0},c{1},{2}".format(rule.ptype,state.fields[rule.dstField],rule.content)
    call = call[:-3]
    call = "additionalCode.manipulate(self,"+ call + ")"
    print(call)
    additionalCode.manipulate(state,call.split('self,')[1][:-1])
    return call

def computeChangeState(state, postHist, actionCounter):
    #print(state.hist)
    #print(postHist)
    #print(len(postHist))
    change = []
    if len(postHist) == 0:
        return change
    if len(postHist) == 1:
        #print(list(postHist.values())[0])
        change.append(ET.Element('Action', attrib={'type':'changeState', 'ref':str(list(postHist.values())[0][0])}))
        return change
    prob = len(postHist) - 1
    for ID, nextState in postHist.items():
        #print(nextState)
        for ns in nextState:
            if len(nextState) > 1:
                changeState = ET.Element('Action', attrib={'type':'changeState', 'ref':str(ns),
                    'when':'(int(StateModel.states[{0}].actions[{1}].dataModel["a1"].InternalValue == int({2}))) '
                    'and str(StateModel.states[{0}].actions[0].dataModel[0][0][0].referenceName) == "{3}")'
                    .format(state.hist, actionCounter, prob, ns.preTempID[0])})
            else:
                changeState = ET.Element('Action', attrib={'type':'changeState', 'ref':str(ns),
                    'when':'(int(StateModel.states[{0}].actions[{1}].dataModel["a1"].InternalValue == int({2}))) '
                    .format(state.hist, actionCounter, prob)})
            #print(ET.tostring(changeState,pretty_print = True))
            change.append(changeState)
        prob -= 1
    #print('\n')
    return change


def beatTehRandomness(state,templates):
    postHist = {}
    if state.postHist != None:# and len(state.postHist) > 1:
        #print('PRE',state.postHist,len(state.postHist))
        for hist in state.postHist:
            if hist.curTempID[0] not in postHist.keys():
                postHist.update({hist.curTempID[0]:[hist]})
            else:
                postHist[hist.curTempID[0]] += [hist]
        #print('POST',postHist,len(postHist))
        #print()
        #print('post',state.postHist)
        #TODO attention
        #getDiscriminativeFields(postHist.keys(),templates)
    return postHist

def getDiscriminativeFields(IDs, templates):
    #print(list(IDs))
    IDs = list(IDs)
    if IDs == ['00']:
        return
    fields = {}
    orderedForLength = []
    min = -1
    i = 0
    while IDs != []:
        j = 0
        min = -1
        while j < len(IDs):
            if IDs[j] not in templates.keys():
                IDs.remove(IDs[j])
                continue
            if min < 0 or templates[IDs[j]].length < min:
                min = templates[IDs[j]].length
                ind = j
            j += 1
        orderedForLength.append(IDs.pop(ind))
    #print(orderedForLength)
    cpy = orderedForLength[:]
    while orderedForLength != []:
        ID = orderedForLength[0]
        if templates[ID].length == 0:
            fields.update({ID:None})
            orderedForLength.remove(ID)
            continue
        for ind in range(len(templates[ID].content)):
            if templates[ID].content[ind] == '':
                continue
            possible = True
            for rest in orderedForLength[1:]:
                if templates[ID].content[ind] == templates[rest].content[ind]:
                    possible = False
                    break
            if possible == True:
                fields.update({ID:ind})
                orderedForLength.remove(ID)
                break
        if possible != True:
            print('gotta problem!')
    #print(fields)


#manually implement choice elements
#for data fields in template
#   compute crossproduct of data fields
#   and create data set for each tuple
def data(dataModel, state):
    #for i in state.dataRules:
        #print(i,'DST: ',i.dstField, state.dataFields, state.dataFields[i.dstField])
    index = 0
    data = []
    for dataRule in state.dataRules:
        data.append([])
        for d in dataRule.data:
            if d not in data[index]:
                data[index].append(d)
        index += 1
    #print(data)
    dat = cross(data)
    #print(dat)
    for d in dat:
        data = ET.Element('Data')
        for i in range(len(d)):
            #print(state.dataFields[state.dataRules[i].dstField])
            data.append(ET.Element('Field', name='c'+str(state.fields[state.dataRules[i].dstField]), attrib={'value':d[i]}))
        dataModel.append(data)
    #print()
    return dataModel

def cross(data,depth=0):
    #print('\nInto cross lvl{}'.format(depth,),'\n',data)
    tup = []
    if len(data) == 1:
        #print('internal: ',data)
        for r in data[0]:
            tup.append([r])
        return tup
    dat = data[0]
    ret = cross(data[1:],depth+1)
    #print(ret)
    #ret = ret[0]#cross(data[1:],depth+1)[0]
    #print('dat: ',dat)
    #print('Receiving ret on lvl{}: '.format(depth),ret)
    for d in dat:
        for r in ret:
            #print('internal: ',d,r)
            tup.append([d] + r)
    return tup
    #return data

def slurpActions(state,done):
    theRules = []
    #print(state.hist,state.IOAction)
    for rule in state.rules:
        #print(rule.dstField,state.fields)
        #construct path from where to read; valueXpath
        valueXpath = '//StateModel//{0}//rec//read//c{1}'.format(*findPreState(state,rule,done))
        #print(valueXpath)
        #construct path to where to write; setXpath
        setXpath = '//StateModel//{0}//out//write//c{1}'.format(str(state.hist),str(state.fields[rule.dstField]))
        theRules.append(ET.Element('Action',attrib={'type':'slurp','valueXpath':valueXpath, 'setXpath':setXpath}))
    return theRules

def findPreState(state,rule,done):
    depth = rule.srcID
    ID = rule.hist.getID(depth)
    while depth != -1:
        state = done[state.preHist]
        depth += 1
    if not state.isMultiModel:
        return (state.hist,state.fields[rule.srcField])
    else:
        for i in range(len(state.hist.curTempID)):
            if state.hist.curTempID  == ID:
                break
        return (state.hist,state.fields[i][rule.srcField])

