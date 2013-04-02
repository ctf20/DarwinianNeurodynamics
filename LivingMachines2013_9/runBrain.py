import os
import time
from naoqi import *
import random
import pickle 
import pprint
from actorClass import actorClass
#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
LOCALBROKER_NAME="localbroker"
LOCALBROKER_IP="0.0.0.0" # listen on all available interfaces
LOCALBROKER_PORT=9560
PARENTBROKER_IP=  "ctf.local" #"naoFernando.local"
PARENTBROKER_PORT=9559
broker=ALBroker(LOCALBROKER_NAME,LOCALBROKER_IP,LOCALBROKER_PORT,PARENTBROKER_IP,PARENTBROKER_PORT)

from_file = False

#INITIALIZATION

#Create memory manager to store dictionary of sensory and motor states
#All use of memory is through use of the memory manager module. 
from memoryManagerClass import memoryManagerClass
global memoryManager
memoryManager = memoryManagerClass("memoryManager")

#Create an instance of a game population module.
from gamePopulationClass import gamePopulationClass
global gamePopulation
gamePopulation = gamePopulationClass("gamePopulation", 1)

#Create an instance of an actor population module. 
from actorPopulationClass import actorPopulationClass
global actorPopulation
actorPopulation = actorPopulationClass("actorPopulation", 3, from_file)

#Create an instance of a basic motor function module. 
from basicMotorFunctionClass import basicMotorFunctionClass
global bmf
bmf = basicMotorFunctionClass("bmf")

NUM_EXPERIMENTS = 100000
EXPERIMENTS_PER_GENERATION = 1

def saveGenomes(j):
    output = open('actordata.pkl'  + str(j), 'wb')
    data1 = actorPopulation.getActorPickles()
    data = [data1]
 #   pprintpprint(data1)
    pickle.dump(data, output, -1)
    output.close()

def loadGenomes():
    print "Loading genomes"
    pkl_file = open('actordata.pkl' + str(89), 'rb')
    data1 = pickle.load(pkl_file)
 #   pprint.pprint(data1[0][3]) #Prints the pickled data of the first actor.
    #Input this data into the relavent data structures.
    actorPopulation.molecules = data1[0][0]
    print actorPopulation.molecules
    actorPopulation.moleculeFitness = data1[0][1]
    actorPopulation.totalCount = data1[0][2]
    for index, i in enumerate(data1[0][3]):
##        print data1[0][3][index][0]
##        print data1[0][3][index][1]
##        print data1[0][3][index][2]
##        print data1[0][3][index][3]
##        print data1[0][3][index][4]
##        print data1[0][3][index][5]
##        print data1[0][3][index][6]
##        print data1[0][3][index][7]
        actorPopulation.actors[data1[0][3][index][2]] = actorClass(typeA = data1[0][3][index][0], nameA = data1[0][3][index][1], count = data1[0][3][index][2], sensors = data1[0][3][index][3], messages = data1[0][3][index][4], motors = data1[0][3][index][5], function = data1[0][3][index][6], parameters = data1[0][3][index][7])
                                                                     #[self.type,           self.atomKind,   self.id,                self.sensors,           self.messages,              self.motors,                self.function,      self.parameters, ]
     
    pkl_file.close()
    

#Run a microbial GA on the actor population...
    
def runMicrobialGA():
    #First generate and get fitness of all molecules in the initial population of actors.
    for i in range(len(actorPopulation.actors)):
        if actorPopulation.actors[i].timesTested is 0 and actorPopulation.actors[i].type is "sensory":
            #print "times tested =  " + str(actorPopulation.actors[i].timesTested)
            #print actorPopulation.actors[i].type
            leastTestedActiveActor = actorPopulation.actors[i].id
            bmf.rest()
            gamePopulation.clearMessageHistories()
            actorPopulation.exclusiveActivate(leastTestedActiveActor)
            for t in range(10):
 #               print " " + str(t)

                actorPopulation.runActiveActors()
                actorPopulation.conditionalActivate()
                gamePopulation.storeObservedMessages()
        
            currentMol = actorPopulation.recordMolecule()
            #print "current mol = " + str(currentMol)
            fitAllGames = gamePopulation.getMoleculeFitness()
            print "fitness = " + str(fitAllGames)
            actorPopulation.updateFitness(currentMol, fitAllGames)
            actorPopulation.getPopFitness()
            actorPopulation.inactivateAndCleanupMemory()
    print actorPopulation.molecules
    print actorPopulation.moleculeFitness

    for i in range(1000000):
        #print actorPopulation.molecules
        r1 = random.randint(0,len(actorPopulation.molecules)-1)
        r2 = random.randint(0,len(actorPopulation.molecules)-1)
        while r1 == r2:
          r2 = random.randint(0,len(actorPopulation.molecules)-1)
          #print r2
        fit1 = getFitness(r1)
        fit2 = getFitness(r2)
        print "r1= " + str(r1) + " Fitness r1 = " + str(fit1)
        print "r2= " + str(r2) +"  Fitness r2 = " + str(fit2)
        winner = None
        looser = None
        if fit1 >= fit2:
            winner = r1
            looser = r2
        else:
            winner = r2
            looser = r1
        #parentMolecule = actorPopulation.molecules[winner]
        #3. Destroy looser molecule, and replicate the winner molecule.
        actorPopulation.microbeOverwrite(winner, looser)
        #4. Test out this newly replicated set of atoms and urn it into a molecule. 
        testNewAtoms()
 #       saveGenomes(i)
            
