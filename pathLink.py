from pageC import PageClass

class PathLink:

    #global allPages
    evapRate = 2

    def __init__(self, startObj, endString, fullDict):
        # Default Parameters
        self.phermones = 0
        self.startStr = startObj.pageStr
        self.endStr = endString
        self.lastUpdate = 0
        # Create Link
        if endString in fullDict:
            fullDict[endString].setLink(self.startStr, self)
        else:
            newPage = PageClass(endString)
            newPage.setLink(self.startStr,self)
            fullDict[endString] = newPage

    def addPhermones(self, val, timeStep):
        self.phermoneUpdate(timeStep)
        self.phermones = self.phermones + val

    def phermoneUpdate(self, timeStep):
        diff = timeStep - lastUpdate
        evap = diff*evapRate
        self.phermones = self.phermones - evap
        self.lastUpdate = timeStep
        if self.phermones < 0:
            self.phermones = 0
