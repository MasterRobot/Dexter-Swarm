Dexter-Swarm
=====

## Description
Dexter-Swarm is a Wikipedia degree of seperation program. It explores the shortest path of links between two wikipedia pages using Ant-Colony optimization. If a MongoDB database is provided, Dexter-Swarm will save page information and shortest links between pages for future exploration. If the program is run for extended periods of time, the ants will gradually discover the fastest path and save link informtation for other fast path connections. With optimized settings and plenty of time, this program could be used to develop connections between topics, people, and objects.

## Development Progress
Development on this program is nearly finished. Future developments will focus on optimizing settings and reducing runtime. At the moment, tests are running to identify ideal settings for ant exploration. Work will be done to evaluate program timing, but the current development team (just TheExcitedRobot) does not have a large background in program optimization so improvements will be modest. Future work on Dexter-Swarm may improve compatibility with other programs currently planned for development (Dexter-Comp and Dexter-Knowledge).


## Software Requirements
Python 2.7.x

### Python Packages
  * Wikipedia
  * PyMongo
