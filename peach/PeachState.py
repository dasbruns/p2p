class PeachState(object):
    def __init__(self, curState, preHist, hist):
        #these are PRISMA states
        self.curState = curState
        self.nextStates = []
        #these are HIST objects
        self.preHist = preHist
        self.hist = hist
        self.nextHist = None
        #this is TEMPLATE object
        self.templates =  []
        self.fields = None
        #these are DIFFERENT RULE objects
        self.rules = []
        self.copyRules = []
        self.dataRules = []
        self.ioAction = []
        #self.isinitial = False
        #self.isMultiModel = None

    #def copy(self, ID):
    #    a = PeachState(self.curState, self.preHist)
    #    a.hist = self.preHist.update([ID])
    #    a.templates = [ID]
    #    return a

    def __str__(self):
       # if self.hist != None:
        #    return str(self.hist) + ' ' + str( self.curState)
        return str(self.hist) + ' ' + str(self.curState) + ' ' + str(self.templates) + ' ' + str(self.rules) + ' ' + str(self.copyRules) + ' ' + str(self.dataRules) + ' ' + str(self.ioAction)#str(self.preHist) + ' --> ' + str(self.curState)

    def __repr__(self):
        return 'PeachState {!r} {!r}'.format(self.hist, self.curState)

    #def __eq__(self,obj):
    #    return isinstance(obj,PeachState) and self.curState == obj.curState and self.hist == obj.hist and self.preHist == obj.preHist

    def getCurState(self):
        return self.curState.getCurState()

    def isMulti(self):
        return len(self.templates) > 1

    # [-11] indicates the start state
    def isInit(self):
        return self.hist.theHist[0] == [-11]

    def __hash__(self):
        return hash(self.hist)

    def __eq__(self, obj):
        return isinstance(obj, PeachState) and self.__dict__ == obj.__dict__
