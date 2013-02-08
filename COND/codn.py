import os
import sys
from Actor import Actor
from Game import Game

POP_SIZE = 10

class codn(object):
    def __init__(self):
        self.archieve = []
        self.popActors = []
        self.popGames = []
        pass

    def createPopulations(self):
        #Create a population of actor objects.
        self.popActors = [Actor() for i in range(POP_SIZE)]
        self.popGames = [Game() for i in range(POP_SIZE)]

        pass


def main (argv=None):
    print("In codn\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
