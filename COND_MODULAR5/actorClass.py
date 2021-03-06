from naoqi import *
import math
import almath
import random
import time
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
  
  def __init__(self,name = "actor", count = 0, inputs = None, outputs = None, messageInputs = None, function = None, typeA = 0):
    #MAKE RANDOM ACTOR

    if typeA is 0:#RANDOM      
      self.name = name + str(count)
      ALModule.__init__(self,self.name)
      print "Making actor random:" + str(count)
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
      self.memory.insertListData([["ActorData" + str(count), 1], ["ActorMesg" + str(count) ,[0]]]) #1 is inactive. 0 is active.[0 0 0] is the extra message sent to the ALMemory by this actor under this key label  
      self.sd.insertData("ActorData" + str(count))
      self.sd.insertMesg("ActorMesg" + str(count)) #Give this message a number. 
      self.functionName = []

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
      self.parameters = [0] * self.outputSize
      self.newParameters = [0] * self.outputSize
      

    #MAKE SHC ACTOR 
    elif typeA is 3:
      self.name = name+str(count)
      ALModule.__init__(self,name)
      print "Making SHC Actor:" + str(count)
      self.isRunning=True
      self.number = count
      #Create a proxy to the sharedData module.
      self.sd = ALProxy("sharedData")
      #And to ALMemory
      self.memory = ALProxy("ALMemory")    
      self.motion = ALProxy("ALMotion", "ctf.local", 9559)
      self.Body = self.motion.getLimits("Body")
      self.set_stiffness(1.0)
      self.sd.start()
      #Make a list of ALMemory state inputs from the arguments.
      self.inputs = inputs 
      #Make a list of ALMemory mesg inputs that this actor will check regularly.
      self.mesgInputs = messageInputs
      print "Regular data inputs to actor " + str(count) + " = " + str(self.inputs)
      print " message inputs to actor " + str(count) + " = " + str(self.mesgInputs)

      #Make a list of ALMemory Events that this actor will subscribe and listen to.
      self.eventInputs = [] 
      print "event inputs = "+ str(self.eventInputs)
      self.eventName = []
      self.eventTable = []
      
      #Make a conditional activation function (of which various types can be selected) e.g.
      self.conditionType = random.randint(0,1)
      #***************************
      #Activation function type 0:HYPERBOXES 
      #***************************
      #HYPER-BOXES [Initial range -1 to 1] Define ranges within which the input must be for this actor to be active.
      self.hyperboxesDataCondition = self.sd.getRandWithinRanges(self.inputs)#-1 to 1 range initial. 
      print "conditions for sensory activation = " + str(self.hyperboxesDataCondition)
      #Always activate this actor on recognition of an event (by default) 
      #***************************
      #Activation function type 1:LOGISTIC REGRESSION CLASSIFIER 
      #***************************
      
      self.actorType = typeA
      #Type 1: "Function actor" computes a function of sensor input.
      
      #***************************
      #Behaviour function type 0:SINGLE PRIMITIVE ACTION ONLY   
      #***************************
      #Encode a primitive action as a function of the input vector, e.g. a FFNN.
      self.hiddenSize = random.randint(1,5)
      if outputs is None:
        self.outputSize = random.randint(1,5)
      else:
        self.outputSize = len(outputs)
      self.net = buildNetwork(len(self.inputs), self.hiddenSize, self.outputSize)
      #Choose a subset of self.outputSize actions to control.
      print "Output size = " + str(self.outputSize)
      if outputs is None:
        self.outputs = self.sd.getRandomMotors(self.outputSize)
      else:
        self.outputs = outputs

      #***************************
      #Behaviour function type 1:WRITE TO ALMEMORY
      #In this case, construct this memory structure in the 1 (off) state awaiting writing.
      #And put this into the sharedMemory numToData array. 
      #***************************
      self.memory.insertListData([["ActorData" + str(count), 1], ["ActorMesg" + str(count) ,[0]]])
      self.sd.insertData("ActorData" + str(count))
      self.sd.insertMesg("ActorMesg" + str(count)) #Give this message a number.
      self.functionName = None
      
      
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
      self.parameters = [0] * self.outputSize
      self.newParameters = [0] * self.outputSize
      

    #MAKE MESSAGE MAKING ACTOR 
    elif typeA is 1:
      name = name+str(count)
      ALModule.__init__(self,name)
      print "Making Message Actor:" + str(count)
      self.isRunning=True
      self.number = count
      #Create a proxy to the sharedData module.
      self.sd = ALProxy("sharedData")
      #And to ALMemory
      self.memory = ALProxy("ALMemory")    
      self.motion = ALProxy("ALMotion", "ctf.local", 9559)
      self.Body = self.motion.getLimits("Body")
      self.set_stiffness(1.0)
      self.sd.start()
      #Make a list of ALMemory state inputs from the arguments.
      self.inputs = inputs 
      #Make a list of ALMemory mesg inputs that this actor will check regularly.
      self.mesgInputs = [] #No message inputs. 
      print "Regular data inputs to actor " + str(count) + " = " + str(self.inputs)

      #Make a list of ALMemory Events that this actor will subscribe and listen to.
      self.eventInputs = [] 
      print "events = " + str(self.eventInputs)
      self.eventName = []
      self.eventTable = []
      
      #Make a conditional activation function (of which various types can be selected) e.g.
      self.conditionType = random.randint(0,1)
      #***************************
      #Activation function type 0:HYPERBOXES 
      #***************************
      #HYPER-BOXES [Initial range -1 to 1] Define ranges within which the input must be for this actor to be active.
      self.hyperboxesDataCondition = self.sd.getRandWithinRanges(self.inputs)#-1 to 1 range initial. 
      print "conditions for sensory activation = " + str(self.hyperboxesDataCondition)
      #Always activate this actor on recognition of an event (by default) 
      #***************************
      #Activation function type 1:LOGISTIC REGRESSION CLASSIFIER 
      #***************************
      
      self.actorType = typeA
      #Type 1: "Function actor" computes a function of sensor input.
      
      #***************************
      #Behaviour function type 0:SINGLE PRIMITIVE ACTION ONLY   
      #***************************
      #Encode a primitive action as a function of the input vector, e.g. a FFNN.
      self.hiddenSize = random.randint(1,5)
      self.outputSize = random.randint(1,5)    
      self.net = buildNetwork(len(self.inputs), self.hiddenSize, self.outputSize)
      #Choose a subset of self.outputSize actions to control.
      print "Output size = " + str(self.outputSize)
      self.outputs = self.sd.getRandomMotors(self.outputSize)

      #***************************
      #Behaviour function type 1:WRITE TO ALMEMORY
      #In this case, construct this memory structure in the 1 (off) state awaiting writing.
      #And put this into the sharedMemory numToData array. 
      #***************************
      self.memory.insertListData([["ActorData" + str(count), 1], ["ActorMesg" + str(count) ,[0]]])
      self.sd.insertData("ActorData" + str(count))
      self.sd.insertMesg("ActorMesg" + str(count)) #Give this message a number.
      self.functionName = function
      
      
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
      self.parameters = [0] * self.outputSize
      self.newParameters = [0] * self.outputSize
      

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
    
