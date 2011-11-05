# stdlib
import sys
import datetime
# local
import protocol
from brownian import Decider as Brownian


def genlogger(fn):
    LOG = open(fn, mode='wb')
    def f(s):
        LOG.write('{} {}\n'.format(datetime.datetime.now(), s))
        LOG.flush()
    return f


def listen():
    return sys.stdin.readline().strip()


def tell(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    #
    # initialize bot
    if len(sys.argv) > 1:
        logger = genlogger(sys.argv[1])
        brain = Brownian(logger)
        bot = protocol.Bot(brain, logger)
    else:
        logger = lambda s: None
        brain = Brownian()
        bot = protocol.Bot(brain)
    #
    # main loop
    while True:
        heard = listen()
        #logger('IN ' + heard)
        replies = bot.handle(heard)
        if replies:
            tell('\n'.join(replies))
            #logger('OUT ' + str(replies))
