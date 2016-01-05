# import prisma.Hist
from .PeachState import PeachState
from .PeachStateReloaded import PeachStateReloaded
from .PeachStateContainer import PeachStateContainer
from .PIT import PIT
from lxml import etree as ET
import copy
import string
import base64
import random
from urllib import parse

# testing purpose import
# from .additionalCode import manipulate

# dataModelID to dataModelLength dictionary
# insert empty template with length 0 manually
length = {"''": 0}
tempID2StateMap = []


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
    test.append(ET.Element('Publisher', name='nullOUT', attrib={'class': 'Console'}))
    #append some kind of logger
    logger = ET.Element('Logger', attrib={'class': 'File'})
    logger.append(ET.Element('Param', name='Path', attrib={'value': 'logs'}))
    test.append(logger)
    return pit


def agent(pit, application, fuzzedBin):
    pit.tree.getroot().append(ET.Element('Agent', name='Local'))
    agent = pit.tree.find('Agent')
    agent.append(ET.Element('Monitor', attrib={'class': 'LinuxCrashMonitor'}))
    monitor = ET.Element('Monitor', attrib={'class': 'Process'})
    monitor.append(ET.Element('Param', name='Executable', attrib={'value': './{}'.format(application)}))
    monitor.append(ET.Element('Param', name='StartOnCall', attrib={'value': 'Start'}))
    monitor.append(ET.Element('Param', name='Arguments', attrib={'value': '{}'.format(fuzzedBin)}))
    agent.append(monitor)
    return pit


def createContent(ID, dataModel, templates, fuzzyness, blob, advanced):
    count = 0
    mutCount = -1
    for cont in templates[ID].content:
        mutCount -= 1
        if random.random() <= float(fuzzyness) and cont != ' ':
            mutable = 'true'
        else:
            mutable = 'false'
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
                cont = parse.unquote(cont)
                #check if there are non-printable characters
                escCont = ''.join(c for c in cont if c in string.printable)
                if not escCont == cont:
                    #handle 'em
                    #strip content to pure hex
                    #cont = handleControl(cont)
                    cont = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(cont))))))
                    data = ET.Element('Blob', name='c' + str(count),
                                      attrib={'value': cont, 'token': token, 'mutable': mutable, 'valueType': 'hex'})  #,'size':size})
            # else: put it in a string
            if data == '':
                # if cont.find('port=') != -1:
                #     token = 'false'
                #just a normal string, no non-printables detected
                if mutCount == 0 and advanced:
                    mutable = 'true'
                    mutCount = -1
                data = ET.Element('String', name='c' + str(count), attrib={'value': cont, 'token': token, 'mutable': mutable})
                if ':' in cont:
                    mutCount = 2
        else:
            # rule field (defaultValue: good question)
            # ToDo consider thinking of better defaultValue
            value = '1337133811'
            if blob:
                value = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(value))))))
                data = ET.Element('Blob', name='c' + str(count), attrib={'value': value, 'token': 'false',
                                                                         'mutable': 'true', 'valueType': 'hex'})
            else:
                data = ET.Element('String', name='c' + str(count), attrib={'value': value, 'token': 'false',
                                                                           'mutable': 'true'})
        dataModel.append(data)
        count += 1
    # ToDo: check that
    # make sure last field contents twice /r/n
    if count != 0:
        if cont == '':
            if dataModel[-1].attrib['value'] == '':
                if dataModel[-2].attrib['value'] == '':
                    dataModel = dataModel[:-1]
                dataModel[-1].set('value', '\r\n\r\n')
                dataModel[-1].set('token', 'true')
    return templates[ID].isServer()


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


