import matplotlib.pyplot as plt
from naoqi import *
import math
import almath
import random
from actorClass import actorClass
#from gamePopulationClass import gamePopulationClass
##global actors
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
    self.MAX_POP_SIZE = 30
    self.mm = ALProxy("memoryManager")
    self.games = ALProxy("gamePopulation")
    self.totalCount = 0
    self.actors = {}

    #Create a molecule consisting of three atoms 
    #a. An atom taking a sensory input and writing a function of it to its ALMemory location
    if from_file is False and kind is 1:
      actor0 = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [141,142,143,144,145,146,147,140,139,138],messages = None, messageDelays = None, motors = None, function = "sum", parameters = None)
      self.totalCount = self.totalCount + 1
      #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
      actor1 = actorClass(copyA = False, atomA = None, typeA = "shc", nameA = "actor",count = self.totalCount,sensors = None, messages = [0], messageDelays = [1], motors = None, function = "sum", parameters = [0,0,0,0,0,0,0,0,0,0])
      self.totalCount = self.totalCount + 1
      #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
      actor2 = actorClass(copyA = False, atomA = None, typeA = "motor", nameA = "actor",count = self.totalCount, sensors = None, messages = [1] , messageDelays = [1], motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = None, parameters = None)
      self.totalCount = self.totalCount + 1
      self.actors = {0:actor0, 1:actor1, 2:actor2}
      
    if from_file is False and kind is 2:
      for i in range(self.MAX_POP_SIZE):
       self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor(),self.mm.getRandomSensor()],messages = None,messageDelays = None,motors = None, function = "sum", parameters = None)
       self.totalCount = self.totalCount + 1
       #b. An atom taking an ALMemory location of the first atom and doing SHC with it, and a downstream atom.
       self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "shc", nameA = "actor",count = self.totalCount,sensors = None, messages = [self.totalCount-1], messageDelays = [1], motors = None, function = "sum", parameters = [0,0,0,0,0,0,0,0,0,0])
       self.totalCount = self.totalCount + 1
       #c. An atom that takes an ALMemory location and converts it into a motor action (as specified by its parameters)
       self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motor", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1], motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = None, parameters = None)
       self.totalCount = self.totalCount + 1
    
    #Compositional Motor-Sequence Molecule Initialization. 
    if from_file is False and kind is 3:
      for i in range(self.MAX_POP_SIZE):
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        self.totalCount = self.totalCount + 1
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1],motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        self.totalCount = self.totalCount + 1
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
        self.totalCount = self.totalCount + 1

    #Compositional Motor-Sequence Molecule Initialization. 
    if from_file is False and kind is 4:
      for i in range(self.MAX_POP_SIZE):
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        self.totalCount = self.totalCount + 1
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorIzh", nameA = "actor",count = self.totalCount,
                                                  sensors = [self.mm.getRandomSensor(), self.mm.getRandomSensor()], messages = [self.totalCount-1] , messageDelays = [1],
                                                  motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence",
                                                  parameters = [[random.randint(0,3)],
                                                  [[random.sample(range(100), 5)], [random.sample(range(100), 5)], [random.sample(range(100), 5)], [random.sample(range(100), 5)], [random.sample(range(100), 5)]],
                                                  [[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
                                                  [random.random()-0.5 for x in range(0, 5)]], [1, 1, 1]])
        self.totalCount = self.totalCount + 1
##        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
##        self.totalCount = self.totalCount + 1
        
        self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorIzh", nameA = "actor",count = self.totalCount,
                                                  sensors = [self.mm.getRandomSensor(), self.mm.getRandomSensor()], messages = [self.totalCount-1], messageDelays = [2],
                                                  motors = [self.mm.getRandomMotor(),self.mm.getRandomMotor(),self.mm.getRandomMotor()], function = "sequence",
                                                  parameters = [[random.randint(0,3)],
                                                  [[random.sample(range(100), 5)], [random.sample(range(100), 5)], [random.sample(range(100), 5)], [random.sample(range(100), 5)]],
                                                  [[random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)], [random.random()-0.5 for x in range(0, 5)],
                                                  [random.random()-0.5 for x in range(0, 5)]], [1, 1, 1]])
        self.totalCount = self.totalCount + 1

    if from_file is False:
        self.molecules = [] 
        self.moleculeFitness = []
        self.f = open('fitnessfile','w')
        self.fitnessHistory = []
        plt.ion()
      
    if from_file is True:
        self.loadGenomes(5)
        self.f = open('fitnessfile','w')
        self.fitnessHistory = []
        plt.ion()
  
  def loadGenomes(self, i):
    print "Loading genomes"
    pkl_file = open('actordata.pkl' + str(i), 'rb')
    data1 = pickle.load(pkl_file)
 #   pprint.pprint(data1[0][3]) #Prints the pickled data of the first actor.
    #Input this data into the relavent data structures.
    self.molecules = data1[0][0]
    print self.molecules
    self.moleculeFitness = data1[0][1]
    print self.moleculeFitness
    self.totalCount = data1[0][2]
    print self.totalCount
    for index, i in enumerate(data1[0][3]):
