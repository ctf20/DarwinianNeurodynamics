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

  def __init__(self,  nameA = None, count = None, messages = None, function = None, states = None):

    ALModule.__init__(self,str(uuid.uuid4()))
    self.mm = ALProxy("memoryManager")
    self.motion = ALProxy("ALMotion")
    self.atomKind = nameA
    self.id = count
    self.messages = messages
    self.function = function
    self.mm.putGameMemory(self.id, [1,0,0]) #0 in first position = inactive, 1 in first position = active. 
    self.fitness = [0]*len(states) #Fitness vector over all actors that this game examines/watches.
#    self.messageHistory = []
    self.stateHistory = []
    self.states = states

  def clearMessageHistory(self):      
#      self.messageHistory = []
      self.stateHistory = []
    
  def getMoleculeFitness(self):
      # print "OBSERVED MESSAGES FOR THIS EXPERIMENT WERE: " + str(self.messageHistory)
      if self.function == "maximize" and len(self.stateHistory) > 1:
          #print "start fit = " + str(self.messageHistory[len(self.messageHistory)-1])
          #print "finish fit = " + str(self.messageHistory[0])
          #print self.stateHistory
          return self.stateHistory[len(self.stateHistory)-1] - self.stateHistory[0]
      if self.function == "minimize" and len(self.stateHistory) > 1:
          return self.stateHistory[0] - self.stateHistory[len(self.stateHistory)-1]
      if self.function == "sum" and len(self.stateHistory) > 1:
          sumf = 0 
          for index, i in enumerate(self.stateHistory):
            for index2, j in enumerate(self.stateHistory[index]):
              sumf = sumf + self.stateHistory[index][index2]
          return sumf
      if self.function == "negsum" and len(self.stateHistory) > 1:
          sumf = 0 
          for index, i in enumerate(self.stateHistory):
            for index2, j in enumerate(self.stateHistory[index]):
              sumf = sumf + self.stateHistory[index][index2]
          return -sumf
      else:
          return 0

    
##      #print "OBSERVED MESSAGES FOR THIS EXPERIMENT WERE: " + str(self.messageHistory)
##      if self.function == "maximize" and len(self.messageHistory) > 1:
##          #print "start fit = " + str(self.messageHistory[len(self.messageHistory)-1])
##          #print "finish fit = " + str(self.messageHistory[0])
##          #print self.messageHistory
##          return self.messageHistory[len(self.messageHistory)-1] - self.messageHistory[0]
##      if self.function == "minimize" and len(self.messageHistory) > 1:
##          return self.messageHistory[0] - self.messageHistory[len(self.messageHistory)-1]
##      if self.function == "sum" and len(self.messageHistory) > 1:
##          sumf = 0 
##          for index, i in enumerate(self.messageHistory):
##            sumf = sumf + self.messageHistory[index]
##          return sumf
##      else:
##          return 0

  def storeObservedMessages(self):
      #Go through each message that this game observes
      #for index, i in enumerate(self.messages):
          #Check if the message is active
          #print "observed games messages " + str(self.messages[index])
 #         if self.mm.getMessageValue(i)[0] == 1:
 #              self.messageHistory.append(self.mm.getMessageValue(i)[1])

      stateValues = []
      for index, i in enumerate(self.states):
          stateValues.append(self.mm.getSensorValue(i))
      self.stateHistory.append(stateValues)
      

 # def removeGameMessages(self, message):
#          for index, i in enumerate(message):
#            for index2, j in enumerate(self.messages):
#              if message[index] == self.messages[index2]:
#                del self.messages[index2]

#  def updateGameMessages(self, fromM, toM):
#      newMessages = []
#      for index, i in enumerate(self.messages):
#          if self.messages[index] == fromM:
#              newMessages.append(toM)
#      self.messages.extend(newMessages)
#      self.messages = list(set(self.messages))
#      #print "Updated messages are: + " + str(self.messages)
    
  def exit(self):
    self.isRunning=False
    ALModule.exit(self)