def dataModel(templates, horizon, fuzzyness, blob=False, advanced=False, role=True):
    pit = PIT()
    root = pit.tree.getroot()

    # create random dataModel
    dataModel = ET.Element('DataModel', name='rand')
    dataModel.append(ET.Element('String', name='a', attrib={'value': 'randomNumber: ', 'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='a1', attrib={'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='c', attrib={'value': '\n', 'mutable': 'false'}))
    root.append(dataModel)

    # create randomChange dataModel
    dataModel = ET.Element('DataModel', name='randChange')
    dataModel.append(ET.Element('String', name='a', attrib={'value': 'randomChange: ', 'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='a1', attrib={'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='c', attrib={'value': '\n\n', 'mutable': 'false'}))
    root.append(dataModel)

    # create model for outputting state name
    dataModel = ET.Element('DataModel', name='enterState')
    dataModel.append(ET.Element('String', name='a', attrib={'value': '===== entering: ', 'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='a1', attrib={'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='c', attrib={'value': ' ===== \n', 'mutable': 'false'}))
    root.append(dataModel)

    # create history dataModel
    histModel = createHistModel(horizon)
    root.append(histModel)

    # unknown dataModel
    dataModel = ET.Element('DataModel', name='MissingNo')
    dataModel.append(ET.Element('String', name='no', attrib={'mutable': 'false', 'value': '', 'token': 'false'}))
    root.append(dataModel)

    # empty dataModel
    dataModel = ET.Element('DataModel', name='MissingMo')
    root.append(dataModel)

    for ID in templates.keys():
        dataModel = ET.Element('DataModel', name='{}'.format(str(ID)))
        isServer = createContent(ID, dataModel, templates, fuzzyness, blob, advanced)
        if not role:
            isServer = not isServer
        root.append(dataModel)
        # create specific derivatives of dataModel
        if isServer:
            # print('dmlen{}= '.format(ID), len(dataModel.getchildren()))
            length[ID] = len(dataModel.getchildren())
            dataModelSpec = dataModel.__copy__()
            createSpecific(dataModelSpec)
            root.append(dataModelSpec)
    return pit


def createSpecific(dataModel):
    dataModel.set('name', '{}{}'.format(dataModel.attrib['name'], 'spec'))
    flag = 0
    for child in dataModel.getchildren():
        if flag == 1:
            flag = 0
            continue
        if child.attrib['token'] == 'true':
            child.attrib['token'] = 'false'
        else:
            child.attrib['token'] = 'true'

        if child.attrib['value'] == '':
            child.attrib['token'] = 'false'
            if child.getprevious() is not None:
                child.getprevious().attrib['token'] = 'true'
                flag = 1
    return


def createHistModel(horizon):
    dataModel = ET.Element('DataModel', name='hist')
    for i in range(horizon):
        # dataModel.append(ET.Element('String', name='message{}'.format(horizon-i), attrib={'mutable': 'false', 'value': '-11'}))
        dataModel.append(ET.Element('String', name='ID-{}'.format(horizon-i+1), attrib={'mutable': 'false', 'value': '-1'}))
        # horizon -= 1
    dataModel.append(ET.Element('String', name='theEnd', attrib={'mutable': 'false', 'value': '\n\n'}))
    return dataModel


def createMultiModel(dataModelID):
    multiModel = ET.Element('DataModel', name=str(dataModelID))
    choice = ET.Element('Choice', name='c', attrib={'minOccurs': '1', 'maxOccurs': '1'})
    IDs = order4Length(dataModelID.split('and'))
    if len(IDs) < 2:
        multiModel.set('name', '{}mult'.format(dataModelID))
    for dataModel in IDs:
        choice.append(
            ET.Element('Block', name='o{}spec'.format(str(dataModel)), attrib={'ref': '{}spec'.format(str(dataModel))}))
        choice.append(
            ET.Element('Block', name='o{}'.format(str(dataModel)), attrib={'ref': '{}'.format(str(dataModel))}))
        multiModel.append(choice)
    # provide 'unknown' template to let communication go on
    choice.append(ET.Element('Block', name='unknown', attrib={'ref': 'MissingNo'}))
    choice.append(ET.Element('Block', name='None', attrib={'ref': 'MissingMo'}))
    return multiModel


def order4Length(list):
    l = []
    ordered = []
    for item in list:
        if item != '"':
            l.append(length[int(item)])
    while list != []:
        ind = l.index(min(l))
        ordered.append(list.pop(ind))
        l.pop(ind)
    return ordered


def modelName(modelIDs):
    modelName = ''
    for IDs in modelIDs:
        modelName += '{}and'.format(IDs)
    return modelName[:-3]


def stateModel(dataPit, done, horizon, templatesID2stateName, DEBUG=False, blob=False):
    pit = PIT()
    pit.tree.getroot().append(ET.Element('StateModel', name='StateModel'))
    stateModel = pit.tree.getroot().find('StateModel')
    multiModels = {}
    dataRuleModels = {}
    global tempID2StateMap
    tempID2StateMap = templatesID2stateName
    for listOstates in done.values():
        for state in listOstates:
            actionCounter = 0
            state.name = encodeState(state, DEBUG)
            stateName = encodeState(state, DEBUG)
            if state.isInit == True:
                stateModel.attrib.update({'initialState': stateName})
            peachState = ET.Element('State', name=stateName)

            # tell us where we are
            # ToDo: DEBUG only
            current = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT', 'onStart':
                'additionalCode.name(self)'})
            current.append(ET.Element('DataModel', attrib={'ref': 'enterState'}))
            peachState.append(current)
            actionCounter += 1

            # install hist dataModel
            histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT', 'name': 'theHist'})
            histAction.append(ET.Element('DataModel', attrib={'ref': 'hist', 'name': 'hist'}))
            peachState.append(histAction)
            actionCounter += 1

            # handle ioActions
            if state.ioAction != 'END':
                # dataModelIDs = state.nextHist.getID()
                dataModelIDs = state.templates
                # dataModelIDs = state.nextHist.theHist[-1]
            if state.ioAction == 'input' and state.templates:
                histActionNumber = actionCounter
                name = modelName(dataModelIDs)
                # if len(dataModelIDs) > 1 and tuple(dataModelIDs) not in multiModels.keys():
                if tuple(dataModelIDs) not in multiModels.keys():
                    multiModels.update({tuple(dataModelIDs): createMultiModel(name)})
                inputAction = ET.Element('Action', name='in', attrib={'type': 'input'})
                if len(dataModelIDs) <= 1:
                    inputAction.append(ET.Element('DataModel', name='read', attrib={'ref': '{}mult'.format(name)}))
                else:
                    inputAction.append(ET.Element('DataModel', name='read', attrib={'ref': name}))
                inputAction.set('onComplete', 'additionalCode.updateHist(self,{})'.format('in'))
                peachState.append(inputAction)
                actionCounter += 1
            elif state.ioAction == 'output':
                # have multiple output options
                count = 0
                hasOpts = False
                # install random generator for multi-output
                if len(dataModelIDs) > 1:
                    outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randOut',
                                                                'onStart': 'additionalCode.rand(self,{})'.format(
                                                                    len(dataModelIDs) - 1), 'publisher': 'nullOUT'})
                    outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                    peachState.append(outputAction)
                    count = len(dataModelIDs) - 1
                    hasOpts = True
                    actionCounter += 1

                # deal with DataRules
                if state.dataRules != []:
                    # dataModels, slurps = data(state, dataRuleModels, done, DEBUG, blob)
                    dataModels, slurps = data(state, dataRuleModels, done, DEBUG, blob)

                    # install dataRule output models
                    # for model in dataModelsNslurps.keys():
                    for model in dataModels:
                        # modID = int(model.attrib['name'].split()[0].split(';')[-1][1:-1])
                        modID = getHist(model, horizon)
                        when = computeWhenOut(state, modID[0])
                        peachState.append(ET.Comment('dataRuleModel {}'.format(model.attrib['name'])))
                        dataAction = ET.Element('Action', attrib={'type': 'output', 'name': '{}'.format(
                            model.attrib['name']), 'publisher': 'null', 'when': when})
                        dataAction.append(ET.Element('DataModel',
                                                     attrib={'ref': '{}'.format(model.attrib['name']),
                                                             'name': '{}model'.format(model.attrib['name'])}))
                        peachState.append(dataAction)
                        actionCounter += 1

                    # slurp from those
                    for slurp in slurps:
                        # peachState.append(ET.Comment('dataSlurp {}'.format(ruleHist)))
                        peachState.append(slurp)
                        actionCounter += 1

                # # apply rules
                # # for ruleList in state.rules:
                # #     # rule = rule[0]
                for rule in state.rules:
                    peachState.append(ET.Comment('exact rule: {}'.format(rule)))
                    # slurp = craftSlurp(rule.ruleHist.theHist, rule.srcID, state, rule, done, DEBUG)
                    slurp = craftSlurp(state, rule, done, DEBUG)
                    peachState.append(slurp)
                #     cpy = slurp.__copy__()
                #     pimped = pimpMySlurp(cpy, rule.srcID, True)
                #     if rule.srcID == -1:
                #         peachState.append(slurp)
                #         actionCounter += 1
                #     else:
                #         for slurps in pimped:
                #             peachState.append(slurps)
                #             actionCounter += 1

                # # then apply advance copyRules
                # # for ruleList in state.copyRules:
                for rule in state.copyRules:
                    peachState.append(ET.Comment('{} rule: {}'.format(rule.typ.split('.')[-1], rule)))
                    slurp = craftSlurp(state, rule, done, DEBUG, ruleType='copy')
                    peachState.append(slurp)
                #     cpy = slurp.__copy__()
                #     if rule.srcID % 2 == 1:
                #         peachState.append(slurp)
                #         actionCounter += 1
                #     else:
                #         pimped = pimpMySlurp(cpy, rule.srcID, True)
                #         # if dunno:
                #         #     pimped = pimpMySlurp(cpy, rule.srcID, True)
                #         # else:
                #         #     pimped = pimpMySlurp(cpy, rule.srcID)
                #         for slurps in pimped:
                #             peachState.append(slurps)
                #             actionCounter += 1

                for ID in dataModelIDs:
                    outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'out{}'.format(ID)})
                    if count > 0:
                        # whenExpression = 'int(self.parent.actions["randOut"].dataModel["a1"].InternalValue) == int({})'.format(
                        whenExpression = 'int(State["randOut"].dataModel["a1"].InternalValue) == int({})'.format(
                            count)
                        outputAction.set('when', whenExpression)
                        outputAction.append(
                            ET.Element('DataModel', attrib={'ref': '{}'.format(ID), 'name': 'out{}'.format(ID)}))
                        count -= 1
                    else:
                        if hasOpts == False:
                            outputAction.append(ET.Element('DataModel', attrib={'ref': '{}'.format(ID),
                                                                                'name': 'out{}'.format(ID)}))
                        else:
                            whenExpression = 'int(State["randOut"].dataModel["a1"].InternalValue) == ' \
                                             'int({})'.format(count)
                            outputAction.set('when', whenExpression)
                            outputAction.append(ET.Element('DataModel', attrib={'ref': '{}'.format(ID),
                                                                                'name': 'out{}'.format(ID)}))
                    # apply dataRules
                    if state.dataRules != []:
                        pass
                        # dataElements = data(ID, state)
                        # outputAction.append(ET.Element('Data'))
                    outputAction.set('onComplete', 'additionalCode.updateHist(self,{})'.format(ID))
                    peachState.append(outputAction)
                    actionCounter += 1

            # # handle history update
            # histAction = updateHist(stateName, horizon)
            # for i in histAction:
            #     actionCounter += 1
            #     peachState.append(i)

            # handle changeStateActions
            count = 0
            if len(state.nextStates) > 1:
                count = len(state.nextStates) - 1
                outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randChange',
                                                            'onStart': 'additionalCode.rand(self,{})'.format(
                                                                len(state.nextStates) - 1), 'publisher': 'nullOUT'})
                outputAction.append(ET.Element('DataModel', attrib={'ref': 'randChange'}))
                peachState.append(outputAction)
            for nxt in state.nextStates:
                # stateRef = '{} {}'.format(state.nextHist, nxt)
                stateRef = '{}'.format(nxt)
                if not DEBUG:
                    stateRef = str(base64.b64encode(stateRef.encode('ascii')))[2:-1].replace('=', '')
                if count > 0:
                    # whenExpression = 'int(self.parent.actions["randChange"].dataModel["a1"].InternalValue) ==' \
                    whenExpression = 'int(State["randChange"].dataModel["a1"].InternalValue) ==' \
                                             ' int({})'.format(count)
                    # whenExpression = 'int(self.parent.actions[{0}].dataModel["a1"].InternalValue) == int({1})'.format(
                    #     actionCounter, count)
                    changeAction = ET.Element('Action',
                                              attrib={'type': 'changeState', 'ref': stateRef, 'when': whenExpression})
                    count -= 1
                else:
                    changeAction = ET.Element('Action', attrib={'type': 'changeState', 'ref': stateRef})
                # toDo: make function of this mess
                #       for more than 2-horizon
                peachState.append(ET.Comment('manipulate hist here for nextState {}'.format(nxt)))
                peachState.append(ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-2'.format(state),
                                                               'setXpath': '//StateModel//{}//theHist//hist//ID-3'.format(nxt)}))
                # crazy idea here: oldest message ID not needed any more. so eventually put in the emitted message ID
                # of this very state and slurp it to the most recent message ID of the nextState's history model!
                peachState.append(ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-3'.format(state),
                                                               'setXpath': '//StateModel//{}//theHist//hist//ID-2'.format(nxt)}))
                if 'when' in changeAction.attrib.keys():
                    peachState.append(ET.Comment('{}'.format(changeAction.attrib['when'])))
                peachState.append(changeAction)
            stateModel.append(peachState)
        #stateModel.append(peachState)
    dataPitRoot = dataPit.tree.getroot()
    # append multi models
    for ID in multiModels.values():
        dataPitRoot.append(ID)
    # append dataRule models
    for model in dataRuleModels.values():
        dataPitRoot.append(model)
    dataPitRoot.append(pit.tree.getroot().find('StateModel'))
    return dataPit


