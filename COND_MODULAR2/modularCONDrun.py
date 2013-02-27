# Retrieve environment variables
import os
import time

#NAO_IP=os.environ["NAO_IP"]
#NAO_PORT=int(os.environ["NAO_PORT"])

# Create a local broker
from naoqi import *
LOCALBROKER_NAME="localbroker"
LOCALBROKER_IP="0.0.0.0" # listen on all available interfaces
LOCALBROKER_PORT=9560
PARENTBROKER_IP="naoFernando.local" #"ctf.local" 
PARENTBROKER_PORT=9559
broker=ALBroker(LOCALBROKER_NAME,LOCALBROKER_IP,LOCALBROKER_PORT,PARENTBROKER_IP,PARENTBROKER_PORT)

# Instantiate the modules to be used for co-evolutionary Darwinian Neurodynamics.

#from atom0_moduleClass import atom0_moduleClass
#global atom0_module
#atom0_module = atom0_moduleClass("atom0_module") #This module runs on my computer, not on the NAO 

#A Library of modules (i.e. innate competences) which our algorithm assumes exists already. 

from atom1_moduleClass import atom1_moduleClass
global atom1_module
atom1_module = atom1_moduleClass("atom1_module") #Moves head in relation to visual movement detected. 

from atom2_moduleClass import atom2_moduleClass
global atom2_module
atom2_module = atom2_moduleClass("atom2_module") #Calls a function in response to a list of possible words

from atom3_moduleClass import atom3_moduleClass
global atom3_module
atom3_module = atom3_moduleClass("atom3_module") #Moves head as a function of localized sound. 

from atom4_moduleClass import atom4_moduleClass
global atom4_module
atom4_module = atom4_moduleClass("atom4_module") #Gives text output when an object is recognized 

from atom5_moduleClass import atom5_moduleClass
global atom5_module
atom5_module = atom5_moduleClass("atom5_module") #Landmark Detection module prints info about landmarks detected


#The atoms should potentially have access to a range of interesting events (sometimes high-level events)
#The events that our system will be able to directly use as inputs to behavioural atoms ae below
#In effect they are kinds fo INNATE competences that we assume NAO has and needs not to learn.

#This code opens and instantiates the modules.
#Proxies to these modules can access them.

#atom1_module.start()
#atom2_module.start()
#atom3_module.start()
#atom4_module.start()
#atom5_module.start()
#time.sleep(5)
#atom1_module.finish()
#atom2_module.finish()
#atom3_module.finish()
#atom4_module.finish()
#for i in range(0,5):
#    atom5_module.getNaoSpaceLandmark()

#atom5_module.finish()
