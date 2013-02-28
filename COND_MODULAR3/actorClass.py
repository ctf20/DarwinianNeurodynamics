from naoqi import *
import math
import almath
import random
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.neuralnets import NNregression 
from pybrain.tools.plotting import MultilinePlotter

#TO DO 1. Create a new kind of actor that writes the output of a function of its inputs to ALMemory, but doesnt make any motor movements.
#TO DO 2. An actor may read from the ActorMesg values. 

# create python module
class actorClass(ALModule):
  """Create an actor instance"""
  
  def __init__(self,name, count):
    ALModule.__init__(self,name)
    print "Making actor:" + str(count)
    self.isRunning=True

    #************RANDOMLY GENERATE THE ACTOR GENOTYPE HERE********************
    #GENOTYPE [Makes a random genotype]
    self.number = count

    #Create a proxy to the sharedData module.
    self.sd = ALProxy("sharedData")
    #And to ALMemory
    self.memory = ALProxy("ALMemory")    
    self.motion = ALProxy("ALMotion", "ctf.local", 9559)
    self.Body = self.motion.getLimits("Body")
    self.set_stiffness(1.0)
    
    self.sd.start()

    #Make a list of ALMemory state inputs that this actor will check regularly. 
    self.inputs = self.sd.getRandomMemoryInputs(5)
    #Make a list of ALMemory mesg inputs that this actor will check regularly.
    self.mesgInputs = self.sd.getRandomMemoryMesgInputs(1) #By default get one message only.
    
    print "Regular data inputs to actor " + str(count) + " = " + str(self.inputs)

    #Make a list of ALMemory Events that this actor will subscribe and listen to.
    self.eventInputs = self.sd.getRandomEventInputs(1)
    print self.eventInputs
    self.eventName = self.sd.getEventName(self.eventInputs[0])
    #Create a listener for these events to record them in recordListenedEvent
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
      pass
    print self.eventName
    self.memory.subscribeToEvent(self.eventName,self.getName(),"recordListenedEvent")

    #Make an event list to store the listened to events for use later.
    self.eventTable = []
    
    #Make a conditional activation function (of which various types can be selected) e.g.
    self.conditionType = random.randint(0,1)
    #***************************
    #Activation function type 0:HYPERBOXES 
    #***************************
    #HYPER-BOXES [Initial range -1 to 1] Define ranges within which the input must be for this actor to be active.
    self.hyperboxesDataCondition = self.sd.getRandWithinRanges(self.inputs)#-1 to 1 range initial. 
    print self.hyperboxesDataCondition
    #Always activate this actor on recognition of an event (by default) 
    #***************************
    #Activation function type 1:LOGISTIC REGRESSION CLASSIFIER 
    #***************************



    NUM_ACTION_TYPES = 4
    #Construct the internal type of the actor atom behaviour which may be of a huge range of types.
    self.actorType = random.randint(0,NUM_ACTION_TYPES)
    #Type 0: Standard "primitive actor" makes primitive motor actions.
    #Type 1: "Function actor" computes a function of sensor input.


    
    
    #***************************
    #Behaviour function type 0:SINGLE PRIMITIVE ACTION ONLY   
    #***************************
    #Encode a primitive action as a function of the input vector, e.g. a FFNN.
    self.hiddenSize = random.randint(1,5)
    self.outputSize = random.randint(1,5)    
    self.net = buildNetwork(len(self.inputs), self.hiddenSize, self.outputSize)
    #Choose a subset of self.outputSize actions to control.
    print self.outputSize
    self.outputs = self.sd.getRandomMotors(self.outputSize)

    #***************************
    #Behaviour function type 1:WRITE TO ALMEMORY
    #In this case, construct this memory structure in the 1 (off) state awaiting writing.
    #And put this into the sharedMemory numToData array. 
    #***************************
    self.memory.insertListData([["ActorData" + str(count), 1], ["ActorMesg" + str(count) ,[0,0,0]]]) #1 is inactive. 0 is active.[0 0 0] is the extra message sent to the ALMemory by this actor under this key label  
    self.sd.insertData("ActorData" + str(count))
    self.sd.insertMesg("ActorMesg" + str(count)) #Give this message a number. 
    
    #***************************
    #Behaviour function type 2:RAISE EVENT
    #In this case, create this type of event and put it in the numToEvent array. 
    #***************************
    #self.memory.raiseEvent("ActorEvent"+str(count), 1)
    #self.sd.insertEvent("ActorEvent"+str(count))


    #Actor state and fitness variables****************
    self.active = False       #Starts inactive.
    self.dataMatched = False  #Starts unmatched to data.
    self.timesTested = 0      #Number of times this actor has been tested.
    self.oldMesgValue = [0]    #Stores the old message for optimization atoms
    self.oldOutput = []
    self.parameters = [0] * self.outputSize
    self.oldParameters = [0] * self.outputSize
    
  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)
    
  def act(self):
    
    #Actor is active if we get here, so increment timesTested.
    self.timesTested = self.timesTested+1  
    #Update sensory input from ALMemory
    v = [0] * len(self.inputs) #Initialize input vector to zero. 
    j = 0                      #Counter.
    
    for i in self.inputs:      #For each data input into the atom. 
      v[j] = self.memory.getData(self.sd.getDataName(i)) #Get data value 
      j = j +1

    #Get the message data as well. 
    m = []
    for i in self.mesgInputs:      #For each mesg input into the atom. 
      m.append(self.memory.getData(self.sd.getMesgName(i))) #Get data value 
    #print m  

    #ACT 0 **************************************************************************
    if self.actorType is 0: #MOTOR PRIMITIVE ACTOR 
      motorRaw = list(self.net.activate(v)) #Put through neural network to get raw "motor" outputs
      
      angles = motorRaw
      names = []
      for i in range(len(angles)):
        names.append(self.sd.getMotorName(self.outputs[i]))#Put motor output names into names list

      for index, i in enumerate(names):#Check that motor outputs are within limits. 
        lim = self.motion.getLimits(i)
        #print lim
        #print i
        if angles[index] < lim[0][0]/2.0:
          angles[index] = lim[0][0]/2.0
        if angles[index] > lim[0][1]/2.0:
          angles[index] = lim[0][1]/2.0
 
      self.motion.post.setAngles(names,angles,0.5)#Actually move the motors according to values in angles list.

    #ACT 1 **************************************************************************
    if self.actorType is 1: #FUNCTION ACTOR
      #Take the primitive input data (not messages from other actors) and write a message with the output.  
      #print "Inserting data, not acting"
      #Functions include, e.g. 1. Euclidean distance , 2. neural network. 3. RBF. 
      functRaw = list(self.net.activate(v))
      self.memory.insertData("ActorMesg" + str(self.number) ,functRaw)

    #ACT 2 **************************************************************************
    if self.actorType is 2: #TAKE A MESSAGE INPUT AND DO A PRIMITIVE MOTOR ACTION AS A FUNCTION OF THAT.
      #print "Message length = " + str(len(m))
      #print "Output length = " + str(len(self.outputs))

      #The function implemented here must transform the message into a the right dimension
      #of output values.
      m.extend([0] * (len(self.outputs) - len(m)))
      
      angles = m
      names = []
      for i in range(len(angles)):
        names.append(self.sd.getMotorName(self.outputs[i]))#Put motor output names into names list

      for index, i in enumerate(names):#Check that motor outputs are within limits. 
        lim = self.motion.getLimits(i)
        #print lim
        #print i
        if angles[index] < lim[0][0]/2.0:
          angles[index] = lim[0][0]/2.0
        if angles[index] > lim[0][1]/2.0:
          angles[index] = lim[0][1]/2.0
 
      self.motion.post.setAngles(names,angles,0.5)#Actually move the motors according to values in angles list.

    #ACT 3 *************************************************************************
    if self.actorType is 3: #TAKE A MESSAGE INPUT AS FITNESS, and OUTPUT MOTOR OUTPUT DIRECTLY.
     # print "Running SHC atom"
    #STOCHASTIC HILL CLIMBER TO MINIMIZE MESSAGE INPUT
      #1. Based on the change in fitness (Mesg input), either revert to prev. keep solution.
      if m[0] > self.oldMesgValue[0]:
        self.oldParameters = self.parameters #Keep mutated parameters
      else:
        self.parameters = self.oldParameters #Return to old parameters

      #1.1 Save current as old parameters prior to mutation/exploration 
      self.oldParameters = self.parameters      
      #2. Mutate the current parameters
      for i,v in enumerate(self.parameters):
        self.parameters[i] = self.parameters[i] + 1*(random.random()-0.5)
      print m
      
      #3. Execute action based on mutated parameters
      #Motor output is the parameters, which should be the size of the output
           
      angles = self.parameters
      names = []
      for i in range(len(angles)):
        names.append(self.sd.getMotorName(self.outputs[i]))#Put motor output names into names list

      for index, i in enumerate(names):#Check that motor outputs are within limits. 
        lim = self.motion.getLimits(i)
        #print lim
        #print i
        if angles[index] < lim[0][0]/2.0:
          angles[index] = lim[0][0]/2.0
        if angles[index] > lim[0][1]/2.0:
          angles[index] = lim[0][1]/2.0
      self.motion.post.setAngles(names,angles,0.5)#Actually move the motors according to values in angles list.
      
      #4. Record the current fitness for comparison in the next step. 
      self.oldMesgValue = m
    

  def conditionalActivate(self):
    #print "In conditinal activate of atom " + str(self.number)
    #1. Go through inputs looking for inputs that start with ActorData 
    for i in self.inputs:
      if "ActorData" in self.sd.getDataName(i):
        #print self.sd.getDataName(i)
        #print self.memory.getData(self.sd.getDataName(i))
        if self.memory.getData(self.sd.getDataName(i)) is 0: #if it is active in ALMemory!
          self.active = True
          self.memory.insertData("ActorData" + str(self.number), 0)#Active signal
          #print "Activating conditionally Actor: " + str(self.number)
          
  def checkActivefromData(self):
    #self.memory.raiseEvent(self.eventName, "eventtest")
    index = 0
    self.dataMatched = True
    for i in self.inputs:
      v = self.memory.getData(self.sd.getDataName(i))
      if self.conditionType is 0 or self.conditionType is 1:
         if not (v > self.hyperboxesDataCondition[index][0] and v < self.hyperboxesDataCondition[index][1]):
           self.dataMatched = False
      index = index + 1
      return self.dataMatched

  def checkActivefromEvents(self):
    
    
    pass

    
  def recordListenedEvent(self, a, b, c):
     print "********EVENT LISTENED TO******** Event listened to by action atom" + str(self.number)
     #Put events in the event table stored in this atom.
     self.eventTable.append([a,b,c])
     
     
     pass

  
  def start(self):
    """Start actor module"""
    try:
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
        pass
    self.isRunning = False

  def exit(self):
    try:
      self.memory.unsubscribeToEvent(self.eventName,self.getName())
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
