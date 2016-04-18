#!/usr/bin/env python

import PrismaIO
import peach
import argparse
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help='where to look for files')
    parser.add_argument('-r', '--role', help='set if you are server', action='store_false')
    parser.add_argument('-n', '--name', help='specify name of parsed family')
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Add more v's for more verbosity")

    parser.add_argument('-d', '--debug', action='store_true',
                        help='enables debug mode; does not produce valid pit files!')
    parser.add_argument('-a', '--address', help='specify which IP Peach uses', default='127.0.0.1')
    parser.add_argument('-p', '--port', help='specify which PORT Peach uses', default='36666')

    parser.add_argument('-c', '--crazyIvan', help='specify the fraction of mutable fields per model \
            (should be between 0 and 1)', default='0')
    parser.add_argument('-e', '--enhance', action='store_true',
                        help='remove useless states')
    parser.add_argument('-b', '--blob', action='store_true', help='decide to encode rule-fields as hex-blobs')
    parser.add_argument('-adv', '--advanced', action='store_true', help='make certain fields mutable')
    parser.add_argument('-bin', '--fuzzedBinary', default='pathToKodi', help='location of binary to be fuzzed')
    parser.add_argument('-app', '--application', default='kodi', help='application to be fuzzed')

    parser.add_argument('-o', '--outFile', help='specify output file name', default='pit')
    args = parser.parse_args()

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

    if args.verbose: print('Reading Files ...', end='', flush=True)
    try:
        f = open('{0}/{1}.templates'.format(args.folder, args.name), 'r')
        if args.verbose > 1: print('\n  \\__Processing Templates ...', end='', flush=True)
        templates = PrismaIO.templateParse(f)
        f.close()
        if args.verbose > 1: print(' Done\n', end='', flush=True)
    except FileNotFoundError:
        print('file {0}/{1}.templates not found'.format(args.folder, args.name))
        exit()
    #print('=============ID2TEMPS===============')
    #for i,j in templates.IDtoTemp.items():
    #    print(i,j)
    ##    pass
    # print('=============STATE2ID===============')
    # for i,j in templates.stateToID.items():
    # #    pass
    #     print(i,j)

    tmp = sorted([i for i in zip(templates.stateToID.values(), templates.stateToID.keys())])
    templateID2stateName = []
    for tup in tmp:
        for ID in tup[0]:
            templateID2stateName.append(tup[1])

    try:
        f = open('{0}/{1}.rules'.format(args.folder, args.name), 'r')
        if args.verbose > 1: print('  \\__Processing Rules ...', end='', flush=True)
        rules, copyRules, dataRules, theHistLength = PrismaIO.ruleParse(f)
        f.close()
        if args.verbose > 1: print(' Done\n', end='', flush=True)
    except FileNotFoundError:
        print('file {0}/{1}.rules not found'.format(args.folder, args.name))
        exit()

    #gosh
    rulesReloaded = {}
    for i in rules.keys():
        for j in rules[i]:
            ID = j.ruleHist.getID()[0]
            if ID not in rulesReloaded.keys():
                rulesReloaded[ID] = []
            rulesReloaded[ID].append(j)
    dataRulesReloaded = {}
    for i in dataRules.keys():
        for j in dataRules[i]:
            ID = j.ruleHist.getID()[0]
            if ID not in dataRulesReloaded.keys():
                dataRulesReloaded[ID] = []
            dataRulesReloaded[ID].append(j)
    copyRulesReloaded = {}
    for i in copyRules.keys():
        for j in copyRules[i]:
            ID = j.ruleHist.getID()[0]
            if ID not in copyRulesReloaded.keys():
                copyRulesReloaded[ID] = []
            copyRulesReloaded[ID].append(j)

    # Some stats on learned rules
    # count = 6*[0]
    # print('===========RULES============')
    # for i in rules.keys():
    #     print(i,rules[i])
    #     for r in rules[i]:
    #         count[-r.srcID-1] += 1
    #     #count += len(rules[i])
    # print(count)
    # print('===========DATA=============')
    # dataCount = 0
    # for i in dataRules.keys():
    #     print(i,dataRules[i])
    #     dataCount += len(dataRules[i])
    # print(dataCount)
    # print('===========COPY=============')
    # copyCount = 6*[0]
    # for i in copyRules.keys():
    #     print(i,copyRules[i])
    #     for r in copyRules[i]:
    #         copyCount[-r.srcID-1] += 1
    #     #copyCount += len(copyRules[i])
    # print(copyCount)
    # print(sum(count)+sum(copyCount)+dataCount)

    # dr = copy.copy(dataRules)
    # histDict = {}
    # for i in dr.keys():
    #     # print(i,dr[i])
    #     # print(i)
    #     for rule in dr[i]:
    #         # print([rule.ruleHist.getID(-2), rule.ruleHist.getID(-1)])
    #         # print(rule, rule.ruleHist, rule.ruleHist.getID(-2), rule.ruleHist.getID(-1))
    #         x = PrismaIO.Hist(hist=[rule.ruleHist.getID(-2), rule.ruleHist.getID(-1)])
    #         if x not in histDict.keys():
    #             histDict.update({x: [rule]})
    #         else:
    #             histDict.update({x: histDict[x] + [rule]})
    # for i in histDict.keys():
    #     if len(histDict[i]) > 5:
    #         k = i
    #     # print(i, histDict[i])
    #     # print(len(histDict[i]))

    # print(histDict[k])
    # l = (len(histDict.keys())) * [0]
    # i = 0
    # for key in histDict.keys():
    #     fieldDict = {}
    #     for rule in histDict[key]:
    #         dst = rule.dstField
    #         if dst not in fieldDict.keys():
    #             fieldDict.update({dst: rule.data})
    #         else:
    #             fieldDict.update({dst: fieldDict[dst] + rule.data})
    #     l[i] = fieldDict
    #     i += 1

    # c = 0
    # for i in l:
    #     #print(i)
    #     for key in i.keys():
    #         # print(key, fieldDict[key], flush=False)
    #         myList = list(set(i[key]))
    #         if len(myList) > 1:
    #             c += 1
    #             print(key, myList)
    #     print()
    # print(c)


    try:
        f = open('{0}/{1}.markovModel'.format(args.folder, args.name), 'r')
        if args.verbose > 1: print('  \\__Processing MarkovModel ...', end='', flush=True)
        model = PrismaIO.markovParse(f)
        f.close()
        # do not enhance
        if args.enhance and False:
            if args.verbose > 1: print('\n    \\__pruning StateModel ...', end='', flush=True)
            model.modelEnhancer()
            # for k,v in model.model.items():
            #     print(k,v)
        if args.verbose: print(' Done\n', end='', flush=True)
    except FileNotFoundError:
        print('file {0}/{1}.markovModel not found'.format(args.folder, args.name))
        exit()
    #print('=============MARKOVMODEL================')
    #for i,j in model.model.items():
    #l.append(peach.InterStates(i,PrismaIO.Hist(1,2,3)))
    #print(i,j)
    #print(model.model[PrismaIO.PrismaState('START','START')])

    if args.verbose: print('\nInternal Dataprocessing ... ', end='', flush=True)
    #gap to peach
    #Decide which side of communication we are
    container = peach.PeachStateContainer()

    #create first state
    # [-11] indicates true start xD
    # in case start does not emit symbol on transition
    #start = peach.PeachState(PrismaIO.PrismaState(theHistLength * ['START']), None,
    #                         PrismaIO.Hist([[-11]] + (theHistLength - 1) * [[-1]]))
                             # PrismaIO.Hist(hist=[[-11]] + (theHistLength - 1) * [[-1]]))
    start = peach.PeachStateReloaded(PrismaIO.PrismaState(theHistLength * ['START']), parent=None, init=True)
    start.nextStates = model.model[start.curState]
    # start.isinitial = True
    #fetch possible Templates for this State
    if start.curState in templates.stateToID.keys():
        start.templates = templates.stateToID[start.curState]
        # start.nextHist = start.hist.update(start.templates)
    # else:
        # start.nextHist = start.hist.update([-1])
    #print(start.nextHist)
    #print('\n===START===')
    #print(start, start.isInit())
    container.doneadd(start)
    for nextState in start.nextStates:
        # container.todoadd(peach.PeachState(nextState, start.hist, start.nextHist, parent=start))
        container.todoadd(peach.PeachStateReloaded(nextState, parent=start))
    #create other states
    while (container.todo != []):
        state = container.todo[0]
        container.todorem(state)
        #if parent was multiModel state, create mutiple nextStates
        #print(state.preHist)
        #if len(state.preHist.preTempID) > 1:
        #    for hist in state.preHist.assembleHist():
        #        #multiAssembler(state, hist, container, model, templates)
        #       stateAssembler(peach.createInterState(state.curState,state.preHist), container, model, templates)
        #    continue
        peach.stateAssembler(state, container, model, templates, rulesReloaded, copyRulesReloaded, dataRulesReloaded, args.role)
        #print(model.model)
        #print(len(container.done) ==len(model.model))
        #for i in container.done.values():
        #print()
        #print(i)
    #print(rules)
    #print('============woot==============')
    #for i,j in container.done.items():
    #    if len(j)>1:
    #        print(i)
    #        for x in j:
    #            print('\t',x.__dict__)
    #print(len(container.done),len(model.model))

    #for i in container.done.keys():
    #    print(container.done[i])
    #    print()
    #print(len(container.done),len(model.model))

    # for stateList in container.done.values():
    #     for state in stateList:
    #         if state.previous:
    #             for prev in state.previous:
    #                 prev.next.append(state)
    # for stateList in container.done.values():
    #     for state in stateList:
    #         for s in state.previous:
    #             print(s, end=' ')
    #         print('-->', state, '-->', end='')
    #         for s in state.next:
    #             print(s, end=' ')
    #         print()
    #         print()
    if args.verbose > 1: print('Done\n')
    if args.verbose > 1: print('Processing DataModels ... ', end='', flush=True)
    pit = peach.dataModel(templates.IDtoTemp, theHistLength, args.crazyIvan, args.blob, args.advanced, args.role)
    if args.verbose > 1: print('Done')
    if args.verbose > 1: print('Processing StateModel ... ', end='', flush=True)
    pit = peach.stateModel(pit, container.done, theHistLength, templateID2stateName, args.debug, args.blob)
    if args.verbose > 1: print('Done')
    if args.verbose > 1: print('Processing Agent/Test area ... ', end='', flush=True)
    pit = peach.agent(pit, args.application, args.role)
    pit = peach.test(pit, args.role, args.address, args.port)
    if args.verbose: print('Done\n')
    if args.role:
        if args.verbose: print('Writing to {0}/{1}client.xml'.format(args.folder, args.outFile))
        pit.toFile('{0}/{1}client.xml'.format(args.folder, args.outFile))
    else:
        if args.verbose: print('Writing to {0}/{1}server.xml'.format(args.folder, args.outFile))
        pit.toFile('{0}/{1}server.xml'.format(args.folder, args.outFile))

