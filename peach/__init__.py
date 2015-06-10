# import prisma.Hist
from .PeachState import PeachState
from .PeachStateContainer import PeachStateContainer
from .PIT import PIT
from lxml import etree as ET
import random
import string
import base64
from urllib import parse

# testing purpose import
# from .additionalCode import manipulate


def test(pit, role=False, IP='127.0.0.1', port=80):
    pit.tree.getroot().append(ET.Element('Test', name='Default'))
    test = pit.tree.find('Test')
    test.append(ET.Element('Agent', attrib={'ref': 'Local'}))
    test.append(ET.Element('StateModel', attrib={'ref': 'StateModel'}))
    # append default publisher
    if role == True:
        publisher = ET.Element('Publisher', name='test', attrib={'class': 'TcpClient'})
        publisher.append(ET.Element('Param', name='Host', attrib={'value': str(IP)}))
    else:
        publisher = ET.Element('Publisher', name='test', attrib={'class': 'TcpListener'})
        publisher.append(ET.Element('Param', name='Interface', attrib={'value': str(IP)}))
    publisher.append(ET.Element('Param', name='Port', attrib={'value': str(port)}))
    test.append(publisher)
    # append publishing device for random number generating
    test.append(ET.Element('Publisher', name='null', attrib={'class': 'Null'}))
    #append some kind of logger
    logger = ET.Element('Logger', attrib={'class': 'File'})
    logger.append(ET.Element('Param', name='Path', attrib={'value': 'logs'}))
    test.append(logger)
    return pit


def agent(pit):
    pit.tree.getroot().append(ET.Element('Agent', name='Local'))
    agent = pit.tree.find('Agent')
    monitor = ET.Element('Monitor', attrib={'class': 'Process'})
    monitor.append(ET.Element('Param', name='Executable', attrib={'value': './server'}))
    monitor.append(ET.Element('Param', name='StartOnCall', attrib={'value': 'Start'}))
    monitor.append(ET.Element('Param', name='Arguments', attrib={'value': 'fuzzed.bin'}))
    agent.append(monitor)
    return pit


def createContent(ID, dataModel, templates):
    count = 0
    for cont in templates[ID].content:
        if count == 0:
            token = 'false'
        else:
            if dataModel[-1].attrib['token'] == 'false':
                token = 'true'
            else:
                token = 'false'
        if cont != '':
            data = ''
            #no-rule field
            if '%' in cont:
                #unquote encoding...
                #use blob in peach
                #data = ET.Element('String', name='c'+str(count), attrib={'value':cont,'token':'true'})
                #cont = parse.unquote(cont)
                cont = parse.unquote(cont)
                #check if there are non-printable characters
                escCont = ''.join(c for c in cont if c in string.printable)
                if not escCont == cont:
                    #handle 'em
                    #strip content to pure hex
                    #model field as hex number; NOT possible.. use BLOB instead
                    #for sake of ease
                    #cont = handleControl(cont)
                    cont = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(cont))))))
                    #size = str(int(len(''.join(cont.split()))/2)*8)
                    # if cont.find('port=') != -1:
                    #     token = 'false'
                    data = ET.Element('Blob', name='c' + str(count),
                                      attrib={'value': cont, 'token': token, 'valueType': 'hex'})  #,'size':size})
            # maybe it's a number? -> yields the need of knowing the exact size of the number, e.g. 32 bits, 8 bits, etc
            # else: put it in a string
            if data == '':
                # if cont.find('port=') != -1:
                #     token = 'false'
                #just a normal string, no non-printables detected
                data = ET.Element('String', name='c' + str(count), attrib={'value': cont, 'token': token})
        else:
            #rule field (empty)
            data = ET.Element('String', name='c' + str(count), attrib={'value': cont, 'token': 'false'})
        dataModel.append(data)
        count += 1
    # make sure last field contents twice /r/n
    if count != 0:
        if cont == '':
            if dataModel[-1].attrib['value'] == '':
                if dataModel[-2].attrib['value'] == '':
                    dataModel = dataModel[:-1]
                dataModel[-1].set('value', '\r\n\r\n')
                dataModel[-1].set('token', 'true')
                #elif 'valueType' in dataModel[-1].keys():
                #    if dataModel[-1].attrib['valueType'] == 'hex':
                #        if dataModel[-1].attrib['value'][-5:] != '0D 0A':
                #            if dataModel[-1].attrib['value'][-11:-5] != '0D 0A':
                #                print(dataModel[-1].attrib['value'])
                #                print(dataModel[-1].attrib['value'][-11:-5])
                #                data = ET.Element('String', name='c' + str(count+1), attrib={'value': '\r\n\r\n'})
                #            else:
                #                data = ET.Element('String', name='c' + str(count+1), attrib={'value': '\r\n'})
                #            dataModel.append(data)
                # #   pass
    return dataModel


