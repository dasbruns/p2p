from .InterState import InterState
from .InterStateContainer import InterStateContainer
from .PIT import PIT
from lxml import etree as ET

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
    return dataModel


def stateModel(pit, done):
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
            theRules = slurpActions(state)
            for rule in theRules:
                peachState.append(rule)
            actionCounter += len(theRules)
        #implement IOactions
        #print(state.hist)
        if state.IOAction == 'input':
            inputAction = ET.Element('Action', name='rec', attrib={'type':'input'})
            inputAction.append(ET.Element('DataModel', name='read', attrib={'ref':str(state.hist)}))
            peachState.append(inputAction)
            actionCounter += 1
        if state.IOAction == 'output':
            #insert copyRules here in onStart
            outputAction = ET.Element('Action', name='out', attrib={'type':'output','onStart':'void'})
            dataModel = ET.Element('DataModel', name='write', attrib={'ref':str(state.hist)})
            #look for DATA to be applied by DataRules
            if state.dataRules != None:
                dataModel = data(dataModel, state)
            outputAction.append(dataModel)
            peachState.append(outputAction)
            actionCounter += 1
        #implement random number
        if state.nextStates != None and len(state.postHist) > 1:
            randomAction = ET.Element('Action', name='rand', attrib={'publisher':'null', 'onStart':'additionalCode.rand(self,{})'.format(len(state.postHist)-1)})
            randomAction.append(ET.Element('DataModel', attrib={'ref':'rand'}))
            peachState.append(randomAction)
        #impement changeState actions
        if state.postHist != None:
            prob = len(state.postHist) - 1
            for nextState in state.postHist:
                if prob == 0:
                    changeState = ET.Element('Action', attrib={'type':'changeState', 'ref':str(nextState)})
                else:
                    changeState = ET.Element('Action', attrib={'type':'changeState', 'ref':str(nextState), 
                        'when':'int(StateModel.states[{}].actions[{}].dataModel["a1"].InternalValue) == int({})'.format(state.hist,actionCounter,prob)})
                prob -= 1
                peachState.append(changeState)
        stateModel.append(peachState)
    return pit

def data(dataModel, state):
    index = 0
    for dataRule in state.dataRules:
        #print(dataRule,' Index: ',index, 'Field: ',state.dataFields[index])
        for point in dataRule.data:
            data = ET.Element('Data')
            data.append(ET.Element('Field', name='c'+str(state.dataFields[index]), attrib={'value':point}))
            dataModel.append(data)
        index += 1
    return dataModel

def slurpActions(state):
    theRules = []
    #print(state.hist,state.IOAction)
    for rule in state.rules:
        #construct path from where to read; valueXpath
        #print(rule)
        #construct path to where to write; setXpath
        theRules.append(ET.Element('Action',attrib={'type':'slurp','valueXpath':'?', 'setXpath':'!'}))#, name=str(rule.hist), attirb={'type':'slurp'}))
    return theRules

def createInterState(curState, preHist):
    return InterState(curState,preHist)


