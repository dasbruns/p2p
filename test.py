#!/usr/bin/env python

#from PrismaState import PrismaState as S
#from MarkovModel import MarkovModel
#from MarkovTransition import MarkovTransition as P
import prisma

if __name__ == '__main__':

    f = open('samples/ftp.rules','r')
    rules,dataRules = prisma.ruleParse(f)
    count = 0
    for i in rules.keys():
        print(i,rules[i])
        count += len(rules[i])
    for i in dataRules.keys():
        print(i,dataRules[i])
        count += len(dataRules[i])
    print(count)
    f.close()

    f = open('samples/ftp.templates','r')
    templates = prisma.templateParse(f)
    for i,j in templates.IDtoTemp.items():
        #print(i,j)
        pass
    for i,j in templates.stateToID.items():
        pass
        #print(i,j)
    f.close()

    f = open('samples/ftp.markovModel','r')
    model = prisma.markovParse(f) 
    for i,j in model.model.items():
        #print(i,j)
        pass
    f.close()

