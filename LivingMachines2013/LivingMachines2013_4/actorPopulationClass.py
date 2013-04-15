from naoqi import *
import math
import almath
import random
from actorClass import actorClass
#from gamePopulationClass import gamePopulationClass
global actors
import copy

# create python module
class actorPopulationClass(ALModule):
  """Create an actor population instance"""
  
  def __init__(self,name, type):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.mm = ALProxy("memoryManager")
    self.games = ALProxy("gamePopulation")
    self.totalCount = 0
    #Create a molecule consisting of three atoms 
    #a. An atom taking a sensory input and writing a function of it to its ALMemory location
    actor0 = actorClass(typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [10,10],messages = None, motors = None, function = "sum", parameters = None)
    self.totalCount = self.totalCount + 1
    #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
    actor1 = actorClass(typeA = "shc", nameA = "actor",count = self.totalCount,sensors = None, messages = [0], motors = None, function = "sum", parameters = [0,0])
    self.totalCount = self.totalCount + 1
    #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
    actor2 = actorClass(typeA = "motor", nameA = "actor",count = self.totalCount, sensors = None, messages = [1] , motors = [6], function = None, parameters = None)
    self.totalCount = self.totalCount + 1
    self.actors = {0:actor0, 1:actor1, 2:actor2}

    self.molecules = [] 
    self.moleculeFitness = []
    self.MAX_POP_SIZE = 20
  
  def getLeastTestedActiveActor(self):#Chooses the actor with least timesTested to activate. 
    least = 10000000
    leastA = None
    for k,act in self.actors.iteritems():
      if act.type is "sensory":
        if act.timesTested < least:
            least = act.timesTested
            leastA = act.id

    return leastA

  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for k,act in self.actors.iteritems():
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
    for k,act in self.actors.iteritems():
      if act.active is True:
        act.act()

  def conditionalActivate(self):
    for k,act in self.actors.iteritems():
      act.conditionalActivate()
   
  def inactivateAndCleanupMemory(self):
    for k,act in self.actors.iteritems():
      act.active = False
      act.mm.putMemory(act.id, [0,0,0]) 

  def replicateMolecules(self):
    print "REPLICATING *************"
 #   print "REPLICATING *************"
    #Take a molecule from self.molecules and replicate it.
    newMol = []
    topographicMap = {} #Dictionary linking parent key to offspring value 
    if len(self.molecules) > 0:

  
      #Choose which parent molecule to replicate based on its fitness.
      #Choose two molecules randomly (Use microbial selection)
      r1 = random.randint(0,len(self.molecules)-1)
      r2 = random.randint(0,len(self.molecules)-1)
      if len(self.molecules) > 2:
        while r1 is r2:
          r2 = random.randint(0,len(self.molecules)-1)
      
      if len(self.moleculeFitness[r1]) > 1:
        fit1 = sum(self.moleculeFitness[r1][len(self.moleculeFitness[r1])-1])
      else:
        fit1 = 1
        
      if len(self.moleculeFitness[r2]) > 1:
        fit2 = sum(self.moleculeFitness[r2][len(self.moleculeFitness[r2])-1])
      else:
        fit2 = 0
        
      print "Fitness r1 = " + str(fit1)
      print "Fitness r2 = " + str(fit2)
      winner = None
      looser = None
      if fit1 > fit2:
        winner = r1
        looser = r2
      else:
        winner = r2
        looser = r1
      parentMolecule = self.molecules[winner]
        
      
      #parentMolecule = self.molecules[len(self.molecules)-1]
      
      
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
                      
         newMol.append(actorClass(typeA = a.type, nameA = a.atomKind, count = self.totalCount, sensors = se, messages = am, motors = mo, function = a.function, parameters = a.parameters))
         self.totalCount = self.totalCount + 1
         newMol[len(newMol)-1].mutate()
         topographicMap[str(a.id)] = newMol[len(newMol)-1].id

      if len(self.molecules) > self.MAX_POP_SIZE:
        #Remove the looser molecule and corresponding atoms!
        for index, i in enumerate(self.molecules[looser]):
          self.actors.pop(self.molecules[looser][index])
        self.molecules.pop(looser)

              #self.actors.extend(newMol)
      for index, i in enumerate(newMol):
        self.actors[newMol[index].id] = newMol[index]
    
      
 #     for act in self.actors:
