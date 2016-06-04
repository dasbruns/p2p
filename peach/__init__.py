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
# from .Prisma import manipulate

# dataModelID to dataModelLength dictionary
# insert empty template with length 0 manually
length = {"''": 0}
tempID2StateMap = []
blackList = {}
fieldsINblock = {}


def test(pit, role=False, IP='127.0.0.1', port=80):
    pit.tree.getroot().append(ET.Element('Test', name='Default'))
    test = pit.tree.find('Test')
    strategy = ET.Element('Strategy', attrib={'class': 'Random'})
    strategy.append(ET.Element('Param', name='SwitchCount', attrib={'value': '200'}))
    test.append(strategy)
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
    test.append(ET.Comment('set to "Console" for debugging'))
    test.append(ET.Element('Publisher', name='nullOUT', attrib={'class': 'Null'}))
    #append some kind of logger
    logger = ET.Element('Logger', attrib={'class': 'File'})
    logger.append(ET.Element('Param', name='Path', attrib={'value': 'logs'}))
    test.append(logger)
    return pit


def agent(pit, application, role, port=80):
    pit.tree.getroot().append(ET.Element('Agent', name='Local'))
    agent = pit.tree.find('Agent')
    if role:
        agent.append(ET.Element('Monitor', attrib={'class': 'LinuxCrashMonitor'}))
        monitor = ET.Element('Monitor', attrib={'class': 'Process'})
        monitor.append(ET.Element('Param', name='Executable', attrib={'value': '{}'.format(application)}))
        monitor.append(ET.Element('Param', name='FaultOnEarlyExit', attrib={'value': 'True'}))
        agent.append(monitor)
    monitor = ET.Element('Monitor', attrib={'class': 'Pcap'})
    monitor.append(ET.Element('Param', name='Device', attrib={'value': 'lo'}))
    monitor.append(ET.Element('Param', name='Filter', attrib={'value': 'port {}'.format(port)}))
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
                    cont = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(cont))))))
                    data = ET.Element('Blob', name='c' + str(count),
                                      attrib={'value': cont, 'token': token, 'mutable': mutable, 'valueType': 'hex'})  #,'size':size})
            # else: put it in a string
            if data == '':
                #just a normal string, no non-printables detected
                if mutCount == 0 and advanced:
                    # use this to fuzz structs like key : value
                    # assumed that key, :, and value are each their own field in datamodel
                    # mutable = 'true'
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


