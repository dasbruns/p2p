from .PrismaState import PrismaState
from .MarkovTransition import MarkovTransition
from .MarkovModel import MarkovModel

def markovParse(filehandle):
    model = MarkovModel()
    for line in filehandle:
        line = line.split(',',1)[0]
        left, right = line.split('->')
        curState = PrismaState(*left.split('|'))
        nextState = PrismaState(*right.split('|'))
        transition = MarkovTransition(curState,nextState)
        model.add(transition)
    return model
        #transition = M()