#        print "actor " + str(act.id) + "messages = " +  str(act.messages)

      #Copy connectivity. 
      for i in parentMolecule:
        if self.actors[topographicMap[str(i)]].messages is not None:
          for ind, j in enumerate(self.actors[topographicMap[str(i)]].messages):
           self.actors[topographicMap[str(i)]].messages[ind] = topographicMap[str(self.actors[i].messages[ind])]

      #Update game messages.
      for i in parentMolecule:
        if self.actors[topographicMap[str(i)]].messages is not None:
          for ind, j in enumerate(self.actors[topographicMap[str(i)]].messages):
            #Check all games observing old message and make them also view the new message 
            self.games.updateGameMessages(self.actors[i].messages[ind],  topographicMap[str(self.actors[i].messages[ind])])
            

    
      for k,act in self.actors.iteritems():
        print "actor " + str(act.id) + "messages = " +  str(act.messages)

      #Go through the parent molecule
#      for index, i in enumerate(parentMolecule):
#        if self.actors[topographicMap[str(i)]].messages is not None:
#          for index2, j in enumerate(self.actors[topographicMap[str(i)]].messages):
#            j = topographicMap[str(self.actors[i].messages[index2])]

##        
##      #Check the connectivity of the copied molecule
##      print "Offspring molecule connectivity" 
##      for index, i in enumerate(newMol):
##        print "atom" + str(i.id) + "gets input from atoms:"
##        if i.messages is not None:
##          for index2, j in enumerate(i.messages):
##            print "atom " + str(j)
##
##    
##      #Check the connectivity of the parent molecule
##      print "Parent molecule connectivity POST-COPY " 
##      for index, i in enumerate(parentMolecule):
##        print "atom" + str(self.actors[i].id) + "gets input from atoms:"
##        if self.actors[i].messages is not None:
##          for index2, j in enumerate(self.actors[i].messages):
##            print "atom " + str(j)
##          
    
 #   for i in newMol:
#      print i.id

    pass
    
  def recordMolecule(self):
    mol = []
    for k,act in self.actors.iteritems():
      if act.active is True:
        mol.append(act.id)
    if mol not in self.molecules:
      self.molecules.append(mol)
      self.moleculeFitness.append([0])
    print "Molecules = " + str(self.molecules)

    for index, i in enumerate(self.molecules):
      if mol is self.molecules[index]:
        return index

          
        
  def updateFitness(self, mol, fit):
    self.moleculeFitness[mol].append(fit)
    print "Actor molecule " + str(mol) + " fitness = " + str(self.moleculeFitness[mol])


    
##  def replicateAtoms(self):
##     for k,act in self.actors.iteritems():
##         if act.id is 0:
##             print "REPLICATING *************"
##             cop = actorClass(typeA = act.type, nameA = act.atomKind, count = self.totalCount, sensors = act.sensors, messages = act.messages, motors = act.motors, function = act.function, parameters = act.parameters)
##             self.totalCount = self.totalCount + 1 
##             #Check that the downstream atoms get input from this new copied atom.
##             #1.Go through all the atoms checking if their input list includes the act atom.
##             for k,others in self.actors.iteritems():
##                 if others is not act:
##                     if others.messages is not None:
##                         for i in others.messages:
##                             if i is act.id:
##                                 others.messages.append(cop.id) #Get input from offspring actor to the downstream act that also got input from the offspring's parent. 
##             self.actors.append(cop)
##


             
  def exit(self):
    print "Exiting actor populaton"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