def dataModel(templates, horizon, fuzzyness, blob=False, advanced=False, role=True):
    pit = PIT()
    root = pit.tree.getroot()

    # create random dataModel
    dataModel = ET.Element('DataModel', name='rand')
    dataModel.append(ET.Element('String', name='a', attrib={'value': 'randomNumber: ', 'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='a1', attrib={'mutable': 'false', 'value': '-1'}))
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

    # create count dataModel
    dataModel = ET.Element('DataModel', name='count')
    dataModel.append(ET.Element('String', name='a', attrib={'value': '===== COUNT: ', 'mutable': 'false'}))
    count = ET.Element('String', name='count', attrib={'value': '0', 'mutable': 'false'})
    dataModel.append(count)
    dataModel.append(ET.Element('String', name='c', attrib={'value': ' ===== \n', 'mutable': 'false'}))
    root.append(dataModel)

    # create model for ending gracefully
    dataModel = ET.Element('DataModel', name='endState')
    dataModel.append(ET.Element('String', name='a', attrib={'value': '===== ENDING RUN =====\n', 'mutable': 'false'}))
    root.append(dataModel)

    # create history dataModel
    histModel = createHistModel(horizon)
    root.append(histModel)

    for ID in templates.keys():
        dataModel = ET.Element('DataModel', name='{}'.format(str(ID)))
        isServer = createContent(ID, dataModel, templates, fuzzyness, blob, advanced)
        if not role:
            isServer = not isServer
        getLengthRelation(dataModel)
        root.append(dataModel)
        # # create specific derivatives of dataModel
        if isServer:
            length[ID] = len(dataModel.getchildren())
    return pit


def getLengthRelation(dataModel):
    for child in dataModel.getchildren():
        if child.attrib['value'] == '\r\n\r\n':
            if child == dataModel.getchildren()[-1]:
                return
    global blackList
    global fieldsINblock
    flag = False
    for child in dataModel.getchildren():
        if child.attrib['value'] == 'Content-Length:':
            flag = True
            break
    if flag:
        # we assume the existence of fields carrying the length of some specific part of the current message
        # as PRISMA does not learn those, we are doing here some guessing
        # results show it might be okay..
        # this indeed is AirPLay specifc!
        target = child.getnext().getnext()
        name = target.attrib['name']
        ID = int(dataModel.attrib['name'])
        if target.tag == 'Blob':
            target.tag = 'String'
            if ID not in blackList.keys():
                blackList[ID] = []
            blackList[ID].append(int(name[1:]))
        for key in target.attrib.keys():
            target.attrib.pop(key)
        target.set('name', name)
        target.set('mutable', 'false')
        rel = ET.Element('Relation', attrib={'type': 'size', 'of': 'blockB', 'expressionGet': 'size'})
        target.append(rel)

        flag = False
        blockB = ET.Element('Block', name='blockB', mutable='false')
        for child in dataModel.getchildren():
            if 'value' in child.attrib.keys() and child.attrib['value'] == '\r\n\r\n':
                # use this to know if field is in blockB or not
                theCut = child.attrib['name']
                fieldsINblock[ID] = theCut
                flag = True
                continue
            if flag:
                blockB.append(child)
        dataModel.append(blockB)


def createHistModel(horizon):
    dataModel = ET.Element('DataModel', name='hist')
    dataModel.append(ET.Element('String', name='count', attrib={'value': '0', 'mutable': 'false'}))
    dataModel.append(ET.Element('String', name='newline', attrib={'value': '\n', 'mutable': 'false'}))
    for i in range(horizon):
        dataModel.append(ET.Element('String', name='ID-{}'.format(horizon-i+1), attrib={'mutable': 'false', 'value': '-1'}))
        dataModel.append(ET.Element('String', name='lb{}'.format(horizon-i+1), attrib={'mutable': 'false', 'value': '\n'}))
    dataModel.append(ET.Element('String', name='theEnd', attrib={'mutable': 'false', 'value': '\n'}))
    return dataModel


def createMultiModel(dataModelID):
    multiModel = ET.Element('DataModel', name=str(dataModelID))
    choice = ET.Element('Choice', name='c', attrib={'minOccurs': '1', 'maxOccurs': '1'})
    IDs = order4Length(dataModelID.split('and'))
    if len(IDs) < 2:
        multiModel.set('name', '{}mult'.format(dataModelID))
    for dataModel in IDs:
        choice.append(
            ET.Element('Block', name='o{}'.format(str(dataModel)), attrib={'ref': '{}'.format(str(dataModel))}))
        multiModel.append(choice)
    return multiModel


def order4Length(list):
    l = []
    ordered = []
    for item in list:
        if item != '"':
            l.append(length[int(item)])
    while list != []:
        # try to crack longer messages first
        ind = l.index(max(l))
        ordered.append(list.pop(ind))
        l.pop(ind)
    return ordered


def modelName(modelIDs):
    modelName = ''
    for IDs in modelIDs:
        modelName += '{}and'.format(IDs)
    return modelName[:-3]


def blackListed(state):
    # remove invalid Rules from state's rules
    global blackList
    for ID in state.templates:
        if ID in blackList.keys():
            for dr in state.dataRules:
                if dr.dstID[0] == ID:
                    if computeAbsoluteFields(state, ID, dr.dstField) == blackList[ID][0]:
                        state.dataRules.remove(dr)
            for cr in state.copyRules:
                if cr.dstID[0] == ID:
                    if computeAbsoluteFields(state, ID, cr.dstField) == blackList[ID][0]:
                        state.copyRules.remove(cr)
            for er in state.rules:
                if er.dstID[0] == ID:
                    if computeAbsoluteFields(state, ID, er.dstField) == blackList[ID][0]:
                        state.rules.remove(er)


def stateModel(dataPit, done, horizon, templatesID2stateName, DEBUG=False, blob=False):
    pit = PIT()
    pit.tree.getroot().append(ET.Element('StateModel', name='StateModel'))
    stateModel = pit.tree.getroot().find('StateModel')
    multiModels = {}
    dataRuleModels = {}
    global tempID2StateMap
    tempID2StateMap = templatesID2stateName
    # create dedicated exit state
    # give it action to reset count model
    pexit = ET.Element('State', name="exit")
    reset = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT'})
    reset.append(ET.Element('DataModel', attrib={'ref': 'count'}))
    pexit.append(reset)
    stateModel.append(pexit)
    for listOstates in done.values():
        for state in listOstates:
            blackListed(state)
            actionCounter = 0
            state.name = encodeState(state, DEBUG)
            stateName = encodeState(state, DEBUG)
            if state.isInit():
                stateModel.attrib.update({'initialState': stateName})
            peachState = ET.Element('State', name=stateName)

            # tell us where we are
            # ToDo: DEBUG only
            current = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT', 'onStart':
                'Prisma.name(self)'})
            if state.isInit():
                current.attrib['onStart'] = 'Prisma.start(self)'
                # current = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT', 'onStart':
                #     'Prisma.name(self)', 'onComplete': 'Prisma.start(self)'})
            current.append(ET.Element('DataModel', attrib={'ref': 'enterState'}))
            peachState.append(current)
            actionCounter += 1

            # install hist dataModel
            histAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT', 'name': 'theHist',
                                                      'onComplete': 'Prisma.set(self)'})
            histAction.append(ET.Element('DataModel', attrib={'ref': 'hist', 'name': 'hist'}))
            peachState.append(histAction)
            actionCounter += 1

            # ToDo parameterize this
            messageMAX = 50
            peachState.append(ET.Comment('max {} messages exchanged per session'.format(messageMAX)))
            current = ET.Element('Action', attrib={'type': 'changeState', 'when': 'int(State["theHist"].dataModel["count"].InternalValue) == int({})'.format(messageMAX), 'ref': 'exit'})
            peachState.append(current)
            actionCounter += 1

            noHist = False

            if state.ioAction == 'END':
                # tell us the end
                # ToDo: DEBUG only
                end = ET.Element('Action', attrib={'type': 'output', 'publisher': 'nullOUT',
                                                   'onComplete': 'Prisma.end(self)'})
                end .append(ET.Element('DataModel', attrib={'ref': 'endState'}))
                peachState.append(end )

            # handle ioActions
            if state.ioAction != 'END':
                # dataModelIDs = state.nextHist.getID()
                dataModelIDs = state.templates
                # dataModelIDs = state.nextHist.theHist[-1]
            if state.ioAction == 'input' and state.templates:
                for ID in dataModelIDs:
                    if length[ID] == 0:
                        dataModelIDs.remove(ID)
                if not dataModelIDs:
                    #clever flag
                    noHist = True
                else:
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
                    inputAction.set('onComplete', 'Prisma.updateHist(self)')
                    peachState.append(inputAction)
                    actionCounter += 1
            elif state.ioAction == 'output':
                # find out:
                #   does state have more than one model
                #   does it possess models with fields
                #   does it posses models without fields
                #   if so write down all models WITHOUT fields in random
                noFields = []
                hasFields = False
                for id in dataModelIDs:
                    if id in state.fields.keys():
                        if state.fields[id] == []:
                            # noFields.append(str(id))
                            noFields.append(str(len(dataModelIDs) -1 - dataModelIDs.index(id)))
                        else:
                            hasFields = True
                if hasFields and noFields:
                    s = ';;;'.join(noFields)
                    current.attrib['onComplete'] = 'Prisma.fallback(self, "{}")'.format(s)
                # have multiple output options
                hasOpts = False
                count = 0
                seenHists = []
                # install random generator for multi-output
                # if len(dataModelIDs) > 1:
                #     # outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randOut',
                #     #                                             'onStart': 'Prisma.rand(self,{})'.format(
                #     #                                                 len(dataModelIDs) - 1), 'publisher': 'nullOUT'})
                #     outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randOut'})
                #     outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                #     peachState.append(outputAction)
                #     count = len(dataModelIDs) - 1
                #     hasOpts = True
                #     actionCounter += 1

                # deal with DataRules
                if state.dataRules != []:
                    # dataModels, slurps = data(state, dataRuleModels, done, DEBUG, blob)
                    dataModels, slurps = data(state, dataRuleModels, done, DEBUG, blob)

                    # install dataRuState = ET.Element('State'le output models
                    for model in dataModels:
                        # modID = int(model.attrib['name'].split()[0].split(';')[-1][1:-1])
                        modID = getHist(model, horizon)
                        if not DEBUG:
                            model.attrib['name'] = str(base64.b64encode((model.attrib['name']).encode('ascii')))[2:-1].replace('=', '')
                        # when = computeWhenOut(state, modID[0])
                        peachState.append(ET.Comment('dataRuleModel {}'.format(model.attrib['name'])))
                        dataAction = ET.Element('Action', attrib={'type': 'output', 'name': '{}'.format(
                            model.attrib['name']), 'publisher': 'null'})  # , 'when': when})
                        dataAction.append(ET.Element('DataModel',
                                                     attrib={'ref': '{}'.format(model.attrib['name']),
                                                             'name': '{}model'.format(model.attrib['name'])}))
                        peachState.append(dataAction)
                        actionCounter += 1

                    # slurp from those
                    for slurp in slurps:
                        # peachState.append(ET.Comment('dataSlurp {}'.format(ruleHist)))
                        slurp.attrib['name'] = 'DataRule'
                        peachState.append(slurp)
                        actionCounter += 1

                # # apply rules
                # # for ruleList in state.rules:
                # #     # rule = rule[0]
                for rule in state.rules:
                    peachState.append(ET.Comment('exact rule: {}'.format(rule)))
                    # slurp = craftSlurp(rule.ruleHist.theHist, rule.srcID, state, rule, done, DEBUG)
                    slurp = craftSlurp(state, rule, done, DEBUG)
                    slurp.attrib['name'] = 'ExactRule'
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
                    slurp.attrib['name'] = rule.typ.split('.')[-1]
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

                # install random generator for multi-output
                if len(dataModelIDs) > 1:
                    # crazy idea

                    modelsWithFields = set(state.fields.keys())
                    modelswithoutFields = list(set(dataModelIDs) - modelsWithFields)
                    if modelswithoutFields:
                        modelswithoutFields = ';'.join(modelswithoutFields)
                        outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'fallback', 'publisher': 'nullOUT', 'onStart': 'acdditionalCode.set(self,{})'.format(modelswithoutFields)})
                        outputAction.append(ET.Element('DataModel', attrib={'ref': 'fallback'}))
                        peachState.append(outputAction)

                    outputAction = ET.Element('Action', attrib={'type': 'output', 'name': 'randOut', 'publisher': 'nullOUT', 'onStart': 'Prisma.choose(self, {})'.format(len(dataModelIDs)-1)})
                    outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                    peachState.append(outputAction)
                    count = len(dataModelIDs) - 1
                    hasOpts = True
                    actionCounter += 1

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
                    # apply dataRuleState = ET.Element('State's
                    if state.dataRules != []:
                        pass
                        # dataElements = data(ID, state)
                        # outputAction.append(ET.Element('Data'))
                    outputAction.set('onComplete', 'Prisma.updateHist(self,{})'.format(ID))
                    peachState.append(outputAction)
                    actionCounter += 1

                if hasOpts:
                    outputAction = ET.Element('Action', attrib={'type': 'output', 'publisher': 'null', 'name': 'randOutReset', 'onComplete': 'Prisma.randMan(self)'})
                    outputAction.append(ET.Element('DataModel', attrib={'ref': 'rand'}))
                    peachState.append(outputAction)
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
                                                            'onStart': 'Prisma.randChange(self,{})'.format(
                                                                len(state.nextStates) - 1), 'publisher': 'nullOUT'})
                outputAction.append(ET.Element('DataModel', attrib={'ref': 'randChange'}))
                peachState.append(outputAction)
            nxtwhen = ''
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
                    nxtwhen = whenExpression
                else:
                    changeAction = ET.Element('Action', attrib={'type': 'changeState', 'ref': stateRef})
                    nxtwhen = ''
                # made function of this mess
                # for more than 2-horizon
                if not noHist:
                    peachState.append(ET.Comment('manipulate hist here for nextState {}'.format(nxt)))
                    nxtName = nxt
                    if not DEBUG:
                        nxtName = str(base64.b64encode(str(nxt).encode('ascii')))[2:-1].replace('=', '')
                    # if not nxtwhen:
                    for hor in reversed(range(2, horizon+1)):
                        tFA = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-{}'.format(encodeState(state, DEBUG), hor),
                                                                       'setXpath': '//StateModel//{}//theHist//hist//ID-{}'.format(nxtName, hor+1)})
                        if nxtwhen:
                            tFA.set('when', nxtwhen)
                        peachState.append(tFA)
                    # crazy idea here: oldest message ID not needed any more. so eventually put in the emitted message ID
                    # of this very state and slurp it to the most recent message ID of the nextState's history model!
                    tFA = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-{}'.format(encodeState(state, DEBUG), horizon+1),
                                                                   'setXpath': '//StateModel//{}//theHist//hist//ID-2'.format(nxtName)})
                    if nxtwhen:
                        tFA.set('when', nxtwhen)
                    peachState.append(tFA)
                    # else:
                    #     peachState.append(ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-2'.format(encodeState(state, DEBUG)),
                    #                                                    'setXpath': '//StateModel//{}//theHist//hist//ID-3'.format(nxtName), 'when': whenExpression}))
                    #     # crazy idea here: oldest message ID not needed any more. so eventually put in the emitted message ID
                    #     # of this very state and slurp it to the most recent message ID of the nextState's history model!
                    #     peachState.append(ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': '//StateModel//{}//theHist//hist//ID-3'.format(encodeState(state, DEBUG)),
                    #                                                    'setXpath': '//StateModel//{}//theHist//hist//ID-2'.format(nxtName), 'when': whenExpression}))
                if 'when' in changeAction.attrib.keys():
                    peachState.append(ET.Comment('MULTI'))
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
    if srcState.ioAction == 'output':
        valueXpath = '//StateModel//{0}//out{1}//out{1}//c{2}'.format(encodeState(srcState, DEBUG), srcID, absoluteSrcField)
    elif srcState.ioAction == 'input':
        valueXpath = '//StateModel//{0}//in//read//c{2}'.format(encodeState(srcState, DEBUG), srcID, absoluteSrcField)
    else:
        print('something terribly wrong in peach/__init__.py/craftSlurp')
        exit()
    slurp = ET.Element('Action', attrib={'type': 'slurp', 'valueXpath': valueXpath, 'setXpath': setXpath})

    # check if correct model is output in this state
    if len(state.templates) > 1:
        correctModel = computeWhenOut(state, ID, DEBUG)
        onStart = int(correctModel.split('==')[1].split('int(')[1][:-1])
        slurp.set('onStart', 'Prisma.randMan(self,"{}")'.format(onStart))
    # if '1 == 1' in correctModel:
    #     j = -1
    # else:
    #     j = correctModel.split('int(')[-1][:-1]

    correctHist = whenHist(rule.ruleHist, state)

    # check if correct models have been output in preStates
    # do so by just looking it up in the states own hist model
    # when = correctModel + ' and ' + correctHist
    when = correctHist
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
        # there seem to be problems with to large strings in PEACH
        # resolved in PEACH manually..
        dataElements = list(set(rule.data))
        cont = ';;;'.join(dataElements)
        if blob:
            cont = ' '.join(list(map(lambda x: (x[2:].zfill(2)), list(map(hex, parse.unquote_to_bytes(cont))))))
            models[-1].append(ET.Element('Blob', attrib={'mutable': 'false', 'valueType': 'hex'}, name='c{}'.format(computeAbsoluteFields(
                state, rule.ruleHist.getID()[0], rule.dstField)), value='{}'.format(cont)))
        else:
            models[-1].append(ET.Element('String', attrib={'mutable': 'false'}, name='c{}'.format(computeAbsoluteFields(
                state, rule.ruleHist.getID()[0], rule.dstField)), value='{}'.format(cont)))
        slurps.append(dataSlurp(state, rule, models[-1].attrib['name'], done, DEBUG))

    for model in models:
        if model.attrib['name'] not in dataRuleModels.keys():
            dataRuleModels.update({model.attrib['name']: model})

    return models, slurps

