class InterState(object):
    def __init__(self, curState, preHist):
        self.preHist = preHist
        self.postHist = None
        self.curState = curState
        self.nextStates = None
        self.hist = None
        self.templates = None
        self.rules = None
        self.copyRules = None 
        self.dataRules = None 
        self.dataFields = None
        self.IOAction = None
        self.isinitial = False

    def copy(self,ID):
        a = InterState(self.curState, self.preHist)
        a.hist = self.preHist.update([ID])
        a.templates = [ID]
        return a

    def __str__(self):
       # if self.hist != None:
        #    return str(self.hist) + ' ' + str( self.curState)
        return str(self.hist) + ' ' + str(self.curState) + ' ' + str(self.templates) + ' ' + str(self.rules) + ' ' + str(self.copyRules) + ' ' + str(self.dataRules) + ' ' + str(self.IOAction)#str(self.preHist) + ' --> ' + str(self.curState)

    def __repr__(self):
        if self.hist != None:
            return 'InterState{!r}{!r}'.format(self.hist, self.curState)
        return 'InterState{!r}-->{!r}'.format(self.preHist, self.curState)

    def __eq__(self,obj):
        return isinstance(obj,InterState) and self.curState == obj.curState and self.hist == obj.hist and self.preHist == obj.preHist

    def getCurState(self):
        return self.curState.getCurState()

    def __hash__(self):
        return hash(self.hist)


