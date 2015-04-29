class PeachStateContainer(object):
    def __init__(self):
        self.todo = []
        self.done = {}

    def __str__(self):
        s = 'todo:\n'
        for state in self.todo:
            s += str(state) + ', '
        s = s[:-2]
        s += '\ndone:\n'
        for state in self.done:
            s += str(state) + ', '
        return s[:-2]

    def todoadd(self,state):
        self.todo.append(state)

    def todorem(self,state):
        self.todo.remove(state)

    def doneadd(self,state):
        self.done.update({state.hist:state})

    #def donerem(self,state):
     #   self.done.remove(state)
