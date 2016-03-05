from pathLink import PathLink
import wikipedia


class PageClass:
    def __init__(self,pageName):
        self.pageStr = pageName
        self.page = wikipedia.page(pageName)
        self.linkDict = self.buildDict()

    def buildDict(self):
        tempArr = self.page.links
        lens = len(tempArr)
        newDct = {}

        for i in range(0,lens):
            dictKey = tempArr[i].encode("utf-8")
            newDct[dictKey] = None
        return newDct

    def isLinked(self, linkStr):
        return linkStr in self.linkDict

    def addLink(self, linkStr):
        # Adds link place into dictionary
        self.linkDict[linkStr] = None

    def buildLink(self, linkStr, fullDict):
        # Builds Link object between 2 page objects
        if self.linkDict[linkStr] == None:
            self.linkDict[linkStr] = PathLink(self,linkStr, fullDict)

    def setLink(self, linkStr, linkObj):
        self.linkDict[linkStr] = linkObj

    def linkPherValue(self, linkStr):
        if self.linkDict[linkStr] == None:
            return 0
        else:
            return self.linkDict[linkStr].phermones

    def changePherValue(self, linkStr, val, timeStep):
        self.linkDict[linkStr].addPhermones(val, timeStep)

    def sortLinks(self):
        sortKeys = []
        valArr = []
        strKeys = self.linkDict.keys()
        keyNum = len(strKeys)-1

        valArr.append(self.linkPherValue(strKeys[keyNum]))
        sortKeys.append(strKeys.pop())

        for i in range(0, keyNum):
            counter = 0
            temp = strKeys.pop()
            tempVal = self.linkPherValue(temp)
            while counter < len(valArr) and tempVal > valArr[counter]:
                counter = counter + 1
            valArr.insert(counter, tempVal)
            sortKeys.insert(counter, temp)

        return sortKeys[::-1]
