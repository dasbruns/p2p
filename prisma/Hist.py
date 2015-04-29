#!/usr/bin/env python

#from PrismaState import PrismaState as P

class Hist(object):

    #def __init__(self, prePreTempID, preTempID, curTempID):
    #    self.prePreTempID = prePreTempID
    #    self.preTempID = preTempID
    #    self.curTempID = curTempID

    def __init__(self, hist=None, updateID=None):
        if updateID != None:
            self.theHist = hist.theHist[1:] + [updateID]
        elif hist != None:
            self.theHist = hist
        #self.prePreTempID = self.theHist[-3]
        #self.preTempID = self.theHist[-2]
        #self.curTempID = self.theHist[-1]

    def update(self, ID):
        return Hist(self, updateID=ID)

    def __str__(self):
        s = ''
        for i in self.theHist:
            s += str(i) + ' ; '
        return s[:-3]
        #return str(self.prePreTempID) + ';' + str(self.preTempID) + ';' + str(self.curTempID)

    #remove later
    def __repr__(self):
        #return 'Hist({!r},{!r},{!r})'.format(self.prePreTempID, self.preTempID, self.curTempID)
        rep = ''
        for i in self.theHist:
            rep+=str(i)+';'
        return 'Hist('+rep[:-1]+')'


    def __hash__(self):
        #return hash(str(self.prePreTempID)) ^ hash(str(self.preTempID)) ^ hash(str(self.curTempID))
        h = hash(self.theHist[0][0])
        for i in self.theHist[1:]:
            h ^= hash(i[0])
        return h


    def __eq__(self,obj):
        #return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.preTempID == self.preTempID and obj.curTempID == self.curTempID
        return isinstance(obj,Hist) and obj.theHist == self.theHist

   # TODO
    def assembleHist(self,flag=False):
        allHist = []
        hist = (self.theHist[:-2],self.theHist[-2],self.theHist[-1])
        for i in hist[1]:
            allHist.append(Hist(hist[0]+[[i]]+[hist[2]]))
        return allHist
#
#    def getID(self,pos):
#        if pos == -3:
#            return self.prePreTempID
#        if pos == -2:
#            return self.preTempID
#        return self.curTempID
#
#    def differByPre(self,obj):
#        return isinstance(obj,Hist) and obj.prePreTempID == self.prePreTempID and obj.curTempID == self.curTempID and obj.preTempID != self.preTempID
            
