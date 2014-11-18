#!/usr/bin/env python

#from PrismaState import PrismaState as P

class Hist(object):

    def __init__(self, prePreTempID, preTempID, curTempID):
        self.prePreTempID = prePreTempID
        self.preTempID = preTempID
        self.curTempID = curTempID

    def __str__(self):
        return str(self.prePreTempID) + ':' + str(self.preTempID) + ':' + str(self.curTempID)

    #remove later
    def __repr__(self):
        return 'Hist({!r},{!r},{!r})'.format(self.prePreTempID, self.preTempID, self.curTempID)

    def __hash__(self):
        return hash(str(self.prePreTempID)) ^ hash(str(self.preTempID)) ^ hash(str(self.curTempID))

    def __eq__(self,obj):
        return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.preTempID == self.preTempID and obj.curTempID == self.curTempID
