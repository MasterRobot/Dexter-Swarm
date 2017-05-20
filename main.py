from classes import PageClass, PathLink, AntMem
from pymongo import MongoClient
import pickle
import random

client = MongoClient()
linkDB = client.wikiLinks
pageDB = client.wikiPages

resetSeed = random.randint(0,50000)

allPages = {}
currentTime = 0

pkl_file = open('wikiData.pkl', 'rb')
allPages = pickle.load(pkl_file)
print allPages.keys()
print len(allPages.keys())
pkl_file.close()
#------------------------------------------------------------
#--------------- Link Test

# allPages["Oceans"] = PageClass("Oceans")
# allPages["Floating match on card"] = PageClass("Floating match on card")
#
# allPages["Oceans"].buildLink("Floating match on card", allPages)
# print allPages.keys()
# allPages["Oceans"].changePherValue("Floating match on card", 10)
# print "ocean side =", allPages["Oceans"].linkPherValue("Floating match on card")
# print "other side =", allPages["Floating match on card"].linkPherValue("Oceans")
# print allPages.keys()

startPoint = "Malcolm Gladwell"
endGoal = "Microsoft"
max_steps = 30

gershwin = AntMem(startPoint,endGoal)
allPages[startPoint] = PageClass(startPoint)

for k in range(0,max_steps):
    gershwin.move(allPages,currentTime, resetSeed)
    print "Current = ", gershwin.current
    currentTime = currentTime + 1
    if gershwin.current == startPoint:
        print "WIN"
        break
output = open('wikiData.pkl', 'wb')
pickle.dump(allPages, output)
