from naoqi import *
import math
import almath
import random
from actorClass import actorClass
global actors
import copy

# create python module
class actorPopulationClass(ALModule):
  """Create an actor population instance"""
  
  def __init__(self,name, type):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.mm = ALProxy("memoryManager")

    #Create a molecule consisting of three atoms 
    #a. An atom taking a sensory input and writing a function of it to its ALMemory location
    actor0 = actorClass(typeA = "sensory", nameA = "actor",count = 0, sensors = [10,10],messages = None, motors = None, function = "sum", parameters = None)
    #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
    actor1 = actorClass(typeA = "shc", nameA = "actor",count = 1,sensors = None, messages = [0], motors = None, function = "sum", parameters = [0,0])
    #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
    actor2 = actorClass(typeA = "motor", nameA = "actor",count = 2, sensors = None, messages = [1] , motors = [6], function = None, parameters = None)
    self.actors = [actor0, actor1, actor2]

  def getLeastTestedActiveActor(self):#Chooses the actor with least timesTested to activate. 
    least = 10000000
    leastA = None
    for act in self.actors:
      if act.type is "sensory":
        if act.timesTested < least:
            least = act.timesTested
            leastA = act.id

    return leastA

  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for act in self.actors:
      if act.id == inp:
        act.active = True
        print "Activating actor:" + str(act.id)
        self.mm.putMemory(act.id, [1,0,0])#Active signal
      else:
        act.active = False
        print "Inactivating actor:" + str(act.id)
        act.mm.putMemory(act.id,[0,0,0]) #Inactive signal
    pass

  def runActiveActors(self):
    for act in self.actors:
      if act.active is True:
        act.act()

  def conditionalActivate(self):
    for act in self.actors:
      act.conditionalActivate()
   
  def inactivateAndCleanupMemory(self):
    for act in self.actors:
      act.active = False
      act.mm.putMemory(act.id, [0,0,0]) 
  
  def replicateAtoms(self):
     for act in self.actors:
         if act.id is 0:
             print "REPLICATING *************"
             cop = actorClass(typeA = act.type, nameA = act.atomKind, count = len(self.actors), sensors = act.sensors, messages = act.messages, motors = act.motors, function = act.function, parameters = act.parameters)
             #Check that the downstream atoms get input from this new copied atom.
             #1.Go through all the atoms checking if their input list includes the act atom.
             for others in self.actors:
                 if others is not act:
                     if others.messages is not None:
                         for i in others.messages:
                             if i is act.id:
                                 others.messages.append(cop.id) #Get input from offspring actor to the downstream act that also got input from the offspring's parent. 
             self.actors.append(cop)
             
             
  def exit(self):
    print "Exiting actor populaton"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
