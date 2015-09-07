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

    def todoadd(self, state):
        self.todo.append(state)

    def todorem(self, state):
        self.todo.remove(state)

    def donerem(self, state):
        self.done[state.hist].remove(state)

    def doneadd(self, state):
        if state.hist not in self.done.keys():
            self.done.update({state.hist: []})
        self.done.update({state.hist: self.done[state.hist] + [state]})

        # def doneadd(self,state):
        #self.done.update({state.hist:state})

        #def donerem(self,state):
        #   self.done.remove(state)
