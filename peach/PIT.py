from lxml import etree as ET
class PIT(object):
    def __init__(self):
        root = ET.Element('Peach')
        self.tree = ET.ElementTree(root)

    def insertState(self, InterState):
        state = ET.Element('State', name=str(InterState.hist))
        state.append(ET.Element('Action', name=str(InterState.IOAction)))
        self.tree.getroot().append(state)

    def __str__(self):
        return str(ET.tostring(self.root,short_empty_elements=False))

    def toFile(self, fileName):
        #tree = ET.ElementTree(self.root)
        self.tree.write(fileName, pretty_print=True)
        return