def handleControl(cont, data=False):
    #by now ignores control characters... NOT!
    rmCont = ''
    contFlag = False
    for c in cont:
        if ord(c) <= 126 and ord(c) >= 32:
            rmCont += c
        else:
            contFlag = True
        if data == True and contFlag == True:
            print(parse.quote(cont))
    return rmCont


def dataModel(templates):
    pit = PIT()
    root = pit.tree.getroot()
    # create random dataModel
    dataModel = ET.Element('DataModel', name='rand')
    dataModel.append(ET.Element('String', name='a1', attrib={'mutable': 'false'}))
    root.append(dataModel)
    # create history dataModel
    dataModel = ET.Element('DataModel', name='hist')
    dataModel.append(ET.Element('String', name='c2', attrib={'mutable': 'false'}))  # the prePreState's name, a Hist-Obj
    dataModel.append(ET.Element('String', name='c1', attrib={'mutable': 'false'}))  # the preState's name
    root.append(dataModel)
    for ID in templates.keys():
        dataModel = ET.Element('DataModel', name='{}'.format(str(ID)))
        createContent(ID, dataModel, templates)
        root.append(dataModel)
    return pit


def createMultiModel(dataModelID):
    multiModel = ET.Element('DataModel', name=str(dataModelID))
    choice = ET.Element('Choice', name='c', attrib={'minOccurs': '1', 'maxOccurs': '1'})
    for dataModel in dataModelID.split('and'):
        choice.append(
            ET.Element('Block', name='o{}'.format(str(dataModel)), attrib={'ref': '{}'.format(str(dataModel))}))
        multiModel.append(choice)
    return multiModel


def modelName(modelIDs):
    modelName = ''
    for IDs in modelIDs:
        modelName += '{}and'.format(IDs)
    return  modelName[:-3]