def craftSlurp(state, rule, done, DEBUG, ruleType=None):
    encState = encodeState(state, DEBUG)
    ID = rule.ruleHist.getID()[0]
    srcID = rule.ruleHist.getID(rule.srcID)[0]
    srcState = done['|'.join(tempID2StateMap[srcID].hist)][0]
    absoluteDstField = computeAbsoluteFields(state, ID, rule.dstField)
    absoluteSrcField = computeAbsoluteFields(srcState, srcID, rule.srcField)
    setXpath = '//StateModel//{}//out{}//out{}//c{}'.format(encState, ID, ID, absoluteDstField)
    valueXpath = '//StateModel//{0}//{1}//c{2}'.format(encodeState(srcState,DEBUG), srcID, absoluteSrcField)
    slurp = ET.Element('Action', attrib={'type': 'slurp', 'onComplete': 'additionalCode.dataRule(self)',
                                         'valueXpath': valueXpath, 'setXpath': setXpath})

    # check if correct model is output in this state
    correctModel = computeWhenOut(state, ID, DEBUG)
    # if '1 == 1' in correctModel:
    #     j = -1
    # else:
    #     j = correctModel.split('int(')[-1][:-1]

    correctHist = whenHist(rule.ruleHist, state)

    # check if correct models have been output in preStates
    # do so by just looking it up in the states own hist model
    when = correctModel + ' and ' + correctHist
    slurp.set('when', when)
    if ruleType:
        onComp = assembleCopyRules(rule)
        slurp.set('onComplete', onComp)
    return slurp


