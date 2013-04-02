import matplotlib.pyplot as plt
from naoqi import *
import math
import almath
import random
from actorClass import actorClass
#from gamePopulationClass import gamePopulationClass
global actors
import copy
import pickle
import itertools
import time

# create python module
class actorPopulationClass(ALModule):
  """Create an actor population instance"""
  
  def __init__(self,name, kind, from_file):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.MAX_POP_SIZE = 10
    self.mm = ALProxy("memoryManager")
    self.games = ALProxy("gamePopulation")
    self.totalCount = 0
    self.actors = {}
    #Create a molecule consisting of three atoms 
    #a. An atom taking a sensory input and writing a function of it to its ALMemory location
    if from_file is False and kind is 1:
      actor0 = actorClass(typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [141,142,143,144,145,146,147,140,139,138],messages = None, motors = None, function = "sum", parameters = None)
      self.totalCount = self.totalCount + 1
      #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
      actor1 = actorClass(typeA = "shc", nameA = "actor",count = self.totalCount,sensors = None, messages = [0], motors = None, function = "sum", parameters = [0,0,0,0,0,0,0,0,0,0])
      self.totalCount = self.totalCount + 1
      #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
      actor2 = actorClass(typeA = "motor", nameA = "actor",count = self.totalCount, sensors = None, messages = [1] , motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = None, parameters = None)
      self.totalCount = self.totalCount + 1
      self.actors = {0:actor0, 1:actor1, 2:actor2}
      
    if from_file is False and kind is 2:
      for i in range(self.MAX_POP_SIZE):
       self.actors[self.totalCount] = actorClass(typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor()],messages = None, motors = None, function = "sum", parameters = None)
       self.totalCount = self.totalCount + 1
       #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
       self.actors[self.totalCount] = actorClass(typeA = "shc", nameA = "actor",count = self.totalCount,sensors = None, messages = [self.totalCount-1], motors = None, function = "sum", parameters = [0,0,0,0,0,0,0,0,0,0])
       self.totalCount = self.totalCount + 1
       #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
       self.actors[self.totalCount] = actorClass(typeA = "motor", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = None, parameters = None)
       self.totalCount = self.totalCount + 1
    
    #Compositional Motor-Sequence Molecule Initialization. 
    if from_file is False and kind is 3:
      for i in range(self.MAX_POP_SIZE):
        self.actors[self.totalCount] = actorClass(typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [188],messages = [ self.totalCount], motors = None, function = "position", parameters = None)
        self.totalCount = self.totalCount + 1
        self.actors[self.totalCount] = actorClass(typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence", parameters = [[0], [0.2, 0.2, 0.2], [1, 1, 1]])
        self.totalCount = self.totalCount + 1
        self.actors[self.totalCount] = actorClass(typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1],  motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence", parameters = [[5], [-0.1, -0.2, -0.3], [1, 1, 1]])
        self.totalCount = self.totalCount + 1
       
    self.molecules = [] 
    self.moleculeFitness = []
    self.f = open('fitnessfile','w')
    self.fitnessHistory = []
    plt.ion()

    
    
  def getActorPickles(self):
    actorData = []
    for k,act in self.actors.iteritems():
      actorData.append(act.getPickleData())
    return [self.molecules, self.moleculeFitness, self.totalCount, actorData]

    
  def getLeastTestedActiveActor(self, r):#Chooses the actor with least timesTested to activate.

    least = 10000000
    leastA = None
#    if random.random() < r:
    for k,act in self.actors.iteritems():
       if act.type == "sensory":
          if act.timesTested < least:
              least = act.timesTested
              leastA = act.id
#    else:
#      v = self.actors.values()
#      ch = v[random.randint(0,len(v)-1)]
#      while ch.type != "sensory":
#        ch = v[random.randint(0,len(v)-1)]
#      leastA = ch.id    

    return leastA

  def flatten(self,x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(self.flatten(el))
        else:
            result.append(el)
    return result

  def getPopFitness(self):
     
    plt.close()
    popFit = []
    #print len(self.moleculeFitness)
    if len(self.moleculeFitness) is self.MAX_POP_SIZE:
      for index, i in enumerate(self.moleculeFitness):
#      print "Molecule " + str(index) + " has fitness " + str(self.moleculeFitness[index])
        popFit.append(self.moleculeFitness[index])
        merged = self.flatten(popFit)
     
        
      for i in merged:
        self.f.write(' ')
        self.f.write(str(i))
        
      self.f.write('\n')
      self.f.flush()
      self.fitnessHistory.append(merged)

      #Plot fitnesshistory
      plot1 = plt.figure()
      plt.plot(self.fitnessHistory, marker='o', linestyle='None')
      plt.draw()
    

      
      return self.fitnessHistory
    

  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for k,act in self.actors.iteritems():
      if act.id == inp:
        act.active = True
        #print "Activating actor:" + str(act.id)
        self.mm.putMemory(act.id, [1,0,0])#Active signal
      else:
        act.active = False
        #print "Inactivating actor:" + str(act.id)
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
      act.timer = 0 #Reset timer. 
      act.mm.putMemory(act.id, [0,0,0]) 

  def runMicrobialGA(self):
    r1 = random.randint(0,len(self.molecules)-1)
    r2 = random.randint(0,len(self.molecules)-1)
    while r1 is r2:
      r2 = random.randint(0,len(self.molecules)-1)
    
  def microbeOverwrite(self, winner, looser):
      newMol = []
      topographicMap = {}      
      parentMolecule = self.molecules[winner]
      
      for index, i in enumerate(parentMolecule):        
         a = self.actors[i]
         if a.messages is not  None:
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


      
      #Remove the looser molecule and corresponding atoms!
      for index, i in enumerate(self.molecules[looser]):
         # print "poping from actor dict " + str(i)
          #print self.actors[i].id
          if self.actors.has_key(i):
             del self.actors[i] #self.actors.pop(self.molecules[looser][index])
      #print "looser =  " + str(looser)
      #Remove game pointers to these atoms
      self.games.removeGameMessages(self.molecules[looser])
      del self.molecules[looser] #self.molecules.pop(looser)
      del self.moleculeFitness[looser]

      #Add the newMol atoms to the actors dictionary. 
      for index, i in enumerate(newMol):
        self.actors[newMol[index].id] = newMol[index]
#        print "new mol = " + str(newMol[index].id)
    
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

      #Structurally mutate the molecule            
      #If there is a motorP atom, then we permit a range of viable random variants.
      extraMol = []
      for index, i in enumerate(newMol):
        if newMol[index].type == "motorP":
          nm = self.copyMotorPNode(newMol[index])
          if nm is not None: 
            extraMol.append(nm)

      #Add the extramol atoms to the actors dictionary. 
      for index, i in enumerate(extraMol):
        self.actors[extraMol[index].id] = extraMol[index]
#        print "Extra mol = " + str(extraMol[index].id)

      #Add a random connection within the new molecule.
      newMol.extend(extraMol)#First make the new molecule.
      #for index, i in enumerate(newMol):
      # print "combined new mol = " + str(newMol[index].id)
      if random.random() < 0.1:
        r1 = random.randint(0,len(newMol)-1)
        while newMol[r1].type != "motorP":
          r1 = random.randint(0,len(newMol)-1)
        r2 = random.randint(0,len(newMol)-1)
        while newMol[r2].type != "motorP":
          r2 = random.randint(0,len(newMol)-1)
        self.addLink(newMol[r1], newMol[r2])

      #Delete a node randomly in the new molecule.
      deleted = 0
      del_val = -1
      for index, i in enumerate(newMol):
        if random.random() < 0.05 and deleted == 0 and len(newMol) > 3:
          #Delete a node in newMol.
            del_val = i.id
            if self.actors.has_key(i.id) and newMol[index].type == "motorP":
             del self.actors[i.id]
             del newMol[index]
             self.games.removeGameMessages([i.id])
             print "deleted actor " + str(i.id)
             deleted = 1
        if deleted == 1:
           for index2, p in enumerate(newMol):
              for index3, j in enumerate(self.actors[newMol[index2].id].messages):
                  if self.actors[newMol[index2].id].messages[index3] == del_val:
                    del self.actors[newMol[index2].id].messages[index3]
                    print "removed input message " 




      
  def addLink(self, fromA, toA):
    toA.messages.append(fromA.id)
        
  def copyMotorPNode(self, a):
    #print "Mutating motorP atom actor, STRUCTURALLY, i.e. add, an atom, upstream, downtream, in new branch."
  
    #Create new downstream motorP atom with some probability.
    if random.random() < 0.1:
         if a.messages is not  None:
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
                      
         nm = actorClass(typeA = a.type, nameA = a.atomKind, count = self.totalCount, sensors = se, messages = am, motors = mo, function = a.function, parameters = a.parameters)
         self.totalCount = self.totalCount + 1
         nm.mutate()
         return nm
    
  def replicateMolecules(self):
    #print "REPLICATING *************"
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
      
      
      fit1 = sum(self.moleculeFitness[r1])
      fit2 = sum(self.moleculeFitness[r2])
      
        
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
         if a.messages is not  None:
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
          #print "poping from actor dict " + str(i)
          #print self.actors[i].id
          if self.actors.has_key(i):
             del self.actors[i] #self.actors.pop(self.molecules[looser][index])
        #print "deleting self.molecules[looser] "
        del self.molecules[looser] #self.molecules.pop(looser)
        del self.moleculeFitness[looser]

              #self.actors.extend(newMol)
      for index, i in enumerate(newMol):
        self.actors[newMol[index].id] = newMol[index]
    
      
      #for k,act in self.actors.iteritems():
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
            

    
      #for k,act in self.actors.iteritems():
#         print "actor " + str(act.id) + "messages = " +  str(act.messages)

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
    for k,act in iter(sorted(self.actors.iteritems())):
      if act.active is True:
        mol.append(act.id)
    if mol not in self.molecules:
      self.molecules.append(mol)
      self.moleculeFitness.append([0])
#      print "Molecules = " + str(self.molecules)

    for index, i in enumerate(self.molecules):
 #     print str(mol) + " compared to " + str(self.molecules[index])
      if str(mol) == str(self.molecules[index]):
 #       print str(mol) + " is the same as "+ str(self.molecules[index])
        return index
       

    print "ERROR, WE SHOLD NOT BE HERE!!! MOL WAS NOT FOUND IN SELF>MOLECULES. "
    print "Moleculkes list = " + str(self.molecules)
    print "mol = " + str(mol)
    exit(0)
    
  def updateFitness(self, mol, fit):
 #  print "Actor molecule " + str(mol) + " fitness = " + str(self.moleculeFitness[mol])
    self.moleculeFitness[mol] = fit
    

    
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