#    print "Running actor " + str(self.number)
#    print "DataInput = " + str(v)
#    print "Messageinput = " + str(m)
    #ACT 0 **************************************************************************
    if self.actorType is 0: #MOTOR PRIMITIVE ACTOR 
      motorRaw = list(self.net.activate(v)) #Put through neural network to get raw "motor" outputs
      #print "Primitive motor actor type 0"
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

      if self.functionName is None:
        #print "Function actor type 1:net"
        functRaw = list(self.net.activate(v))
        
      if self.functionName is "product":
        print "Function actor type 1:first value"
        functRaw = v[0] #v[1]
        
      self.memory.insertData("ActorMesg" + str(self.number) ,functRaw)

    #ACT 2 **************************************************************************
    if self.actorType is 2: #TAKE A MESSAGE INPUT AND DO A PRIMITIVE MOTOR ACTION AS A FUNCTION OF THAT.
      #print "Direct message to motor actor type 2"
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
      print "SHC actor type"
      #5. Assess fitness of the new state/position 
      #1. m[0] shows the fitness of the current state./
      #6. If m > oldm, parameters = newparameters.   
      if m[0] > self.oldMesgValue[0]:
        self.parameters = self.newParameters
        self.oldMesgValue = m
      else:
        #7. If m <= oldm, revert, move back to the original parameters
        m = self.oldMesgValue
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

        self.motion.post.setAngles(names,angles,1)#Actually move the motors according to values in angles list.
 #      self.motion.post.angleInterpolation(names,angles,[0.1]*len(names),1)#Actually move the motors according to values in angles list.
        time.sleep(0.2)

      #2. Mutate the current parameters to new-parameters.
      #print len(self.newParameters)
      for i,v in enumerate(self.newParameters):
        self.newParameters[i] = self.parameters[i] + 0.1*(random.random()-0.5)
      #3. Execute the new parameters.
      angles = self.newParameters
      names = []
      for i in range(len(angles)):
        names.append(self.sd.getMotorName(self.outputs[i]))#Put motor output names into names list
      for index, i in enumerate(names):#Check that motor outputs are within limits. 
        lim = self.motion.getLimits(i)
        if angles[index] < lim[0][0]/2.0:
          angles[index] = lim[0][0]/2.0
        if angles[index] > lim[0][1]/2.0:
          angles[index] = lim[0][1]/2.0          
      self.motion.post.setAngles(names,angles,1)#Actually move the motors according to values in angles list.
      time.sleep(0.2)
      #self.motion.post.angleInterpolation(names,angles,[0.1]*len(names),1)#Actually move the motors according to values in angles list.
      #4. Save the value of the old fitness
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
      #print self.sd.getDataName(i)
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