def stateModel(dataPit, done, DEBUG = False):
    pit = PIT()
    pit.tree.getroot().append(ET.Element('StateModel', name='StateModel'))
    stateModel = pit.tree.getroot().find('StateModel')
    multiModels = {}
    for listOstates in done.values():
        for state in listOstates:
            actionCounter = 0
            stateName = encodeState(state, DEBUG)
            if state.isInit() == True:
                stateModel.attrib.update({'initialState': stateName})
            peachState = ET.Element('State', name=stateName)

            # install hist dataModel
            histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null', 'name': 'theHist'})
            histAction.append(ET.Element('DataModel', attrib={'ref': 'hist'}))
            peachState.append(histAction)
            actionCounter += 1

            # handle ioActions
            if state.ioAction != 'END':
                dataModelIDs = state.nextHist.getID()
                # dataModelIDs = state.nextHist.theHist[-1]
            if state.ioAction == 'input':
                histActionNumber = actionCounter
                name = modelName(dataModelIDs)
                if len(dataModelIDs) > 1 and tuple(dataModelIDs) not in multiModels.keys():
                    multiModels.update({tuple(dataModelIDs): createMultiModel(name)})
                inputAction = ET.Element('Action', name='in', attrib={'type': 'input'})
                inputAction.append(ET.Element('DataModel', name='read', attrib={'ref': name}))  # str(dataModelIDs)}))
                peachState.append(inputAction)
                actionCounter += 1
            elif state.ioAction == 'output':
                # have multiple output options
                # install random generator for output
                count = 0
                hasOpts = False
                if len(dataModelIDs) > 1:
                    outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randOut',
                                                                'onStart': 'additionalCode.rand(self,{})'.format(
                                                                    len(dataModelIDs) - 1), 'publisher': 'null'})
                    outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                    peachState.append(outputAction)
                    count = len(dataModelIDs) - 1
                    hasOpts = True
                    actionCounter += 1

                # histActionNumber = actionCounter
                # histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null', 'name': 'theHist'})
                # histAction.append(ET.Element('DataModel', attrib={'ref': 'hist'}))
                # peachState.append(histAction)
                # actionCounter += 1

                # check here for slurpActions
                # handle plain copy rules first
                slurpAction = slurpActions(state, done, DEBUG)
                for action in slurpAction:
                    peachState.append(action)
                    actionCounter += 1

                # then apply advance copyRules
                slurpAction = slurpActions(state, done, DEBUG, 'copy')
                for action in slurpAction:
                    peachState.append(action)
                    actionCounter += 1

                for ID in dataModelIDs:
                    outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'out{}'.format(ID)})
                    if count > 0:
                        whenExpression = 'int(self.parent.actions[1].dataModel["a1"].InternalValue) == int({})'.format(
                            count)
                        outputAction.set('when', whenExpression)
                        outputAction.append(
                            ET.Element('DataModel', attrib={'ref': '{}'.format(ID)}))  # , 'when': whenExpression}))
                        count -= 1
                    else:
                        if hasOpts == False:
                            outputAction.append(ET.Element('DataModel', attrib={'ref': '{}'.format(ID)}))
                        else:
                            whenExpression = 'int(self.parent.actions[0].dataModel["a1"].InternalValue) == int({})'.format(
                                count)
                            outputAction.set('when', whenExpression)
                            outputAction.append(ET.Element('DataModel', attrib={'ref': '{}'.format(ID)}))
                    peachState.append(outputAction)
                    actionCounter += 1

            # handle history update
            if state.isInit():
                histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null',
                                                          'onStart': 'additionalCode.updateHist(self)'})
                histAction.append(ET.Element('DataModel', attrib={'ref': 'hist', 'name': '{}Hist'.format(stateName)}))
                peachState.append(histAction)
                actionCounter += 1
                slurpAction = ET.Element('Action',
                                         attrib={'type': 'slurp', 'valueXpath': '//{}//theHist//c1'.format(stateName),
                                                 'setXpath': '//StateModel//hist//c2'})
                peachState.append(slurpAction)
                actionCounter += 1
                slurpAction = ET.Element('Action', attrib={'type': 'slurp',
                                                           'valueXpath': '//{}//{}Hist//c1'.format(stateName,
                                                                                                   stateName),
                                                           'setXpath': '//StateModel//hist//c1'})
                peachState.append(slurpAction)
                actionCounter += 1
            else:
                slurpAction = ET.Element('Action',
                                         attrib={'type': 'slurp', 'valueXpath': '//{}//theHist//c1'.format(stateName),
                                                 'setXpath': '//StateModel//hist//c2'})
                peachState.append(slurpAction)
                actionCounter += 1
                histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null',
                                                          'onStart': 'additionalCode.updateHist(self)'})
                histAction.append(ET.Element('DataModel', attrib={'ref': 'hist', 'name': '{}Hist'.format(stateName)}))
                peachState.append(histAction)
                actionCounter += 1
                slurpAction = ET.Element('Action', attrib={'type': 'slurp',
                                                           'valueXpath': '//{}//{}Hist//c1'.format(stateName,
                                                                                                   stateName),
                                                           'setXpath': '//StateModel//hist//c1'})
                peachState.append(slurpAction)
                actionCounter += 1
            # handle changeStateActions
            count = 0
            if len(state.nextStates) > 1:
                count = len(state.nextStates) - 1
                outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randChange',
                                                            'onStart': 'additionalCode.rand(self,{})'.format(
                                                                len(state.nextStates) - 1), 'publisher': 'null'})
                outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                peachState.append(outputAction)
            for nxt in state.nextStates:
                stateRef = '{} {}'.format(state.nextHist, nxt)
                if not DEBUG:
                    stateRef = str(base64.b64encode(stateRef.encode('ascii')))[2:-1].replace('=', '')
                if count > 0:
                    whenExpression = 'int(self.parent.actions[{0}].dataModel["a1"].InternalValue) == int({1})'.format(
                        actionCounter, count)
                    changeAction = ET.Element('Action',
                                              attrib={'type': 'changeState', 'ref': stateRef, 'when': whenExpression})
                    count -= 1
                else:
                    changeAction = ET.Element('Action', attrib={'type': 'changeState', 'ref': stateRef})
                peachState.append(changeAction)
            stateModel.append(peachState)
        stateModel.append(peachState)
    dataPitRoot = dataPit.tree.getroot()
    for ID in multiModels.values():
        dataPitRoot.append(ID)
    dataPitRoot.append(pit.tree.getroot().find('StateModel'))
    return dataPit


