from naoqi import *
import math
import almath
from actorClass import actorClass
global actors

# create python module
class actorPopulationClass(ALModule):
  """Create an actor population instance"""
  
  def __init__(self,name, type):
    ALModule.__init__(self,name)
    self.isRunning=True

    if type is 0:
      self.POP_SIZE = 10
      #Create a population of random actor objects.
      self.actors = [actorClass("actor", count) for count in xrange(self.POP_SIZE)]
    if type is 1:#HAND DESIGNED (BUT EVOLVABLE) SHC OPTIMIZATION ACTOR MOLECULE 
      self.POP_SIZE = 3
      self.actors = self.createSHCchain()

  def createSHCchain(self):
    #Construct the following specifically interconnected actors into an actor molecule.
    
    #1. A function actor that takes two sensory inputs (e.g. accelerometer z and accelerometer y)
    #   and outputs the product of them as a message.
    actor1 = actorClass(name = "actor",count = 0, inputs = [141,142], function = "product", typeA = 1) #Species input vector and the function.
    #ARGUMENTS: name, number,data inputs, function type
    
    #2. A SHC actor that reads that message as a fitness input and outputs a parameter vector as a message.
    actor2 = actorClass(name = "actor",count = 1,inputs = [189], messageInputs = [1], function = None, typeA = 3)
    #ARGUMENTS: name, number, data inputs, message inputs, 3 = optimization actor. 
    
    #3. A message to motor function that reads the above message and outputs a motor command



    #Make into an actor array 
    actors = [actor1, actor2]
    
    return actors
    
    pass

  def activateActorsfromData(self):
    matchedActors = []
    #Go through each actor determining whether it is active or not.
    for act in self.actors:
      matchedActors.append(act.checkActivefromData()) #Updates data_active state of actor. 
    return matchedActors

  def activateActorsfromEventList(self):
    for act in self.actors:
      act.checkActivefromEvents() #Updates event_active state of actor. 
    pass
  
  def getLeastTestedActiveActor(self):
    least = 10000
    leastA = None
    for act in self.actors:
      if act.dataMatched is True:#0 is active!?!? 
        if act.timesTested < least:
          least = act.timesTested
          leastA = act.number
          
    return leastA
    
  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for act in self.actors:
      if act.number == inp:
        act.active = True
        print "Activating actor:" + str(act.number)
        act.memory.insertData("ActorData" + str(act.number), 0)#Active signal
      else:
        act.active = False
        print "Inactivating actor:" + str(act.number)
        act.memory.insertData("ActorData" + str(act.number), 1) #Inactive signal
        
   # print "Active actors are:"
   # for act in self.actors:
   #   print str(act.active) + " " 
    
    pass

  def runActiveActors(self):
    #1. Execute the motor action of the active actors.
    for act in self.actors:
      if act.active is True:
        act.act()
    
    pass
  
  def conditionalActivate(self):
    #2. Determine new active action atoms based on ActorKeys in ALMemory.
    for act in self.actors:
      act.conditionalActivate()
    pass    

  def inactivateAndCleanupMemory(self):
    for act in self.actors:
      act.active = False
      act.memory.insertData("ActorData" + str(act.number), 1) #Inactivate in ALMemory
      act.memory.insertData("ActorMesg" + str(act.number) ,[0])# Switch off messaging from all actors. 
    pass 
  
  def start(self):
    """Start actor population module"""
    try:
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
        pass
    except:
        pass
    self.isRunning = False

  def exit(self):
    print "Exiting actor populaton"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
