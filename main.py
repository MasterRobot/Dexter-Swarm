from classes import PageClass, PathLink, AntMem
from pymongo import MongoClient
import pickle
import random

# -------- DATABASE SETUP
client = MongoClient()
linkDB = client.wikiLinks
pageDB = client.wikiPages

# --------------PARAMETERS
startPoint = "Malcolm Gladwell"
endGoal = "Microsoft"
max_steps = 20
max_ants = 8
concurrent = 2
resetSeed = random.randint(0,50000)

# --------------INITIALIZATION
allPages = {}
currentTime = 0
totalAnts = 0

ants = []
for nAnt in range(0,concurrent):
    ants.append(AntMem(startPoint,endGoal, max_steps))
    totalAnts += 1

allPages[startPoint] = PageClass(startPoint)


# ------------ RUNTIME

while len(ants) > 0:

    aliveAnts = len(ants)
    antNum = 0

    while antNum < aliveAnts:
        if ants[antNum].isDead():
            ants[antNum].postMortem(allPages)
            if totalAnts <= max_ants:
                ants[antNum] = AntMem(startPoint,endGoal, max_steps)
                totalAnts = totalAnts + 1
            else:
                ants.pop(antNum)
                antNum -= 1
                aliveAnts -= 1
        else:
            ants[antNum].move(allPages,currentTime,resetSeed)
        antNum += 1

    currentTime += 1