def assembleCopyRules(state, rule):
    call = ''
    absoluteDstfield = computeAbsoluteFields(state, rule.dstID[0], rule.dstField)
    if 'Complete' in rule.typ:
        s = ''
        for cont in rule.content:
            s += (cont + ':::')
        s = s[:-3]
        s = "comp,{0},c{1},{2}".format(rule.ptype, absoluteDstfield, s)
        s += ';;;'
        call += s
    if 'Partial' in rule.typ:
        # rule.cont here is seperator
        s = "part,{0},c{1},{2}".format(rule.ptype, absoluteDstfield, rule.content)
        s += ';;;'
        # additionalCode.partialCopy(state,s)
        call += s
    if 'Seq' in rule.typ:
        s = "seq,c{0},{1}".format(absoluteDstfield, rule.content)
        s += ';;;'
        call += s
    call = call[:-3]
    call = "additionalCode.manipulate(self,{})".format(call)
    # additionalCode.manipulate(state,call.split('self,')[1][:-1])
    return call


def computeChangeState(state, postHist, actionCounter, templates):
    #print(state.hist)
    #print(postHist)
    #print(len(postHist))
    change = []
    if len(postHist) == 0:
        return change
    if len(postHist) == 1:
        #print(list(postHist.values())[0])
        change.append(ET.Element('Action', attrib={'type': 'changeState', 'ref': str(list(postHist.values())[0][0])}))
        return change
    prob = len(postHist) - 1
    for ID, nextState in postHist.items():
        #need to deal with end states more efficiently...
        print('THEHIST >>>>>', state.hist)
        print('>>>>>', ID, nextState)
        if ID == -2:
            continue
        #TODO removed for design changes
        #what happens here?! PRODUCES MISSING DATAMODELS, BUT WRONG
        #for ns in nextState:
        #    if ns not in templates[ID].hists:
        #        #print(type(templates[ID]))
        #        templates[ID].hists.append(ns)
        #print(state.hist)
        #print(nextState)
        for ns in nextState:
            if len(nextState) > 1:
                changeState = ET.Element('Action', attrib={'type': 'changeState', 'ref': str(ns),
                                                           'when': '(int(StateModel.states["{0}"].actions[{1}].dataModel["a1"].InternalValue) == int({2}) '
                                                                   'and str(StateModel.states["{0}"].actions[0].dataModel[0][0][0].referenceName) == "{3}")'
                                         .format(state.hist, actionCounter, prob, ns.preTempID[0])})
            else:
                changeState = ET.Element('Action', attrib={'type': 'changeState', 'ref': str(ns),
                                                           'when': '(int(StateModel.states["{0}"].actions[{1}].dataModel["a1"].InternalValue) == int({2})) '
                                         .format(state.hist, actionCounter, prob)})
            #print(ET.tostring(changeState,pretty_print = True))
            change.append(changeState)
        prob -= 1
    #print('\n')
    #print()
    return change


#compute s states nextStates
#returns dict tempID:hists of nextStates
#def beatTehRandomness(state, templates):
#    postHist = {}
#    if state.postHist != None:  # and len(state.postHist) > 1:
#        #print('PRE',state.postHist,len(state.postHist))
#        for hist in state.postHist:
#            #print('HIST',hist)
#            if hist.theHist[-1][0] not in postHist.keys():
#                postHist.update({hist.theHist[-1][0]: [hist]})
#            else:
#                postHist[hist.theHist[-1][0]] += [hist]
#                #print('POST',postHist,len(postHist))
#                #print()
#                #print('post',state.postHist)

#                #        #getDiscriminativeFields(postHist.keys(),templates)
#    return postHist


