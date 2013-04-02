from naoqi import *
import math
import almath
import random
import time
import copy
import uuid
##from pybrain.tools.shortcuts import buildNetwork
##from pybrain.structure import FeedForwardNetwork
##from pybrain.structure import LinearLayer, SigmoidLayer
##from pybrain.structure import FullConnection
##from pybrain.datasets import SupervisedDataSet
##from pybrain.supervised.trainers import BackpropTrainer
##from pybrain.tools.neuralnets import NNregression 
##from pybrain.tools.plotting import MultilinePlotter

# create python module
class gameClass(ALModule):
  """Create a game instance"""


  def __init__(self,  nameA = None, count = None, messages = None, function = None):

    ALModule.__init__(self,str(uuid.uuid4()))
    self.mm = ALProxy("memoryManager")
    self.motion = ALProxy("ALMotion")
    self.atomKind = nameA
    self.id = count
    self.messages = messages
    self.function = function
    self.mm.putGameMemory(self.id, [1,0,0]) #0 in first position = inactive, 1 in first position = active. 
    self.fitness = [0]*len(self.messages) #Fitness vector over all actors that this game examines/watches.
    self.messageHistory = []

  def clearMessageHistory(self):      
      self.messageHistory = []
    
  def getMoleculeFitness(self):
      #print "OBSERVED MESSAGES FOR THIS EXPERIMENT WERE: " + str(self.messageHistory)
      if self.function == "maximize" and len(self.messageHistory) > 1:
          #print "start fit = " + str(self.messageHistory[len(self.messageHistory)-1])
          #print "finish fit = " + str(self.messageHistory[0])
          #print self.messageHistory
          return self.messageHistory[len(self.messageHistory)-1] - self.messageHistory[0]
      if self.function == "minimize" and len(self.messageHistory) > 1:
          return self.messageHistory[0] - self.messageHistory[len(self.messageHistory)-1]
      else:
          return 0

  def storeObservedMessages(self):
      #Go through each message that this game observes
      for index, i in enumerate(self.messages):
          #Check if the message is active
          #print "observed games messages " + str(self.messages[index])
          if self.mm.getMessageValue(i)[0] == 1:
              self.messageHistory.append(self.mm.getMessageValue(i)[1])

  def removeGameMessages(self, message):
          for index, i in enumerate(message):
            for index2, j in enumerate(self.messages):
              if message[index] == self.messages[index2]:
                del self.messages[index2]

  def updateGameMessages(self, fromM, toM):
      newMessages = []
      for index, i in enumerate(self.messages):
          if self.messages[index] == fromM:
              newMessages.append(toM)
      self.messages.extend(newMessages)
      self.messages = list(set(self.messages))
      #print "Updated messages are: + " + str(self.messages)
    
  def exit(self):
    self.isRunning=False
    ALModule.exit(self)