def testNewAtoms():
    #print "Testing new atom"
    #bmf.rest()
    gamePopulation.clearMessageHistories()
    #2. Check which matched actor has been tested the least (systematic bias to lower number actors, not randomized) 
    leastTestedActiveActor = actorPopulation.getLeastTestedActiveActor(1)
    #print "Least tried matched actor = " + str(leastTestedActiveActor)

    #3. Set all other actors to inactive and this one to active.
    actorPopulation.exclusiveActivate(leastTestedActiveActor)
    
    #4. Propogate activity through the molecule.
    for t in range(10):
 #       print "test new atoms" + str(t)
        #5.Run active actors
        actorPopulation.runActiveActors()
        #6. Activate new actors based on messages from other actors. 
        actorPopulation.conditionalActivate()
        #gamePopulation.storeObservedMessages()
        
    #7. Record the molecule.
    currentMol = actorPopulation.recordMolecule()

    #8. Assign fitness to the current molecule.
#    fitAllGames = gamePopulation.getMoleculeFitness()
#    actorPopulation.updateFitness(currentMol, fitAllGames)
    actorPopulation.inactivateAndCleanupMemory()
    
def getFitness(s):
    for index, i in enumerate(actorPopulation.molecules[s]):
        if actorPopulation.actors[i].type is "sensory":
            leastTestedActiveActor = i
            bmf.rest()
            gamePopulation.clearMessageHistories()
            actorPopulation.exclusiveActivate(leastTestedActiveActor)
            for t in range(10):
 #               print "getFitness " + str(t)

                actorPopulation.runActiveActors()
                actorPopulation.conditionalActivate()
                gamePopulation.storeObservedMessages()
            currentMol = actorPopulation.recordMolecule()
            if currentMol != s:
                print "CURRENT MOL != S"
                print "s is " + str(s)
                print "currentMol is " + str(currentMol)
                print "actorPopulation.molecules[s] = " + str(actorPopulation.molecules[s])
                print "actorPopulation.molecules[currentMol] = " + str(actorPopulation.molecules[currentMol])
                exit(0)
            fitAllGames = gamePopulation.getMoleculeFitness()
            actorPopulation.updateFitness(currentMol, fitAllGames)
            actorPopulation.getPopFitness()
            actorPopulation.inactivateAndCleanupMemory()

    return actorPopulation.moleculeFitness[currentMol]


def assess(r):
    print "Activation of the " + str(i) + "th Molecule ***************"
    #1  For k,act in self.actors.iteritems():. Reset the position of the robot to a resting state.
    bmf.rest()
    gamePopulation.clearMessageHistories()
    #2. Check which matched actor has been tested the least (systematic bias to lower number actors, not randomized) 
    leastTestedActiveActor = actorPopulation.getLeastTestedActiveActor(r)
    print "Least tried matched actor = " + str(leastTestedActiveActor)

    #3. Set all other actors to inactive and this one to active.
    actorPopulation.exclusiveActivate(leastTestedActiveActor)
    
    #4. Propogate activity through the molecule.
    for t in range(10):
        #print t
        #5.Run active actors
        actorPopulation.runActiveActors()
        #6. Activate new actors based on messages from other actors. 
        actorPopulation.conditionalActivate()
        gamePopulation.storeObservedMessages()
        
    #7. Record the molecule.
    currentMol = actorPopulation.recordMolecule()

    #8. Assign fitness to the current molecule.
    fitAllGames = gamePopulation.getMoleculeFitness()
    actorPopulation.updateFitness(currentMol, fitAllGames)
    actorPopulation.getPopFitness()
    #9. Inactivate all actors 
    actorPopulation.inactivateAndCleanupMemory()
    if r is 1:
        actorPopulation.replicateMolecules()


#LivingMachines_5 Version
        
##if from_file == True:
##    loadGenomes()
##    
###1. Generate an initial random population of individuals from the seed individual. 
##for j in range(100000):
##    for i in range(10):
##        assess(1) #Assess the newly generated molecule.
##    assess(0) #Re-assess a previously generated atom/molecule  
##    saveGenomes(j)
##


#Run Microbial GA Version
#1. Initialize population with 50 individuals randomly (done in constructor).
runMicrobialGA()

       
bmf.rest()
memoryManager.exit()
actorPopulation.exit()
gamePopulation.exit()
bmf.exit()


