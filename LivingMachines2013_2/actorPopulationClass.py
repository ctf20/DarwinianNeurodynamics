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

    self.molecules = [] 
    

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

  def replicateMolecules(self):
    print "REPLICATING *************"
    print "REPLICATING *************"
    #Take a molecule from self.molecules and replicate it.
    newMol = []
    topographicMap = {} #Dictionary linking parent key to offspring value 
    if len(self.molecules) > 0:
      #print self.molecules[len(self.molecules)-1]
      parentMolecule = self.molecules[len(self.molecules)-1]
      #Check the connectivity of the parent molecule
##      print "Parent molecule connectivity PRE-COPY " 
##      for index, i in enumerate(parentMolecule):
##        print "atom" + str(self.actors[i].id) + "gets input from atoms:"
##        if self.actors[i].messages is not None:
##          for index2, j in enumerate(self.actors[i].messages):
##            print "atom " + str(j)
##          
      for index, i in enumerate(parentMolecule):        
         a = self.actors[i]
         if a.messages is not None:
           am = list(a.messages)
         else:
           am = None
         if a.sensors is not None:
           se = list(a.sensors)
         else:
           se = None
         if a.motors is not None:
           mo = list(a.motors)
         else:
           mo = None
                      
         newMol.append(actorClass(typeA = a.type, nameA = a.atomKind, count = len(self.actors)+index, sensors = se, messages = am, motors = mo, function = a.function, parameters = a.parameters))         
         topographicMap[str(a.id)] = newMol[len(newMol)-1].id

         
      self.actors.extend(newMol)
      for act in self.actors:
        print "actor " + str(act.id) + "messages = " +  str(act.messages)

      #self.actors[4].messages[0] = 10
      for i in parentMolecule:
        if self.actors[topographicMap[str(i)]].messages is not None:
          for ind, j in enumerate(self.actors[topographicMap[str(i)]].messages):
           self.actors[topographicMap[str(i)]].messages[ind] = topographicMap[str(self.actors[i].messages[ind])]

      for act in self.actors:
        print "actor " + str(act.id) + "messages = " +  str(act.messages)

      #Go through the parent molecule
#      for index, i in enumerate(parentMolecule):
#        if self.actors[topographicMap[str(i)]].messages is not None:
#          for index2, j in enumerate(self.actors[topographicMap[str(i)]].messages):
#            j = topographicMap[str(self.actors[i].messages[index2])]

        
      #Check the connectivity of the copied molecule
      print "Offspring molecule connectivity" 
      for index, i in enumerate(newMol):
        print "atom" + str(i.id) + "gets input from atoms:"
        if i.messages is not None:
          for index2, j in enumerate(i.messages):
            print "atom " + str(j)

    
      #Check the connectivity of the parent molecule
      print "Parent molecule connectivity POST-COPY " 
      for index, i in enumerate(parentMolecule):
        print "atom" + str(self.actors[i].id) + "gets input from atoms:"
        if self.actors[i].messages is not None:
          for index2, j in enumerate(self.actors[i].messages):
            print "atom " + str(j)
          
    
         
 #   for i in newMol:
#      print i.id

      

    
    pass
    
  def recordMolecule(self):
    mol = []
    for act in self.actors:
      if act.active is True:
        mol.append(act.id)
    if mol not in self.molecules:
      self.molecules.append(mol)
    print "Molecules = " + str(self.molecules)
        
        
  
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
