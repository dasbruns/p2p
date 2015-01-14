#!/usr/bin/env python

#from PrismaState import PrismaState as S
#from MarkovModel import MarkovModel
#from MarkovTransition import MarkovTransition as P
import prisma
import peach
import copy

#def multiAssembler(state, hist, container, model, templates)
 #   s = peach.createInterState(state.curState,state.preHist)


def stateAssembler(state, container, model, templates, UAC=False):
    if 'END' in str(state.curState):
        state.hist = state.preHist.update(['00'])
        state.IOAction = 'END'
        #set preStates postHist
        setPostHist(container.done, state)
        #if container.done[state.preHist].postHist == None:
        #    container.done[state.preHist].postHist = []
        #container.done[state.preHist].postHist.append(state.hist)
        if state not in container.done:
            container.doneadd(state)
        return
    state.templates = templates.stateToID[state.curState]
    #obtain one state per message which can be send in this state
    if (UAC == True and 'UAC' in state.getCurState()) or (UAC == False and 'UAC' not in state.getCurState()):
        for ID in state.templates:
            updateState = state.copy(ID)
            #set templates history
            setTemplatesHist(ID, updateState.hist)
            #set preStates postHist
            updateState.nextStates = model.model[state.curState]
            updateState.IOAction = 'output'
            #multiply em here
            if len(updateState.hist.preTempID) > 1:
                #print(updateState)
                for hist in updateState.hist.assembleHist():
                    cpy = copy.deepcopy(updateState)
                    cpy.hist = hist
                    #print(cpy)
                    setPostHist(container.done, cpy)
                    appendTodo(container, cpy)

            #set correct postHist in preState
            else:
                setPostHist(container.done, updateState)
                appendTodo(container, updateState)
    #just keep all templates and construct multimodel later
    else:
        if len(state.templates) > 1:
            IDs = []
            for ID in state.templates:
                IDs.append(ID)
        else:
            IDs = state.templates
        state.hist = state.preHist.update(IDs)
        #set templates history
        for ID in IDs:
            setTemplatesHist(ID, state.hist)
        #set preStates postHist
        setPostHist(container.done, state)
        state.nextStates = model.model[state.curState]
        state.IOAction = 'input'
        appendTodo(container, state)

def appendTodo(container, state):
   if state.hist not in container.done.keys():
       container.doneadd(state)
       for nextState in state.nextStates:
           nxt = peach.InterState(nextState, state.hist)
           container.todoadd(nxt)

def setPostHist(done, state):
   if container.done[state.preHist].postHist == None:
       container.done[state.preHist].postHist = []
   container.done[state.preHist].postHist.append(state.hist)

def setTemplatesHist(ID, hist):
   if templates.IDtoTemp[ID].hists == None:
       templates.IDtoTemp[ID].hists = []
   templates.IDtoTemp[ID].hists.append(hist)

def toPeachStates(done, pit):
    for state in done:
        pit.insertState(state)

if __name__ == '__main__':

    f = open('samples/koobface.templates','r')
    templates = prisma.templateParse(f)
    f.close()
    for i,j in templates.IDtoTemp.items():
        #print(i,j)
        pass
    for i,j in templates.stateToID.items():
        pass
        #print(i,j)

    f = open('samples/koobface.rules','r')
    rules, copyRules, dataRules = prisma.ruleParse(f)
    f.close()
    count = 0
    ##print('===========RULES============')
    #for i in rules.keys():
    #    if i.curTempID == 31:
    #        #print(i,rules[i])
    #    count += len(rules[i])
    ##print('===========DATA=============')
    #for i in dataRules.keys():
    #    if i.curTempID == 31:
    #        #print(i,dataRules[i])
    #    count += len(dataRules[i])
    ##print('===========COPY=============')
    #for i in copyRules.keys():
    #    if i.curTempID == 31:
    #        #print(i,copyRules[i])
    #    count += len(copyRules[i])
    ##print(count)

    f = open('samples/koobface.markovModel','r')
    model = prisma.markovParse(f) 
    f.close()
    for i,j in model.model.items():
        #l.append(peach.InterStates(i,prisma.Hist(1,2,3)))
        #print(i,j)
        pass
    #print(model.model[prisma.PrismaState('START','START')])

    #gap to peach
    #Decide which side of communication we are
    container = peach.InterStateContainer()

    #create first state
    start = peach.InterState(prisma.PrismaState('START','START'),prisma.Hist([-1],[-1],[-1]))
    start.nextStates = model.model[start.curState]
    start.isinitial = True
    if start.curState in templates.stateToID.keys():
        start.templates = templates.stateToID[start.curState] 
    else:
        start.hist = start.preHist
        container.doneadd(start)
        for nextState in start.nextStates:
            container.todoadd(peach.InterState(nextState,start.preHist))
    #create other states
    while(container.todo != []):
        state = container.todo[0]
        container.todorem(state)
        #if parent was multiModel state, create mutiple nextStates
        #print(state.preHist)
        #if len(state.preHist.preTempID) > 1:
        #    for hist in state.preHist.assembleHist():
        #        #multiAssembler(state, hist, container, model, templates)
        #       stateAssembler(peach.createInterState(state.curState,state.preHist), container, model, templates)
        #    continue
        stateAssembler(state, container, model, templates)

    #assign rules to state
    for state in container.done.values():
        possibleHist = state.hist.assembleHist(True)
        for hist in possibleHist:
            if state.templates != None:
                if len(state.hist.curTempID)>1:
                    state.isMultiModel = True
                    if state.fields == None:
                        state.fields = []
                    state.fields.append(templates.IDtoTemp[hist.curTempID].fields)
                else:
                    state.isMultiModel = False
                    state.fields = templates.IDtoTemp[hist.curTempID].fields
            if hist in dataRules.keys():
                if state.dataRules == None:
                    state.dataRules = []
                state.dataRules += dataRules[hist]
            if hist in rules.keys():
                if state.rules == None:
                    state.rules = []
                state.rules += rules[hist]
            if hist in copyRules.keys():
                if state.copyRules == None:
                    state.copyRules = []
                if state.rules == None:
                    state.rules = []
                state.rules += copyRules[hist]
                state.copyRules += copyRules[hist]
    pit = peach.stateModel(container.done, templates.IDtoTemp)
    #OMG OMG OMG, cant believe im doing this
    allRules = {'data':dataRules,'rules':rules,'copy':copyRules}
    pit = peach.dataModel(pit, templates.IDtoTemp, allRules)
    pit.toFile('pit.xml')

