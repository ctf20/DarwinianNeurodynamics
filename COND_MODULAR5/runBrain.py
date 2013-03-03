import os
import time
from naoqi import *

#TO DO 1> When an actor changes its active ON/OFF state then
#always update its relavent ActorData key/value pair in ALMemory
#Because other actor atoms use this value to determine if they should also become active.

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

#Create an instance of a shared data class that stores indexed pointers to data and events.
from sharedDataClass import sharedDataClass
global sharedData
sharedData = sharedDataClass("sharedData")

#Create an instance of an actor population module. 
from actorPopulationClass import actorPopulationClass
global actorPopulation
#actorPopulation = actorPopulationClass("actorPopulation")
actorPopulation = actorPopulationClass("actorPopulation", 1)

#Create an instance of a basic motor function module. 
from basicMotorFunctionClass import basicMotorFunctionClass
global bmf
bmf = basicMotorFunctionClass("bmf")

#START MAIN SENSORIMOTOR LOOP (WITH FIXED ACTORS,NO EVOLUTION)

##
##simOn = True
##i = 0
##while simOn is True:
##    print i
##    i = i +1
##    #1. Determine actor activation state from data.
##    actorPopulation.activateActorsfromData()
##    #2. Determine actor activation state from events.
##    actorPopulation.activateActorsfromEventList()
##    #3. Execute active actors (i.e. do motor actions and write to memory, and raise events).
##    actorPopulation.activateActors() #
##    if i is 10:
##        simOn = False
##
##    pass

#START MAIN FITNESS EVALUATION ALGORITHM.

simOn = True
i = 0
while simOn is True:
    #RESET ROBOT AND START WITH A NEW SINGLE ACTIVE ACTOR BASED ON SENSORY STATE.
    #I.E. NOT CONDITIONED ON EXISTING ACTOR ACTIVITY. 
    print i
    #1. Reset the position of the robot to a resting state.
    bmf.rest()
    #2. Determine which actor atoms are active based on pure sensory state (not data state)
    #[Remember to reset data state when an actor becomes inactive from a previous molecule executio]
    matchedActors = actorPopulation.activateActorsfromData()
    #print "Matched actors = " + str(matchedActors)
    #3. Check which matched actor has been tested the least (systematic bias to lower number actors, not randomized) 
    leastTestedActiveActor = actorPopulation.getLeastTestedActiveActor()
    #print "Least tried matched actor = " + str(leastTestedActiveActor)
    #4. Set all other actors to inactive and this one to active.
    actorPopulation.exclusiveActivate(leastTestedActiveActor)
    #5. NEW BASAL-GANGLIA LOOP IN WHICH ACTIVE ACTORS ACTIVATE OTHER ACTORS THROUGH ALMEMORY TO FORM A TEMPORAL ACTOR MOLECULE
    for t in range(50):
        print t
        #5.1. Run the policy of each of the currently active actors.
        actorPopulation.runActiveActors()
        #5.2. Activate new actors CONDITIONED ON EXISTING ACTOR ACTIVITY
        #[The basal ganglia simply conditions on internal activity]
        actorPopulation.conditionalActivate()
    actorPopulation.inactivateAndCleanupMemory()    
        
    i = i +1
    if i is 30:
        simOn = False

bmf.rest()
sharedData.exit()
actorPopulation.exit()

