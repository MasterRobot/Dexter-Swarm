from classes import AntColony, PageClass, PathLink, AntMem
from pymongo import MongoClient
import random

# -------- DATABASE SETUP
client = MongoClient()
db = client.dexterSwarm

# --------------PARAMETERS
#startPoint = "Malcolm Gladwell"
#endGoal = "Microsoft"
startPoint = "Jmol"
endGoal = "Microsoft"
max_steps = 20
max_ants = 10
concurrent = 1

# --------------INITIALIZATION
newColony = AntColony(startPoint, endGoal, max_steps, max_ants, concurrent, db)

# --------------RUN
newColony.run()
