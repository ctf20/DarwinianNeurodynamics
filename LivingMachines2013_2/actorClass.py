from naoqi import *
import math
import almath
import random
import time
import copy
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.neuralnets import NNregression 
from pybrain.tools.plotting import MultilinePlotter

# create python module
class actorClass(ALModule):
  """Create an actor instance"""
  
  def __init__(self,typeA = None, nameA = None, count = None, sensors = None,messages = None, motors = None, function = None, parameters = None):

    #Create a proxy to the memoryManager module.
    self.mm = ALProxy("memoryManager")
    self.motion = ALProxy("ALMotion")
    self.type = typeA
    self.atomKind = nameA
    self.id = count
    self.sensors = sensors
    self.messages = messages
    self.motors = motors
    self.function = function
    self.mm.putMemory(self.id, [0,0,0]) #0 in first position = inactive, 1 in first position = active. 
    self.active = False      
    self.timesTested = 0
    self.parameters = parameters
    self.oldParameters = parameters
    self.fitness = 0
    self.oldFitness = 0
    self.set_stiffness(1)

  def act(self):

    #Update no of times actor has been activated.  
    self.timesTested = self.timesTested+1
    
    #Get sensor data
    if self.sensors is not None:
        v = [0] * len(self.sensors) 
        j = 0                      
        for i in self.sensors:      
          v[j] = self.mm.getSensorValue(i) 
          j = j +1

    #Get message data [use a list because messages may be composite]
    m = []
    if self.messages is not None:
      for i in self.messages:
        m.append(self.mm.getMessageValue(i))








    #Type dependent actions
    if self.type is "sensory":#Just take memory, calculate a function and write it to memory.
        print "sensory atom " + str(self.id)
        if self.function is "sum":
            functSum = 0
            for i in v:
                functSum = functSum + i
        self.mm.putMemory(self.id,[1, functSum, 0])
        #print "sensors = " + str(v)






 
    elif self.type is "shc":
        print "SHC atom " + str(self.id)
        #Get fitness of previously tried parameters. 
        if self.function is "sum":
            functSum = 0
            for i in m:
                functSum = functSum + i[1]
            self.fitness = functSum
            print "New fitness = " + str(self.fitness)
            
        if self.fitness < self.oldFitness  or random.random() < 0.05:#If fitness better than old fitness.
            print "retrying new parameters"
            self.oldParameters = list(self.parameters) #Set oldParameters to parameters. 
            self.oldFitness = self.fitness #Old fitness updated with new fitness.
            #Construct new random parameters and pass them to the movement atom
            for i,v in enumerate(self.parameters):
                self.parameters[i] = self.parameters[i] + 0.5*(random.random()-0.5)
        else:
            print "resetting parameters" 
            self.fitness = self.oldFitness #new fitness reset to old fitness.
            self.parameters  = list(self.oldParameters)#Reset old parameters and pass them to the movement atom.
            
        #Write parameters to memory
        self.mm.putMemory(self.id,[1, self.parameters, 0])

        
    if self.type is "motor":
        #Go through each motor and set its value according to the message.
        print "motion atom " + str(self.id)
        inputs = m[0][1]
        print "INputs to motor atom num " + str(self.id) + " = " + str(inputs)
        angles = []
        names = []
        for index, i in enumerate(self.motors):
            name = self.mm.getMotorName(i)
            names.append(name)
            lim = self.motion.getLimits(self.mm.getMotorName(i))
            angles.append(inputs[index])
            if angles[index] < lim[0][0]/2.0:
              angles[index] = lim[0][0]/2.0
            if angles[index] > lim[0][1]/2.0:
              angles[index] = lim[0][1]/2.0          
        self.motion.setAngles(names,angles,1)#Actually move the motors according to values in angles list.
        self.mm.putMemory(self.id,[1, 0, 0])

        print names
        print angles
        time.sleep(0.1)

        pass

  def conditionalActivate(self):
    if self.messages is not None:
        for i in self.messages:
            #print self.mm.getMessageValue(i)
            if self.mm.getMessageValue(i)[0] is 1: 
              self.active = True
              print str(self.id) + "Activated by atom " + str(i) + " with message" + str(self.mm.getMessageValue(i))
              self.mm.putMemory(self.id,[1,0,0])#Active signal
          
  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)


    
          
  def exit(self):
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