def createDataRuleModel(state, hist, DEBUG=False):
    modelName = '{} {}'.format(hist, state.curState)
    drModel = ET.Element('DataModel', name=str(modelName))
    return drModel


def assembleCopyRules(rule):
    call = 'Prisma.'
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


def encodeState(state, DEBUG=False):
    if DEBUG:
        return '{}'.format(state.curState)
    return str(base64.b64encode('{}'.format(state.curState).encode('ascii')))[2:-1].replace('=', '')


def dataSlurp(state, rule, modelName, done, DEBUG):
    encState = encodeState(state, DEBUG)
    if not DEBUG:
        modelName = str(base64.b64encode((modelName).encode('ascii')))[2:-1].replace('=', '')
    ID = rule.ruleHist.getID()[0]
    absoluteDstField = computeAbsoluteFields(state, ID, rule.dstField)
    adiC = 'Prisma.dataRule(self)'
    if ID in fieldsINblock.keys() and absoluteDstField > int(fieldsINblock[ID][1:]):
        adiC = 'Prisma.dataRule(self,1)'
    setXpath = '//StateModel//{}//out{}//out{}//c{}'.format(encState, ID, ID, absoluteDstField)
    valueXpath = '//StateModel//{0}//{1}//c{2}'.format(encState, modelName, absoluteDstField)
    slurp = ET.Element('Action', attrib={'type': 'slurp', 'onComplete': adiC,
                                         'valueXpath': valueXpath, 'setXpath': setXpath})

    # check if correct model is output in this state
    correctModel = computeWhenOut(state, ID, DEBUG)
    correctHist = whenHist(rule.ruleHist, state)

    # check if correct models have been output in preStates
    # do so by just looking it up in the states own hist model
    when = correctHist
    slurp.set('when', when)
    if len(state.templates) > 1:
        onStart = int(correctModel.split('==')[1].split('int(')[1][:-1])
        slurp.set('onStart', 'Prisma.randMan(self,"{}")'.format(onStart))
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
        temps = copy.deepcopy(templates.stateToID[state.curState])
        for tempID in temps[:]:
            # if template has no content: remove it
            if not templates.IDtoTemp[tempID].content:
                temps.remove(tempID)
        state.templates = temps

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

    # fetch rules
    #normal rules
    for tempID in state.templates:
        if tempID in rules.keys():
            for r in rules[tempID]:
                state.rules.append(r)
    # #data rules
    for tempID in state.templates:
        if tempID in dataRules.keys():
            for r in dataRules[tempID]:
                state.dataRules.append(r)
    # #copy rules
    for tempID in state.templates:
        if tempID in copyRules.keys():
            for r in copyRules[tempID]:
                state.copyRules.append(r)
    appendTodo(container, state)
    return


def appendTodo(container, state):
    if state.name in container.done.keys():
        # having state already -> do nothing
        PeachState = container.done[state.name][0]
        for prev in state.previous:
            PeachState.previous.append(prev)
        return
    container.doneadd(state)
    if state.nextStates != []:
        for nextState in state.nextStates:
            nxt = PeachStateReloaded(nextState, parent=state)
            container.todoadd(nxt)
    return
