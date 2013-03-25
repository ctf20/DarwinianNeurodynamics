import os
import time
from naoqi import *

#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
LOCALBROKER_NAME="localbroker"
LOCALBROKER_IP="0.0.0.0" # listen on all available interfaces
LOCALBROKER_PORT=9560
PARENTBROKER_IP=  "ctf.local" #"naoFernando.local"
PARENTBROKER_PORT=9559
broker=ALBroker(LOCALBROKER_NAME,LOCALBROKER_IP,LOCALBROKER_PORT,PARENTBROKER_IP,PARENTBROKER_PORT)

#INITIALIZATION

#Create memory manager to store dictionary of sensory and motor states
#All use of memory is through use of the memory manager module. 
from memoryManagerClass import memoryManagerClass
global memoryManager
memoryManager = memoryManagerClass("memoryManager")

from gamePopulationClass import gamePopulationClass
global gamePopulation
gamePopulation = gamePopulationClass("gamePopulation", 1)

#Create an instance of an actor population module. 
from actorPopulationClass import actorPopulationClass
global actorPopulation
actorPopulation = actorPopulationClass("actorPopulation", 1)

#Create an instance of a basic motor function module. 
from basicMotorFunctionClass import basicMotorFunctionClass
global bmf
bmf = basicMotorFunctionClass("bmf")

NUM_EXPERIMENTS = 100
EXPERIMENTS_PER_GENERATION = 1

#Create an instance of a game population module.


for i in range(NUM_EXPERIMENTS):
    print "Activation of the " + str(i) + "th Molecule ***************"
    #1. Reset the position of the robot to a resting state.
    bmf.rest()
    gamePopulation.clearMessageHistories()
    #2. Check which matched actor has been tested the least (systematic bias to lower number actors, not randomized) 
    leastTestedActiveActor = actorPopulation.getLeastTestedActiveActor()
    print "Least tried matched actor = " + str(leastTestedActiveActor)

    #3. Set all other actors to inactive and this one to active.
    actorPopulation.exclusiveActivate(leastTestedActiveActor)
    
    #4. Propogate activity through the molecule.
    for t in range(10):
        print t
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
    
    #9. Inactivate all actors 
    actorPopulation.inactivateAndCleanupMemory()
    
    if i%EXPERIMENTS_PER_GENERATION is 0:
        actorPopulation.replicateMolecules()
        
 #       actorPopulation.replicateAtoms()
       
bmf.rest()
memoryManager.exit()
actorPopulation.exit()
gamePopulation.exit()
bmf.exit()

