from classes import AntColony, PageClass, PathLink, AntMem
from pymongo import MongoClient
import random

# -------- DATABASE SETUP
client = MongoClient()
db = client.dexterSwarm

# --------------PARAMETERS
#startPoint = "Malcolm Gladwell"
#endGoal = "Microsoft"
startPoint = "Malcolm Gladwell"
endGoal = "Microsoft"
csvFile = 'rawData.csv'
max_steps = 20
max_ants = 10
concurrent = 1

# --------------INITIALIZATION
#newColony = AntColony(startPoint, endGoal, max_steps, max_ants, concurrent, db, csvFile)

# --------------RUN
#newColony.run()

# -------------- CREATE AND RUN MULTIPLE
moreCol = 25
# 4000 more ants for these Settings (run until 20,000 ants)


for colC in range(0, moreCol):
    newNewCol = AntColony(startPoint, endGoal, max_steps, max_ants, concurrent, db, csvFile)
    newNewCol.run()
    print '------------------------------'
    print str(colC+1) + '/' + str(moreCol)
    print '------------------------------'