#def getDiscriminativeFields(IDs, templates):
#    #print(list(IDs))
#    IDs = list(IDs)
#    if IDs == [-2]:
#        return
#    fields = {}
#    orderedForLength = []
#    min = -1
#    i = 0
#    while IDs != []:
#        j = 0
#        min = -1
#        while j < len(IDs):
#            if IDs[j] not in templates.keys():
#                IDs.remove(IDs[j])
#                continue
#            if min < 0 or templates[IDs[j]].length < min:
#                min = templates[IDs[j]].length
#                ind = j
#            j += 1
#        orderedForLength.append(IDs.pop(ind))
#    #print(orderedForLength)
#    cpy = orderedForLength[:]
#    while orderedForLength != []:
#        ID = orderedForLength[0]
#        if templates[ID].length == 0:
#            fields.update({ID: None})
#            orderedForLength.remove(ID)
#            continue
#        for ind in range(len(templates[ID].content)):
#            if templates[ID].content[ind] == '':
#                continue
#            possible = True
#            for rest in orderedForLength[1:]:
#                if templates[ID].content[ind] == templates[rest].content[ind]:
#                    possible = False
#                    break
#            if possible == True:
#                fields.update({ID: ind})
#                orderedForLength.remove(ID)
#                break
#        if possible != True:
#            print('gotta problem!')
#            #print(fields)


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
    #upper-bound number of tuples
    #limit to 4 per position; experimental
    for i in range(len(data)):
        if len(data[i]) > 4:
            data[i] = bound(data[i], 4)
    #print(data)
    dat = cross(data)
    #print(dat)
    retDat = []
    for d in dat:
        data = ET.Element('Data')
        for i in range(len(d)):
            #print(state.dataFields[state.dataRules[i].dstField])
            #unquote field content
            cont = d[i]
            if '%' in cont:
                cont = parse.unquote(cont)
                #check if there are non-printable characters
                escCont = ''.join(c for c in cont if c in string.printable)
                if not escCont == cont:
                    #deal with 'em
                    print('WARNING: CONTROLL CHARACTERS IN DATARULE')
                    print('\tunhandled so far...')
                    #cont = handleControl(cont,True)
                    cont = escCont
            data.append(
                ET.Element('Field', name='c' + str(state.fields[state.dataRules[i].dstField]), attrib={'value': cont}))
        retDat.append(data)
    #print()
    return dataModel, retDat


def bound(data, points):
    ret_data = []
    for i in range(points):
        j = random.randint(0, len(data) - 1)
        ret_data.append(data[j])
    return ret_data


def cross(data, depth=0):
    #print('\nInto cross lvl{}'.format(depth,),'\n',data)
    tup = []
    if len(data) == 1:
        #print('internal: ',data)
        for r in data[0]:
            tup.append([r])
        return tup
    dat = data[0]
    ret = cross(data[1:], depth + 1)
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

def encodeState(state, DEBUG = False):
    if DEBUG:
        return '{} {}'.format(state.hist, state.curState)
    return str(base64.b64encode('{} {}'.format(state.hist, state.curState).encode('ascii')))[2:-1].replace('=', '')

def slurpActions(state, done, DEBUG, ruleType='rules'):
    if ruleType == 'rules' and state.rules == []:
        return []
    if ruleType == 'copy' and state.copyRules == []:
        return []
    theRules = []
    encState = encodeState(state, DEBUG)
    preStates, prePreStates = findPreState(state, done)
    for ruleList in state.getRules(ruleType):
        for rule in ruleList:
            #construct path from where to read; valueXpath
            ID = rule.ruleHist.getID(rule.srcID)[0]
            if rule.srcID == -1:
                absoluteSrcField = computeAbsoluteFields(state, ID, rule.srcField)
            for preState in preStates:
                if rule.srcID == -2:
                    absoluteSrcField = computeAbsoluteFields(preState, ID, rule.srcField)
                for prePreState in prePreStates:
                    encPre = encodeState(preState, DEBUG)
                    if rule.srcID == -3:
                        absoluteSrcField = computeAbsoluteFields(prePreState, ID, rule.srcField)
                    if preState.ioAction == 'input':
                        if not preState.isMulti():
                            # actually does not appear
                            valueXpath = '//StateModel//{0}//in//c{1}'.format(encPre, absoluteSrcField)
                        else:
                            valueXpath = '//StateModel//{0}//in//o{1}//c{2}'.format(encPre, ID, absoluteSrcField)
                    else:
                        valueXpath = '//StateModel//{0}//out{1}//c{2}'.format(encPre, ID, absoluteSrcField)
                    setXpath = '//StateModel//{}//out{}//c{}'.format(encState, rule.dstID[0], computeAbsoluteFields(
                        state, rule.ruleHist.getID()[0], rule.dstField))  # rule.dstID[0])
                    slurp = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': valueXpath, 'setXpath': setXpath})
                    when = computeWhen(state, preState, prePreState, rule, DEBUG)
                    slurp.set('when', when)
                    if ruleType == 'copy':
                        call = assembleCopyRules(state, rule)
                        slurp.set('onComplete', call)
                    theRules.append(ET.Comment('applying {} {}'.format(ruleType,rule)))
                    theRules.append(slurp)
    return theRules


