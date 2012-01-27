# ants.py

This is my code for the [2011 Google AI Challenge](http://aichallenge.org/) in which I re-implemented the ants protocol layer. This allowed solve the problem of friendly ants stepping on each other at a low-enough level that my bots' logic wouldn't need to address it.

## Usage

The ants-protocol implementation is in *protocol.py*, which is fed lines from stdin by *MyBot.py*. If you have the official [tools](http://aichallenge.org/using_the_tools.php) you can play a game with one of my bots via *MyBot.py* or one of the decider-specific _bot*.py_ files. 

* ```$ python botBrownian.py``` moves each ant randomly. Since ants cannot step on eachother, they diffuse outward from the anthills.
* ```$ python botNavigator.py``` assigns each idle ant to a goal. Ants' goals persist between turns, and unassigned ants diffuse randomly.
* ```$ python botKMeans.py``` finds *k* goals and assigns ants to each of *k* clusters. Goals have associated *too close* and *too far* radii, so ants behave differently for different goals.
* ```$ python botHedge.py``` runs 13 simplistic strategies and probabalistically applies them. Then it judges ant behavior based on who collected food without dying and learns to trust or distrust each of the 13 strategies. *See the **metadecider** directory.*

## More Info

* [Read the report](https://docs.google.com/document/d/1MB0IAFvgE2BEx4_PUJ1wvHeEERwt_C9YSU4E4FY2gHA/edit) which details my bots' strategy and performance.
* [Watch games](http://aichallenge.org/profile.php?user=2184) my bots played in the competition.