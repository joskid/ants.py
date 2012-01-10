ants.py
==

*predmond at ccs dot neu dot edu*

* [My profile on aichallenge.org](http://aichallenge.org/profile.php?user=2184)
* [A detailed report about my bots in this repository](https://docs.google.com/document/d/1MB0IAFvgE2BEx4_PUJ1wvHeEERwt_C9YSU4E4FY2gHA/edit)

I participated in the *2011 Google AI Challenge* this year because I was truly intrigued by the premise of the contest. *It was fun!* After getting a bot up-and-running with the provided [starter pack](http://aichallenge.org/starter_packages.php), I thought it would be good practice to re-implement the ants protocol layer. Two things drove this decision:

* It would allow me to exercise my ability to write a protocol handler which read from stdin and wrote to stdout.
* I wanted to solve the problem of friendly ants stepping on each other at a low-enough level that my bots' logic wouldn't need to address it.

The ants-protocol implementation is in *protocol.py*, which is fed lines from stdin by *MyBot.py*. Bots are run with MyBot.py or the decider-specific files. For example, either of the following incantations would run my Hedge bot.

```bash
  $ python MyBot.py --decider Hedge
```

```bash
  $ python botHedge.py
```

I [submitted](http://aichallenge.org/profile.php?user=2184) four bots to the competition, which you can read-all-about in a [report](https://docs.google.com/document/d/1MB0IAFvgE2BEx4_PUJ1wvHeEERwt_C9YSU4E4FY2gHA/edit) I wrote. The last bot was a project for my [Machine Learning](http://www.ccs.neu.edu/home/jaa/CS6140.11F/) class taught by [Javed Aslam](http://www.ccs.neu.edu/home/jaa/). A brief overview of each of the submissions I made to the competition follows.

**Submission Notes**

1. Forgot to remove logging code. Too excited!
2. Brownian motion.
5. Oops. Forgot to zip some of the files.
3. Naive pathfinding. Simple goal assignment and elimination. Gale-Shapley to prevent ants stepping on eachother.
4. KMeans clustering. Ants now maintain different distance for different types of goals. Many kludgey policies for growth and interaction. Berzerker mode at 125 ants.
6. Hedge algorithm for probabalistically applying different strategies. Code got bloated. I don't think I'll be able to look at another python program for a year without throwing up.
7. Hedge bot tweaked to not stick to map edges quite so much...