def getHist(PeachModel, depth):
    modID = []
    while depth >= 0:
        modID.append(int(PeachModel.attrib['name'].split()[0].split(';')[depth][1:-1]))
        depth -= 1
    return modID


def data(state, dataRuleModels, done, DEBUG=False, blob=False):
    models = []
    slurps = []
    # for ruleList in state.dataRules:
    curHist = state.dataRules[0].ruleHist
    models.append(createDataRuleModel(state, state.dataRules[0].ruleHist, DEBUG))
    for rule in state.dataRules:
        if rule.ruleHist != curHist:
            models.append(createDataRuleModel(state, rule.ruleHist, DEBUG))
        curHist = rule.ruleHist
        # print(rule.ruleHist, rule.dstField, computeAbsoluteFields(state, rule.ruleHist.getID()[0], rule.dstField), rule.data)
        # there seem to be problems with to large strings in PEACH
        # going to pick subset of possible data
        # trying to order it and pick first 5 elements
        dataElements = list(set(rule.data))
        # dataElements.sort() [:min(5, len(dataElements))]
        cont = ';;;'.join(dataElements)
        if blob:
            cont = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(cont))))))
            models[-1].append(ET.Element('Blob', attrib={'mutable': 'false', 'valueType': 'hex'}, name='c{}'.format(computeAbsoluteFields(
                state, rule.ruleHist.getID()[0], rule.dstField)), value='{}'.format(cont)))
        else:
            models[-1].append(ET.Element('String', attrib={'mutable': 'false'}, name='c{}'.format(computeAbsoluteFields(
                state, rule.ruleHist.getID()[0], rule.dstField)), value='{}'.format(cont)))
        # 'AAAAAAAAAAAAAAAAAAAAAAAAAAA;;;BBBBBBBBBBBBBBBBBBBBBBBBBBBBB;;;CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'
        slurps.append(dataSlurp(state, rule, models[-1].attrib['name'], done, DEBUG))

    for model in models:
        if model.attrib['name'] not in dataRuleModels.keys():
            dataRuleModels.update({model.attrib['name']: model})

    return models, slurps