def computeWhen(state, preState, prePreState, rule, DEBUG = False):
    correctModel = computeWhenOut(state, rule.ruleHist.getID()[0], DEBUG)
    correctPre = computeWhenHist(preState, 1, DEBUG)
    correctPrePre = computeWhenHist(prePreState, 2, DEBUG)
    correctPreModel = computeWhenOut(preState, rule.ruleHist.getID(-2)[0], DEBUG)
    correctPrePreModel = computeWhenOut(prePreState, rule.ruleHist.getID(-3)[0], DEBUG)

    return '{} and {} and {} and {} and {}'.format(correctModel, correctPre, correctPrePre,
                                                   correctPreModel, correctPrePreModel)


def computeAbsoluteFields(state, templateID, relativeField):
    return state.fields[templateID][relativeField]


def computeWhenHist(state, age, DEBUG = False):
    return "str(self.parent.actions[0].dataModel[c{}].InternalValue) == str('{}')"\
        .format(age, encodeState(state, DEBUG))


def computeWhenOut(state, tempID, DEBUG = False):
    if state.ioAction == 'output':
        if state.isMulti():
            return "int({}.action[1].InternalValue) == int({})".format(encodeState(state, DEBUG), len(state.templates) - 1 -
                                                                   state.templates.index(tempID))
        else:
            # the state then has only one model that could have been sent
            return '1 == 1'
    else:  # state is input
        if state.isMulti():
            return 'str(StateModel.states["{}"].actions[1].dataModel[0][0][0].referenceName) == str("{}")'.format(encodeState(state, DEBUG), tempID)
        else:  # the state then has only one model that could have been received
            return '1 == 1'


def findPreState(state, done):
    preState = done[state.preHist]
    preState = [ps for ps in preState if ps.nextHist == state.hist]
    prePreState = []
    for pre in preState:
        prePreState += done[pre.preHist]
    return (preState, prePreState)


def match(state, ruleList):
    retList = []
    for rule in ruleList:
        if rule.ruleHist.getID()[0] in state.templates:
            retList.append(rule)
    return retList

def stateAssembler(state, container, model, templates, rules, copyRules, dataRules, UAC=True):
    #fetch ioAction
    if (UAC == True and 'UAC' in state.getCurState()) or (UAC == False and 'UAC' not in state.getCurState()):
        state.ioAction = 'output'
    else:
        state.ioAction = 'input'

    if 'END' == state.getCurState():
        state.ioAction = 'END'

    #fetch emittable Template IDs
    #compute hist of nextStates
    if state.curState in templates.stateToID.keys():
        state.templates = templates.stateToID[state.curState]
        state.nextHist = state.hist.update(state.templates)
        #print(state.nextHist)

    #fetch fields of the templates
    for ID in state.templates:
        state.fields.update({ID: templates.IDtoTemp[ID].fields})

    #fetch nextStates
    if state.curState in model.model.keys():
        state.nextStates = model.model[state.curState]
    else:
        # no nextStates ==>> END STATE
        # handle directly
        state.nextStates = []
        appendTodo(container, state)
        return

    #fetch rules
    lenHist = len(state.hist.theHist)
    possibleHists = state.hist.assembleHist(lenHist)
    #normal rules
    for hist in possibleHists:
        if hist in rules.keys():
            rule = match(state, rules[hist])
            if rule:
                state.rules.append(rule)
    #data rules
    for hist in possibleHists:
        if hist in dataRules.keys():
            rule = match(state, dataRules[hist])
            if rule:
                state.dataRules.append(rule)
    #copy rules
    for hist in possibleHists:
        if hist in copyRules.keys():
            rule = match(state, copyRules[hist])
            if rule:
                state.copyRules.append(rule)

    #if state.hist in dataRules.keys():
    #    state.dataRules = dataRules[state.hist]
    #if state.hist in copyRules.keys():
    #    state.copyRules = copyRules[state.hist]

    #print('=====DONESTATE=====', state,state.nextStates, state.isInit(),state.nextHist,'\n')
    appendTodo(container, state)
    return


def appendTodo(container, state):
    if state.hist in container.done.keys():
        for stateDash in container.done[state.hist]:
            if state == stateDash:
                return
    container.doneadd(state)
    if state.nextStates != []:
        for nextState in state.nextStates:
            nxt = PeachState(nextState, state.hist, state.nextHist)
            container.todoadd(nxt)
    return
