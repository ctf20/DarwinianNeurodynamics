from naoqi import *
import math
import almath
import random
from gameClass import gameClass
global actors
import copy

class gamePopulationClass(ALModule):
    """Game population class"""
    
    def __init__(self,name, type):
        ALModule.__init__(self,name)
        self.isRunning=True
        self.mm = ALProxy("memoryManager")
        game0 = gameClass(nameA = "game", count = 0, messages = [0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57], function = "minimize")
        self.games = [game0]
        
    def clearMessageHistories(self):
        for index, i in enumerate(self.games):
            self.games[index].clearMessageHistory()

    def storeObservedMessages(self):
        for index, i in enumerate(self.games):
            self.games[index].storeObservedMessages()

    def getMoleculeFitness(self):
        fitnessAllGames = []
        for index, i in enumerate(self.games):
            fitnessAllGames.append(self.games[index].getMoleculeFitness())
        return fitnessAllGames

    def updateGameMessages(self, fromM, toM):
        for index, i in enumerate(self.games):
            self.games[index].updateGameMessages(fromM, toM)
        
    def exit(self):
        print "Exiting game populaton"
        try:
            pass
        except:
            pass
        self.isRunning=False
        ALModule.exit(self)