def createDataRuleModel(state, hist, DEBUG=False):
    modelName = '{} {}'.format(hist, state.curState)
    if not DEBUG:
        modelName = str(base64.b64encode('{} {}'.format(hist, state.curState).encode('ascii')))[2:-1].replace('=', '')
    drModel = ET.Element('DataModel', name=str(modelName))
    # choice.append(ET.Element('Block', name='unknown', attrib={'ref': 'MissingNo'}))
    return drModel

def pimpMySlurp(slurp, srcID, hardcore=False):
    whens = slurp.attrib['when'].split(' and ')
    sourceState = slurp.attrib['valueXpath'].split('//')[2]

    for part in whens:
        if sourceState in part:
            if '"in"' in part:
                parts = part.split(' or ')
                parts[0] = parts[0][1:]
                parts[1] = parts[1][:-1]
                ind = whens.index(part)
                whens[ind] = parts[0]
                # whenSpec = whens[0] + ' and ' + parts[0]
                whenSpec = ' and '.join(whens)
                whens[ind] = parts[1]
                # when = whens[0] + ' and ' + parts[1]
                when = ' and '.join(whens)
                specSlurp = slurp.__copy__()
                specVXP = specSlurp.attrib['valueXpath'].split('//')
                specVXP[5] = specVXP[5]+'spec'
                specVXP = '//'.join(specVXP)
                specSlurp.set('valueXpath', specVXP)
                specSlurp.set('when', whenSpec)
                slurp.set('when', when)
                return [slurp, specSlurp]

    return [slurp]

def pimpMySlurpOLD(slurp, srcID, hardcore=False):
    if srcID == -1:
        return []
    # cut it in pieces
    s = slurp.attrib['when'].split(' and ')
    c = "c{}".format(-(srcID+1))
    # identify piece to be pimped
    # ToDo: messed it up, need to rethink; works for Horizon of length 3
    for i in s:
        if ' or ' in i:
            ind = s.index(i)
            break
        # if c in i:
        #     ind = s.index(i)+1
        #     break
    repl = s[ind].split(' or ')
    if len(repl) <= 1:
        return [slurp]
    repl[0] = repl[0][1:]
    repl[-1] = repl[-1][:-1]
    # re-glue the pieces
    pimped = []
    for r in repl:
        # if hardcore:
        #     r = r[1:-1]
        when = s[:ind]+[r]+s[ind + 1:]
        when = ' and '.join(when)
        cpy = slurp.__copy__()
        cpy.set('when', when)
        if 'spec' in r:
            # print(dir(cpy))
            unspec = cpy.attrib['valueXpath'].split('//')
            if 'out' in unspec[-2]:
                continue
            spec = unspec[-2]+'spec'
            cpy.set('valueXpath', '//'.join(unspec[:-2]+[spec]+[unspec[-1]]))
        pimped.append(cpy)
    return pimped


