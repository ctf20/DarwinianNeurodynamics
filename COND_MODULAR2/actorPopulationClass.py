from naoqi import *
import math
import almath
from actorClass import actorClass
global actors

# create python module
class actorPopulationClass(ALModule):
  """Create an actor population instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.POP_SIZE = 10
        
    #Create a population of random actor objects.
    self.actors = [actorClass("actor", count) for count in xrange(self.POP_SIZE)]

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
      if act.timesTested < least:
        least = act.timesTested
        leastA = act.number
    return leastA
    
  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for act in self.actors:
      if act.number == inp:
        act.active = True
        act.memory.insertData("ActorData" + str(act.number), 0)#Active signal
      else:
        act.active = False
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
