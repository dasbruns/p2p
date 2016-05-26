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

    parser.add_argument('-o', '--outFile', help='specify output file name', default='')
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


    try:
        f = open('{0}/{1}.markovModel'.format(args.folder, args.name), 'r')
        if args.verbose > 1: print('  \\__Processing MarkovModel ...', end='', flush=True)
        model = PrismaIO.markovParse(f)
        f.close()
        # do not enhance statemodel
        if args.enhance and False:
            if args.verbose > 1: print('\n    \\__pruning StateModel ...', end='', flush=True)
            model.modelEnhancer()
        if args.verbose: print(' Done\n', end='', flush=True)
    except FileNotFoundError:
        print('file {0}/{1}.markovModel not found'.format(args.folder, args.name))
        exit()

    if args.verbose: print('\nInternal Dataprocessing ... ', end='', flush=True)
    #gap to peach
    #Decide which side of communication we are
    container = peach.PeachStateContainer()

    #create first state
    start = peach.PeachStateReloaded(PrismaIO.PrismaState(theHistLength * ['START']), parent=None, init=True)
    start.nextStates = model.model[start.curState]
    #fetch possible Templates for this State
    if start.curState in templates.stateToID.keys():
        start.templates = templates.stateToID[start.curState]
    container.doneadd(start)
    for nextState in start.nextStates:
        container.todoadd(peach.PeachStateReloaded(nextState, parent=start))
    #create other states
    while (container.todo != []):
        state = container.todo[0]
        container.todorem(state)
        peach.stateAssembler(state, container, model, templates, rulesReloaded, copyRulesReloaded, dataRulesReloaded, args.role)
    if args.verbose > 1: print('Done\n')
    if args.verbose > 1: print('Processing DataModels ... ', end='', flush=True)
    pit = peach.dataModel(templates.IDtoTemp, theHistLength, args.crazyIvan, args.blob, args.advanced, args.role)
    if args.verbose > 1: print('Done')
    if args.verbose > 1: print('Processing StateModel ... ', end='', flush=True)
    pit = peach.stateModel(pit, container.done, theHistLength, templateID2stateName, args.debug, args.blob)
    if args.verbose > 1: print('Done')
    if args.verbose > 1: print('Processing Agent/Test area ... ', end='', flush=True)
    pit = peach.agent(pit, args.application, args.role, args.port)
    pit = peach.test(pit, args.role, args.address, args.port)
    if args.verbose: print('Done\n')
    if args.role:
        if args.verbose: print('Writing to {0}/{1}client.xml'.format(args.folder, args.outFile))
        pit.toFile('{0}/{1}client.xml'.format(args.folder, args.outFile))
    else:
        if args.verbose: print('Writing to {0}/{1}server.xml'.format(args.folder, args.outFile))
        pit.toFile('{0}/{1}server.xml'.format(args.folder, args.outFile))

