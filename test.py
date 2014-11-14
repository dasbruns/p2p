#!/usr/bin/env python

#from PrismaState import PrismaState as S
#from MarkovModel import MarkovModel
#from MarkovTransition import MarkovTransition as P
import prisma

if __name__ == '__main__':
    f = open('samples/ftp.markovModel','r')
    model = prisma.markovParse(f) 
    print(model)

