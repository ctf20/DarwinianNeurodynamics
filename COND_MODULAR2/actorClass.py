from naoqi import *
import math
import almath
import random
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
  
  def __init__(self,name, count):
    ALModule.__init__(self,name)
    print "Making actor:" + str(count)
    self.isRunning=True

    #************RANDOMLY GENERATE THE ACTOR GENOTYPE HERE********************
    #GENOTYPE [Makes a random genotype]
    self.number = count

    #Create a proxy to the sharedData module.
    self.sd = ALProxy("sharedData")
    #And to ALMemory
    self.memory = ALProxy("ALMemory")    
    self.motion = ALProxy("ALMotion", "ctf.local", 9559)
    self.Body = self.motion.getLimits("Body")
    self.set_stiffness(1.0)
    
    self.sd.start()

    #Make a list of ALMemory state inputs that this actor will check regularly. 
    self.inputs = self.sd.getRandomMemoryInputs(5)
    print "Regular data inputs to actor " + str(count) + " = " + str(self.inputs)

    #Make a list of ALMemory Events that this actor will subscribe and listen to.
    self.eventInputs = self.sd.getRandomEventInputs(1)
    print self.eventInputs
    self.eventName = self.sd.getEventName(self.eventInputs[0])
    #Create a listener for these events to record them in recordListenedEvent
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
      pass
    print self.eventName
    self.memory.subscribeToEvent(self.eventName,self.getName(),"recordListenedEvent")

    #Make an event list to store the listened to events for use later.
    self.eventTable = []
    

    
    #Make a conditional activation function (of which various types can be selected) e.g.
    self.conditionType = random.randint(0,1)
    #***************************
    #Activation function type 0:HYPERBOXES 
    #***************************
    #HYPER-BOXES [Initial range -1 to 1] Define ranges within which the input must be for this actor to be active.
    self.hyperboxesDataCondition = self.sd.getRandWithinRanges(self.inputs)#-1 to 1 range initial. 
    print self.hyperboxesDataCondition
    #Always activate this actor on recognition of an event (by default) 
    #***************************
    #Activation function type 1:LOGISTIC REGRESSION CLASSIFIER 
    #***************************








    #Construct the internal type of the actor atom behaviour which may be of a huge range of types.
    self.actorType = random.randint(0,1)
    
    #***************************
    #Behaviour function type 0:SINGLE PRIMITIVE ACTION ONLY   
    #***************************
    #Encode a primitive action as a function of the input vector, e.g. a FFNN.
    self.hiddenSize = random.randint(1,5)
    self.outputSize = random.randint(1,5)    
    self.net = buildNetwork(len(self.inputs), self.hiddenSize, self.outputSize)
    #Choose a subset of self.outputSize actions to control.
    print self.outputSize
    self.outputs = self.sd.getRandomMotors(self.outputSize)

    #***************************
    #Behaviour function type 1:SINGLE PRIMITIVE ACTION + WRITE TO ALMEMORY
    #In this case, construct this memory structure in the 0 state awaiting writing.
    #And put this into the sharedMemory numToData array. 
    #***************************
    self.memory.insertData("ActorData" + str(count), 1)#1 is inactive. 0 is active. 
    self.sd.insertData("ActorData" + str(count))
    
    #***************************
    #Behaviour function type 2:SINGLE PRIMITIVE ACTION + RAISE EVENT
    #In this case, create this type of event and put it in the numToEvent array. 
    #***************************
    #self.memory.raiseEvent("ActorEvent"+str(count), 1)
    #self.sd.insertEvent("ActorEvent"+str(count))

    #Actor state and fitness variables****************
    self.active = False       #Starts inactive.
    self.dataMatched = False  #Starts unmatched to data.
    self.timesTested = 0      #Number of times this actor has been tested. 


  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)
    
  def act(self):
    #Actor is active if we get here, so increment times tested.
    self.timesTested = self.timesTested+1  
    #Update sensory input from ALMemory
    v = [0] * len(self.inputs) #Initialize input vector to zero. 
    j = 0                      #Counter. 
    for i in self.inputs:      #For each data input into the atom. 
      v[j] = self.memory.getData(self.sd.getDataName(i)) #Get data value 
      j = j +1
    if self.actorType is 0 or self.actorType is 1: #For now type doesnt matter how actor acts. 
      motorRaw = list(self.net.activate(v)) #Put through neural network to get raw "motor" outputs  
    angles = motorRaw
    names = []
    for i in range(len(angles)):
      names.append(self.sd.getMotorName(self.outputs[i]))#Put motor output names into names list

    for index, i in enumerate(names):#Check that motor outputs are within limits. 
      lim = self.motion.getLimits(i)
      #print lim
      #print i
      if angles[index] < lim[0][0]/2.0:
        angles[index] = lim[0][0]/2.0
      if angles[index] > lim[0][1]/2.0:
        angles[index] = lim[0][1]/2.0
 
    self.motion.post.setAngles(names,angles,0.5)#Actually move the motors according to values in angles list. 

  def conditionalActivate(self):
    #print "In conditinal activate of atom " + str(self.number)
    #1. Go through inputs looking for inputs that start with ActorData 
    for i in self.inputs:
      if "ActorData" in self.sd.getDataName(i):
        #print self.sd.getDataName(i)
        if self.memory.getData(self.sd.getDataName(i)) is 0: #if it is active in ALMemory!
          self.active = True
          self.memory.insertData("ActorData" + str(self.number), 0)#Active signal
          #print "Activating conditionally Actor: " + str(self.number)
          
  
  def checkActivefromData(self):
    #self.memory.raiseEvent(self.eventName, "eventtest")
    index = 0
    self.dataMatched = True
    for i in self.inputs:
      v = self.memory.getData(self.sd.getDataName(i))
      if self.conditionType is 0:
         if not (v > self.hyperboxesDataCondition[index][0] and v < self.hyperboxesDataCondition[index][1]):
           self.dataMatched = False
      index = index + 1
      return self.dataMatched

  def checkActivefromEvents(self):
    
    
    pass

    
  def recordListenedEvent(self, a, b, c):
     print "********EVENT LISTENED TO******** Event listened to by action atom" + str(self.number)
     #Put events in the event table stored in this atom.
     self.eventTable.append([a,b,c])
     
     
     pass

  
  def start(self):
    """Start actor module"""
    try:
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
        pass
    self.isRunning = False

  def exit(self):
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