def updateHist(stateName, horizon):
    update = []
    histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null',
                                              'onStart': 'additionalCode.updateHist(self)'})
    histAction.append(ET.Element('DataModel', attrib={'ref': 'hist', 'name': '{}Hist'.format(stateName)}))
    update.append(histAction)
    assert horizon > 1
    while horizon != 1:
        slurpAction = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//{0}//theHist//c{1}'.format(
            stateName, horizon - 1), 'setXpath': '//StateModel//hist//c{}'.format(horizon)})
        update.append(slurpAction)
        horizon -= 1
    slurpAction = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//{}//{}Hist//c1'.format(
        stateName, stateName), 'setXpath': '//StateModel//hist//c1'})
    update.append(slurpAction)
    return update


def assembleCopyRules(rule):
    call = 'additionalCode.'
    if 'Complete' in rule.typ:
        s = ''
        for cont in set(rule.content):
            s += (cont + ';;;')
        s = s[:-3]
        return "{}copyComp(self,'{}','{}')".format(call, rule.ptype, s)
    if 'Partial' in rule.typ:
        # rule.cont here is separator
        return "{}copyPart(self,'{}','{}')".format(call, rule.ptype, rule.content)
    if 'Seq' in rule.typ:
        return "{}copySeq(self,{})".format(call, rule.content)


# def bound(data, points):
#     ret_data = []
#     for i in range(points):
#         j = random.randint(0, len(data) - 1)
#         ret_data.append(data[j])
#     return ret_data


# def cross(data, depth=0):
#     #print('\nInto cross lvl{}'.format(depth,),'\n',data)
#     tup = []
#     if len(data) == 1:
#         #print('internal: ',data)
#         for r in data[0]:
#             tup.append([r])
#         return tup
#     dat = data[0]
#     ret = cross(data[1:], depth + 1)
#     #print(ret)
#     #ret = ret[0]#cross(data[1:],depth+1)[0]
#     #print('dat: ',dat)
#     #print('Receiving ret on lvl{}: '.format(depth),ret)
#     for d in dat:
#         for r in ret:
#             #print('internal: ',d,r)
#             tup.append([d] + r)
#     return tup
#     #return data

def encodeState(state, DEBUG=False):
    if DEBUG:
        return '{}'.format(state.curState)
    return str(base64.b64encode('{}'.format(state.curState).encode('ascii')))[2:-1].replace('=', '')


def recursiveSlurp(histList, srcID, state, rule, done, DEBUG=False, count=0, ruleType = 'rules'):
    if histList == []:
        return '', ''
    encState = encodeState(state, DEBUG)
    myValueXpath = ''
    if srcID == -1:
        ID = rule.ruleHist.getID(rule.srcID)[0]
        absoluteSrcField = computeAbsoluteFields(state, ID, rule.srcField)
        if state.ioAction == 'input':
            if not state.isMulti():
                # actually does not appear
                # now really can't happen
                myValueXpath = '//StateModel//{0}//in//c{1}'.format(encState, absoluteSrcField)
            else:
                myValueXpath = '//StateModel//{0}//in//read//o{1}//c{2}'.format(encState, ID, absoluteSrcField)
                # myValueXpathSpec = '//StateModel//{0}//in//o{1}spec//c{2}'.format(encState, ID, absoluteSrcField)
        else:
            myValueXpath = '//StateModel//{0}//out{1}//out{2}//c{3}'.format(encState, ID, ID, absoluteSrcField)
    # compute correct when string here
    whenCorrectModel = computeWhenOut(state, histList[-1][0], DEBUG)
    # if count != 0:
    #     whenCorrectPreState = computeWhenHist(state, count, DEBUG)
    #     myWhen = '{1} and {0}'.format(whenCorrectModel, whenCorrectPreState)
    # else:
    #     myWhen = whenCorrectModel
    myWhen = whenCorrectModel
    # recall recursive
    preState = whosURdaddy(state, done)
    if len(preState) == 1:
        preState = preState[0]
    else:
        print('warning you')
    if preState:
        when, valueXpath = recursiveSlurp(histList[:-1], srcID + 1, preState, rule, done, DEBUG, count + 1, ruleType)
    else:
        return '{}'.format(myWhen), '{}'.format(myValueXpath)
    if count == 0:
        valueXpath = '{}{}'.format(valueXpath, myValueXpath)
        setXpath = '//StateModel//{}//out{}//out{}//c{}'.format(encState, rule.dstID[0], rule.dstID[0],
                                                                computeAbsoluteFields(state, rule.ruleHist.getID()[0],
                                                                                      rule.dstField))
        slurp = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': valueXpath, 'setXpath': setXpath})
        # when = '{} and {}'.format(when, myWhen)
        if '1 == 1' in myWhen:
            i = -1
        else:
            i = myWhen.split('int(')[-1][:-1]
        if when.startswith(' and '):
            when = when[5:]
        slurp.set('when', when)
        if ruleType == 'copy':
            call = assembleCopyRules(rule, i)
            slurp.set('onComplete', call)
        else:
            slurp.set('onComplete', 'additionalCode.randMan(self,"{}")'.format(i))
        return slurp
    return '{} and {}'.format(when, myWhen), '{}{}'.format(valueXpath, myValueXpath)


