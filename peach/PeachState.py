class PeachState(object):
    def __init__(self, curState, preHist, hist, parent=None):
        # ref to parent in graph; each state has exactly one parent
        # one state may be parent of arbitrary many states (including 0)
        # parent of initial/start state is None
        self.parent = parent
        self.name = None
        #these are PRISMA states
        self.curState = curState
        self.nextStates = []
        #these are HIST objects
        self.preHist = preHist
        self.hist = hist
        self.nextHist = None
        #this is TEMPLATE object
        self.templates = []
        self.fields = {}
        #these are DIFFERENT RULE objects
        self.rules = []
        self.copyRules = []
        self.dataRules = []
        self.ioAction = []

    def __str__(self):
        # if self.hist != None:
        #    return str(self.hist) + ' ' + str( self.curState)
        return str(self.hist) + ' ' + str(self.curState) + ' ' + str(self.templates) + ' ' + str(self.rules) + ' ' + str(self.copyRules) + ' ' + str(self.dataRules) + ' ' + str(self.ioAction)#str(self.preHist) + ' --> ' + str(self.curState)

    def __repr__(self):
        return 'PeachState {!r} {!r}'.format(self.hist, self.curState)

    def getCurState(self):
        return self.curState.getCurState()

    def isMulti(self):
        return (len(self.templates) > 1) or (self.ioAction == 'input')

    def getRules(self, type):
       if type == 'rules':
           return self.rules
       if type == 'copy':
           return self.copyRules

    # [-11] indicates the start state
    def isInit(self):
        return self.hist.theHist[0] == [-11]

    def __hash__(self):
        return hash(self.hist)

    def __eq__(self, obj):
        if isinstance(obj, PeachState):
            for key in self.__dict__.keys():
                if key != 'preHist' and key != 'parent':
                    if self.__dict__[key] != obj.__dict__[key]:
                        return False
            return True
        return False  # isinstance(obj, PeachState) and self.__dict__ == obj.__dict__