##        print data1[0][3][index][0]
##        print data1[0][3][index][1]
##        print data1[0][3][index][2]
##        print data1[0][3][index][3]
##        print data1[0][3][index][4]
##        print data1[0][3][index][5]
##        print data1[0][3][index][6]
##        print data1[0][3][index][7]
##        print data1[0][3][index][8]

       if data1[0][3][index][4] is not  None:
         am = list(data1[0][3][index][4])
       else:
         am = None
       if data1[0][3][index][5] is not None:
         amd = list(data1[0][3][index][5])
       else:
         amd = None
       if data1[0][3][index][3] is not None:
         se = list(data1[0][3][index][3])
       else:
         se = None
       if data1[0][3][index][6] is not None:
         mo = list(data1[0][3][index][6])
       else:
         mo = None
       if data1[0][3][index][8] is not None:
         pa = list(data1[0][3][index][8])
       else:
         pa = None
         
       self.actors[data1[0][3][index][2]] = actorClass(copyA = True, atomA = data1[0][3][index], typeA = data1[0][3][index][0], nameA = data1[0][3][index][1], count = data1[0][3][index][2], sensors = se, messages = am, messageDelays = amd,  motors = mo, function = data1[0][3][index][7], parameters = pa)                                                                     #[self.type,           self.atomKind,   self.id,                self.sensors,           self.messages,              self.motors,                self.function,      self.parameters, ]
     
    pkl_file.close()

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
    plt.figure(1)
    plt.clf()
    popFit = []
    #print len(self.moleculeFitness)
    if len(self.moleculeFitness) is self.MAX_POP_SIZE:
    #if True:
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
      
      
##      print self.fitnessHistory
      trans = [list(i) for i in zip(*self.fitnessHistory)]
      for index, i in enumerate(trans):
        plt.plot(trans[index], marker='o', linestyle='None')
      plt.draw()
    

      
      return self.fitnessHistory
    

  def exclusiveActivate(self, inp):
    #Set all actors apart from inp to zero activity. 
    for k,act in self.actors.iteritems():
      if act.id == inp:
        act.active = True
        act.activeHist = True
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
      act.activeHist = False
      act.timer = 0 #Reset timer.
      act.timer2 = 0
      act.mm.putMemory(act.id, [0,0,0]) 

#  def runMicrobialGA(self):
#    r1 = random.randint(0,len(self.molecules)-1)
#    r2 = random.randint(0,len(self.molecules)-1)
#    while r1 is r2:
#      r2 = random.randint(0,len(self.molecules)-1)
    
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
         if a.messageDelays is not None:
           amd = list(a.messageDelays)
         else:
           amd = None
         if a.sensors is not None:
           se = list(a.sensors)
         else:
           se = None
         if a.motors is not None:
           mo = list(a.motors)
         else:
           mo = None
         if a.parameters is not None:
           par = list(a.parameters)
         else:
           par = None
                      
         newMol.append(actorClass(copyA = True, atomA = a, typeA = a.type, nameA = a.atomKind, count = self.totalCount, sensors = se, messages = am, messageDelays = amd, motors = mo, function = a.function, parameters = par))
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
 #     self.games.removeGameMessages(self.molecules[looser])
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
 #     for i in parentMolecule:
#        if self.actors[topographicMap[str(i)]].messages is not None:
#          for ind, j in enumerate(self.actors[topographicMap[str(i)]].messages):
#            #Check all games observing old message and make them also view the new message 
#            self.games.updateGameMessages(self.actors[i].messages[ind],  topographicMap[str(self.actors[i].messages[ind])])

      #Structurally mutate the molecule            
      #If there is a motorP atom, then we permit a range of viable random variants.
      extraMol = []
      done = 0
      for index, i in enumerate(newMol):
        if (newMol[index].type == "motorP" or newMol[index].type == "motorIzh") and done == 0:
          nm = self.copyMotorPNode(newMol[index])
          done = 1
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
##      if random.random() < 1:
##        r1 = random.randint(0,len(newMol)-1)
##        while newMol[r1].type != "motorP":
##          r1 = random.randint(0,len(newMol)-1)
##        r2 = random.randint(0,len(newMol)-1)
##        while newMol[r2].type != "motorP":
##          r2 = random.randint(0,len(newMol)-1)
##        self.addLink(newMol[r1], newMol[r2])

      #Delete a node randomly in the new molecule.
      deleted = 0
      for index, i in enumerate(newMol):
        del_val = -1
        
        if random.random() < 0.05 and deleted == 0 and len(newMol) >= 3 and (newMol[index].type == "motorP" or newMol[index].type == "motorIzh"):
          print "Length new mol before deletion = " + str(len(newMol))
          #Go through the molecules data structure removing this atom id.
          for index4,q in enumerate(self.molecules):
            for index5, q2 in enumerate(self.molecules[index4]):
              if q2 == i.id:
#                del self.molecules[index3][index4]
                del self.molecules[index4][index5]

                
          #Delete a node in newMol.
          del_val = i.id
          if self.actors.has_key(i.id):
            del self.actors[i.id]
            del newMol[index]
 #           self.games.removeGameMessages([i.id])
            print "deleted actor " + str(i.id)
            deleted = 1
          print "Length new mol after deletion = " + str(len(newMol))
        if deleted == 1:
           for index2, p in enumerate(newMol):
              for index3, j in enumerate(self.actors[newMol[index2].id].messages):
                  if self.actors[newMol[index2].id].messages[index3] == del_val:
                    del self.actors[newMol[index2].id].messages[index3]
                    del self.actors[newMol[index2].id].messageDelays[index3]
                    print " removed input message "
        

      
  def addLink(self, fromA, toA):
    toA.messages.append(fromA.id)
    toA.messageDelays.append([1])
        
  def copyMotorPNode(self, a):
    #print "Mutating motorP atom actor, STRUCTURALLY, i.e. add, an atom, upstream, downtream, in new branch."
  
    #Create new downstream motorP atom with some probability.
    if random.random() < 0.05:
         if a.messages is not  None:
           am = list(a.messages)
         else:
           am = None
         if a.messageDelays is not None:
           amd = list(a.messageDelays)
         else:
           amd = None
         if a.sensors is not None:
           se = list(a.sensors)
         else:
           se = None
         if a.motors is not None:
           mo = list(a.motors)
         else:
           mo = None
         if a.parameters is not None:
           par = list(a.parameters)
         else:
           par = None

         #Lateral mutation
         nm = None
         if random.random() < 0.5:
           nm = actorClass(copyA = True, atomA = a, typeA = a.type, nameA = a.atomKind, count = self.totalCount, sensors = se, messages = am, messageDelays = amd, motors = mo, function = a.function, parameters = par)
         else:
           #Downstream mutation
           nm = actorClass(copyA = True, atomA = a, typeA = a.type, nameA = a.atomKind, count = self.totalCount, sensors = se, messages = list([a.id]), messageDelays = [1], motors = mo, function = a.function, parameters = par)          
         self.totalCount = self.totalCount + 1
         nm.mutate()
         return nm
    

  def checkMolecule(self):
    mol = []
    for k,act in iter(sorted(self.actors.iteritems())):
      if act.activeHist is True:
        mol.append(act.id)
    if mol not in self.molecules:
      print"MOLECULE NOT FOUND!!!"
      return -1

    for index, i in enumerate(self.molecules):
 #     print str(mol) + " compared to " + str(self.molecules[index])
      if str(mol) == str(self.molecules[index]):
 #       print str(mol) + " is the same as "+ str(self.molecules[index])
        return index
      
  def recordMolecule(self):
    mol = []
    for k,act in iter(sorted(self.actors.iteritems())):
      if act.activeHist is True:
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