def dataSlurp(state, rule, modelName, done, DEBUG):
    # '{}model'.format(model.attrib['name'])
    encState = encodeState(state, DEBUG)
    ID = rule.ruleHist.getID()[0]
    absoluteDstField = computeAbsoluteFields(state, ID, rule.dstField)
    setXpath = '//StateModel//{}//out{}//out{}//c{}'.format(encState, ID, ID, absoluteDstField)
    valueXpath = '//StateModel//{0}//{1}//c{2}'.format(encState, modelName, absoluteDstField)
    slurp = ET.Element('Action', attrib={'type': 'slurp', 'onComplete': 'additionalCode.dataRule(self)',
                                         'valueXpath': valueXpath, 'setXpath': setXpath})

    # check if correct model is output in this state
    correctModel = computeWhenOut(state, ID, DEBUG)
    if '1 == 1' in correctModel:
        j = -1
    else:
        j = correctModel.split('int(')[-1][:-1]

    # obsolete since re-thinking
    # # check if we were in correct preStates
    # daddys = []
    # c = len(state.hist.theHist)
    # s = state
    # while c:
    #     # this should be unambiguous
    #     # if not ... flee in terror
    #     s = whosURdaddy(s, done)[0]
    #     if not s:
    #         break
    #     daddys.append(s)
    #     c -= 1
    # whenHist = ''
    # # for i in range(len(daddys)):
    # #     whenHist = '{} and {}'.format(whenHist, computeWhenHist(daddys[i], i+1, DEBUG))
    correctHist = ''
    correctHist = whenHist(rule.ruleHist, state)

    # check if correct models have been output in preStates
    # do so by just looking it up in the states own hist model
    when = correctModel + ' and ' + correctHist
    # for i in (range(len(daddys))):
    #     whenPreOut = '{} and {}'.format(whenPreOut, computeWhenOut(daddys[len(daddys)-i-1],
    #                                                                rule.ruleHist.theHist[i][0], DEBUG))
    # # slurp.set('when', '{}{}{}'.format(correctModel, whenHist, whenPreOut))
    # when = '{}{}'.format(whenHist, whenPreOut)
    # if when.startswith(' and '):
    #     when = when[5:]
    slurp.set('when', when)
    slurp.set('onComplete', 'additionalCode.dataRule(self,"{}")'.format(j))
    return slurp


def whenHist(hist, state):
    h = hist.length()
    s = ''
    while h > 1:
        s += 'int(StateModel.states["{}"]["theHist"].dataModel["ID-{}"].InternalValue) == int({})'.format(state, h, hist.getID(-h)[0])
        h -= 1
        s += ' and '
    return s[:-5]


def computeAbsoluteFields(state, templateID, relativeField):
    return state.fields[templateID][relativeField]


def computeWhenHist(state, age, DEBUG=False):
    # return 'str(self.parent.actions["theHist"].dataModel["c{}"].InternalValue) == str("{}")' \
    return 'str(State["theHist"].dataModel["c{}"].InternalValue) == str("{}")'\
        .format(age, encodeState(state, DEBUG))


def computeWhenOut(state, tempID, DEBUG=False):
    if state.ioAction == 'output':
        if state.isMulti():
            return 'int(StateModel.states["{}"]["randOut"].dataModel["a1"].InternalValue) == int({})'\
                .format(encodeState(state, DEBUG), len(state.templates) - 1 - state.templates.index(tempID))
        else:
            # the state then has only one model that could have been sent
            return '1 == 1'
    else:  # state is input
        if state.isMulti():
            spec = 'str(StateModel.states["{}"]["in"].dataModel[0][0][0].referenceName) == str("{}spec")' \
                .format(encodeState(state, DEBUG), tempID)
            unspec = 'str(StateModel.states["{}"]["in"].dataModel[0][0][0].referenceName) == str("{}")'\
                .format(encodeState(state, DEBUG), tempID)
            return '({} or {})'.format(spec, unspec)
        else:  # the state then has only one model that could have been received
            return '1 == 1'


