__author__ = 'dasmoep'

class PeachStateReloaded(object):

    def __init__(self, curState, parent, init=False):
        # ref to parent in graph; each state has exactly one parent
        # one state may be parent of arbitrary many states (including 0)
        self.name = '|'.join(curState.hist)
        self.isInitial = init
        #these are PEACH states
        self.previous = []
        if parent:
            self.previous.append(parent)
        self.next = []
        #these are PRISMA states
        self.curState = curState
        self.nextStates = []
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
        # return str(self.curState) + ' ' + str(self.templates) + ' ' + str(self.rules) + ' ' + str(self.copyRules) + ' ' + str(self.dataRules) + ' ' + str(self.ioAction)#str(self.preHist) + ' --> ' + str(self.curState)
        return self.name

    def __repr__(self):
        return 'PeachState {!r}'.format(self.name)

    def getCurState(self):
        return self.curState.getCurState()

    def isMulti(self):
        return (len(self.templates) > 1) or (self.ioAction == 'input')

    def getRules(self, type):
        if type == 'rules':
            return self.rules
        if type == 'copy':
            return self.copyRules

    def isInit(self):
        return self.isInitial

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, obj):
        if isinstance(obj, PeachStateReloaded):
            #for key in self.__dict__.keys():
            #    if key != 'preHist' and key != 'parent':
            #        if self.__dict__[key] != obj.__dict__[key]:
            #            return False
            if obj.name == self.name:
                return True
        return False  # isinstance(obj, PeachState) and self.__dict__ == obj.__dict__
