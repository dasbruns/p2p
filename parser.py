#!/usr/bin/env python

#from PrismaState import PrismaState as S
#from MarkovModel import MarkovModel
#from MarkovTransition import MarkovTransition as P
import prisma
import peach
import copy
import argparse
import os

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

    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='where to look for files')
    parser.add_argument('-r', '--role', help='set if you are server', action='store_true')
    parser.add_argument('-n', '--name', help='specify name of parsed family')
    parser.add_argument('-v', '--verbose', action='count', help="tells what's currently going on")
    args = parser.parse_args()
    print(args)

    if args.folder[-1] == '/':
        args.folder = args.folder[:-1]
    try:
        if args.name == None:
            for files in os.listdir(args.folder):
                if 'markov' in files or 'templates' in files or 'rules' in files:
                    args.name = files.split('.')[0]
    except FileNotFoundError:
        print('specified directory not found')
        exit()

    if args.verbose:print('Reading Files ... ',end='',flush=True)
    try:
        f = open('{0}/{1}.templates'.format(args.folder,args.name),'r')
        templates = prisma.templateParse(f)
        f.close()
    except FileNotFoundError:
        print('file {0}/{1}.templates not found'.format(args.folder,args.name))
        exit()
    #for i,j in templates.IDtoTemp.items():
        #print(i,j)
    #    pass
    #for i,j in templates.stateToID.items():
    #    pass
        #print(i,j)

    try:
        f = open('{0}/{1}.rules'.format(args.folder,args.name),'r')
        rules, copyRules, dataRules = prisma.ruleParse(f)
        f.close()
    except FileNotFoundError:
        print('file {0}/{1}.rules not found'.format(args.folder,args.name))
        exit()
    #count = 0
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

    try:
        f = open('{0}/{1}.markovModel'.format(args.folder,args.name),'r')
        model = prisma.markovParse(f) 
        f.close()
    except FileNotFoundError:
        print('file {0}/{1}.markovModel not found'.format(args.folder,args.name))
        exit()
    if args.verbose:print('Done')
    for i,j in model.model.items():
        #l.append(peach.InterStates(i,prisma.Hist(1,2,3)))
        #print(i,j)
        pass
    #print(model.model[prisma.PrismaState('START','START')])

    if args.verbose:print('Internal Dataprocessing ... ',end='',flush=True)
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
        stateAssembler(state, container, model, templates, args.role)

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
    if args.verbose:print('Done')
    if args.verbose:print('Processing StateModel ... ',end='',flush=True)
    pit = peach.stateModel(container.done, templates.IDtoTemp)
    if args.verbose:print('Done')
    #OMG OMG OMG, cant believe im doing this
    allRules = {'data':dataRules,'rules':rules,'copy':copyRules}
    if args.verbose:print('Processing DataModels ... ',end='',flush=True)
    pit = peach.dataModel(pit, templates.IDtoTemp, allRules)
    if args.verbose:print('Done')
    if args.verbose:print('Processing Agent/Test area ... ',end='',flush=True)
    pit = peach.Agent(pit)
    pit = peach.Test(pit,args.role)
    if args.verbose:print('Done')
    if args.role:
        if args.verbose:print('Write to {0}/pitServer.xml'.format(args.folder))
        pit.toFile('{0}/pitServer.xml'.format(args.folder))
    else:
        if args.verbose:print('Write to {0}/pitClient.xml'.format(args.folder))
        pit.toFile('{0}/pitClient.xml'.format(args.folder))