def whosURdaddy(state, done):
    if state.getCurState() == 'START':
        return [None]
    preState = done[state.preHist]
    preState = [ps for ps in preState if ps.nextHist == state.hist]
    return preState


def match(state, ruleList):
    retList = []
    for rule in ruleList:
        if rule.ruleHist.getID()[0] in state.templates:
            retList.append(rule)
    return retList


def stateAssembler(state, container, model, templates, rules, copyRules, dataRules, UAC=True):
    #fetch ioAction
    if (UAC and 'UAC' in state.getCurState()) or (not UAC and 'UAC' not in state.getCurState()):
        state.ioAction = 'output'
    else:
        state.ioAction = 'input'

    if 'END' == state.getCurState():
        state.ioAction = 'END'

    # fetch emittable Template IDs
    # compute hist of nextStates
    if state.curState in templates.stateToID.keys():
        # state.templates = templates.stateToID[state.curState][:]
        temps = copy.deepcopy(templates.stateToID[state.curState])
        for tempID in temps[:]:
            # if template has no content: remove it
            if not templates.IDtoTemp[tempID].content:
                temps.remove(tempID)
        state.templates = temps
        # if no templates left, there is no nextState to reach
        # if not temps:
        #     checkParent(state, container)
        #     # state.nextStates = []
        #     # state.ioAction = 'END'
        #     # appendTodo(container, state)
        #     return
        # state.nextHist = state.hist.update(state.templates)
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

    #ToDO: fetch rules
    # lenHist = len(state.hist.theHist)
    # possibleHists = state.hist.assembleHist(lenHist)
    # ruleIDs = []
    #normal rules
    for tempID in state.templates:
        if tempID in rules.keys():
            for r in rules[tempID]:
                state.rules.append(r)
    # for hist in possibleHists:
    #     if hist in rules.keys():
    #         rule = match(state, rules[hist])
    #         if rule:
    #             for r in rule:
    #                 ruleIDs.append(r.ruleHist.getID())
    #             state.rules.append(rule)
    # #data rules
    for tempID in state.templates:
        if tempID in dataRules.keys():
            for r in dataRules[tempID]:
                state.dataRules.append(r)
    # for hist in possibleHists:
    #     if hist in dataRules.keys():
    #         rule = match(state, dataRules[hist])
    #         if rule:
    #             for r in rule:
    #                 ruleIDs.append(r.ruleHist.getID())
    #             state.dataRules.append(rule)
    # #copy rules
    for tempID in state.templates:
        if tempID in copyRules.keys():
            for r in copyRules[tempID]:
                state.copyRules.append(r)
    # for hist in possibleHists:
    #     if hist in copyRules.keys():
    #         rule = match(state, copyRules[hist])
    #         if rule:
    #             for r in rule:
    #                 ruleIDs.append(r.ruleHist.getID())
    #             state.copyRules.append(rule)

    # x = []
    # for sublist in ruleIDs:
    #     for ID in sublist:
    #         x.append(ID)
    # ruleIDs = set(x)

    # tmp = state.templates[:]

    # # remove templates with fields which cannot be filled in this context
    # for temp in state.templates[:]:
    #     if state.ioAction == 'output' and state.fields[temp]:
    #         if temp not in ruleIDs:
    #             state.templates.remove(temp)
    #             if not state.templates:
    #                 # having to remove this state completely
    #                 # need to remove the transition to this state in parent state
    #                 # if parent then has no more transitions: remove it, too
    #                 checkParent(state, container)
    #                 return

    # update nextStates hist
    # state.nextHist = state.hist.update(state.templates)

    #if state.hist in dataRules.keys():
    #    state.dataRules = dataRules[state.hist]
    #if state.hist in copyRules.keys():
    #    state.copyRules = copyRules[state.hist]

    #print('=====DONESTATE=====', state,state.nextStates, state.isInit(),state.nextHist,'\n')
    appendTodo(container, state)
    return


def checkParent(state, container):
    parent = state.parent
    # state to be checked may be initial state
    if not parent:
        return
    parent.nextStates.remove(state.curState)
    if not parent.nextStates:
        container.donerem(parent)
        checkParent(parent, container)
    return


def appendTodo(container, state):
    if state.name in container.done.keys():
        # having state already -> do nothing
        PeachState = container.done[state.name][0]
        #    if ns not in PeachState.previous:
        #        PeachState.previous.append(ns)
        for prev in state.previous:
            PeachState.previous.append(prev)
        return
        # for stateDash in container.done[state.hist]:
        #     if state == stateDash:
        #         return
    container.doneadd(state)
    if state.nextStates != []:
        for nextState in state.nextStates:
            # nxt = PeachState(nextState, state.hist, state.nextHist, parent=state)
            nxt = PeachStateReloaded(nextState, parent=state)
            container.todoadd(nxt)
    return
