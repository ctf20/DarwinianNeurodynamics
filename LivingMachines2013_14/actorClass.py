from naoqi import *
import math
import almath
import time
import copy
##from pybrain.tools.shortcuts import buildNetwork
##from pybrain.structure import FeedForwardNetwork
##from pybrain.structure import LinearLayer, SigmoidLayer
##from pybrain.structure import FullConnection
##from pybrain.datasets import SupervisedDataSet
##from pybrain.supervised.trainers import BackpropTrainer
##from pybrain.tools.neuralnets import NNregression 
##from pybrain.tools.plotting import MultilinePlotter
import pickle
import uuid
from brian import *
import random as random
# create python module
class actorClass(ALModule):
  """Create an actor instance"""
  

  def __init__(self, typeA = None, nameA = None, count = None, sensors = None,messages = None, messageDelays = None, motors = None, function = None, parameters = None):

    ALModule.__init__(self,str(uuid.uuid4()))
    #Create a proxy to the memoryManager module.
    self.mm = ALProxy("memoryManager")
    self.motion = ALProxy("ALMotion")
    self.type = typeA
    self.atomKind = nameA
    self.id = count
    self.sensors = sensors
    self.messages = messages
    self.messageDelays = messageDelays
    self.motors = motors
    self.function = function
    self.mm.putMemory(self.id, [0,0,0]) #0 in first position = inactive, 1 in first position = active. 
    self.active = False
    self.activeHist = False
    self.timesTested = 0
    self.parameters = parameters
    self.oldParameters = parameters
    self.fitness = 0 
    self.oldFitness = 0
    self.set_stiffness(1)
    self.timer = 0
    self.timer2 = 0

    #If typeA is a Brian atom then a random network must be constructed from the parameters
    if self.type == "lsm":#http://briansimulator.org/?utm_source=twitterfeed&utm_medium=twitter
      eqs = '''
      dv/dt = (ge+gi-(v+49*mV))/(20*ms) : volt
      dge/dt = -ge/(5*ms) : volt
      dgi/dt = -gi/(10*ms) : volt
      '''
      self.P = NeuronGroup(4000, eqs, threshold=-50*mV, reset=-60*mV)
      self.P.v = -50*mV
      self.Pe = self.P.subgroup(320)
      self.Pi = self.P.subgroup(80)
      self.Ce = Connection(self.Pe, self.P, 'ge', weight=1.62*mV, sparseness=0.02)
      self.Ci = Connection(self.Pi, self.P, 'gi', weight=-9*mV, sparseness=0.02)
      self.M = SpikeMonitor(self.P)
#      run(0.1*second)
#      raster_plot(self.M)
#      show()

  def getPickleData(self):
    return [self.type,
            self.atomKind,
            self.id,
            self.sensors,
            self.messages,
            self.messageDelays,
            self.motors,
            self.function,
            self.parameters]
      
  def mutate(self):

    #Mutate the motor vector if there is one.
    if self.motors is not None:
      for index, i in enumerate(self.motors):
        if random.random() < 0.05:
          #print "MUTATING ************************************************"
          self.motors[index] = self.mm.getRandomMotor()
          #print str(self.id) + " has motor " + str(self.motors[index])
      #for i in self.motors:
      #  print "new motor = " + str(i)
        
    #Mutate the sensory inputs to an atom.
    if self.sensors is not  None:
      for index, i in enumerate(self.sensors):
        if random.random() < 0.0:
          #print "MUTATING ************************************************"
          self.sensors[index] = self.mm.getRandomSensor()
          #print str(self.id) + " has motor " + str(self.motors[index])
      #for i in self.sensors:
      #  print "new sensor = " + str(i)
    
    if self.type == "motorP":
      #Mutate motor positions 
      for index, i in enumerate(self.parameters[1]):
        if random.random() < 0.05:
          self.parameters[1][index] = 0.5*(random.random()-0.5) + self.parameters[1][index]
      #Mutate repetition delay [possibly depreciated]  
      if random.random() < 0.05:
          self.parameters[0][0] = random.randint(1,5)
          if self.parameters[0][0] < 1:
            self.parameters[0][0] = 1
          elif self.parameters[0][0] > 5:
            self.parameters[0][0] = 5
      #Mutate transmission delay 
      for index, i in enumerate(self.messageDelays):
        if random.random() < 0.05:
          self.messageDelays[index] = random.randint(1,5)
        


  def act(self):

    #Update no of times actor has been activated.  
    self.timesTested = self.timesTested+1
    
    #Get sensor data
    if self.sensors is not None:
        v = [0] * len(self.sensors) 
        j = 0                      
        for i in self.sensors:      
          v[j] = self.mm.getSensorValue(i) 
          j = j +1

    #Get message data [use a list because messages may be composite]
    m = []
    if self.messages is not None:
      for i in self.messages:
        m.append(self.mm.getMessageValue(i))

    #Get message delays
    md = []
    if self.messageDelays is not None:
      for i in self.messageDelays:
        md.append(i)
        
 
    #Type dependent actions
    if self.type == "sensory":#Just take memory, calculate a function and write it to memory.
        #print "sensory atom " + str(self.id)
        #print self.sensors
        if self.function == "sum":
            functSum = 0
            for i in v:
                if i is not None:
                  functSum = functSum + i
  
        elif self.function == "position":
            functSum = 0
            for i in v:
                if i is not None:
                  functSum = functSum + i
  
          #Gets the world based cartesian position of the camera. 
          #name            = "CameraTop"
          #space           = motion.FRAME_WORLD
          #useSensorValues = True
          #result          = self.motion.getPosition(name, space, useSensorValues)
          #functSum = result[0] + result[1] + result[2]
          #print "sensors = " + str(functSum)
          
        self.mm.putMemory(self.id,[1, functSum, 0])
        
 
    elif self.type == "shc":
        #print "SHC atom " + str(self.id)
        #Get fitness of previously tried parameters. 
        if self.function == "sum":
            functSum = 0
            for i in m:
                functSum = functSum + i[1]
            self.fitness = functSum
            #print "New fitness = " + str(self.fitness)
            
        if self.fitness < self.oldFitness  or random.random() < 0.05:#If fitness better than old fitness.
            #print "retrying new parameters"
            self.oldParameters = list(self.parameters) #Set oldParameters to parameters. 
            self.oldFitness = self.fitness #Old fitness updated with new fitness.
            #Construct new random parameters and pass them to the movement atom
            for i,v in enumerate(self.parameters):
                self.parameters[i] = self.parameters[i] + 0.5*(random.random()-0.5)
        else:
            #print "resetting parameters" 
            self.fitness = self.oldFitness #new fitness reset to old fitness.
            self.parameters  = list(self.oldParameters)#Reset old parameters and pass them to the movement atom.
            
        #Write parameters to memory
        self.mm.putMemory(self.id,[1, self.parameters, 0])


    
    if self.type == "motorP":
      #Go through each motor and set its value according to its parameters.
##        print "timer = " + str(self.timer) + " param = " + str(self.parameters[0][0])
       # if self.timer == self.parameters[0][0]:
          #print "activating"
#          self.timer = 0
##          print "Activate motor atom " + str(self.id)
       if self.timer2 == self.parameters[0][0]:
          self.mm.putMemory(self.id,[0, 0, 0])
          self.active = False
          self.timer = 0
          self.timer2 = 0
       else:
          self.timer2 = self.timer2 + 1
          angles = []
          times = []
          names = []
          #motorsTemp = set(self.motors)
          motorsTemp = self.motors
          dictTemp = {}
          co = 0
          for index, i in enumerate(motorsTemp):
            name = self.mm.getMotorName(i)
            if name not in dictTemp:
              dictTemp[name] = 1             
              names.append(name)
              lim = self.motion.getLimits(name)
              angles.append(self.parameters[1][index])
              times.append(self.parameters[2][index])
              if angles[co] < lim[0][0]/1.0:
                angles[co] = lim[0][0]/1.0
              if angles[co] > lim[0][1]/1.0:
                angles[co] = lim[0][1]/1.0
              co = co+1
          self.motion.setAngles(names,angles,1)#Actually move the motors according to values in angles list.
          self.mm.putMemory(self.id,[1, 0, 0])
        #self.timer = self.timer + 1
 #       print "timer = " + str(self.timer)





    if self.type == "motor":
        #Go through each motor and set its value according to the message.
        #print "motion atom " + str(self.id)
        inputs = m[0][1]
        #print "INputs to motor atom num " + str(self.id) + " = " + str(inputs)
        angles = []
        names = []
        #Abolish duplicates
        motorsTemp = set(self.motors)
        #print motorsTemp
        for index, i in enumerate(motorsTemp):
            name = self.mm.getMotorName(i)
            names.append(name)
            lim = self.motion.getLimits(self.mm.getMotorName(i))
            angles.append(inputs[index])
            if angles[index] < lim[0][0]/2.0:
              angles[index] = lim[0][0]/2.0
            if angles[index] > lim[0][1]/2.0:
              angles[index] = lim[0][1]/2.0

    
        
        self.motion.setAngles(names,angles,1)#Actually move the motors according to values in angles list.
        self.mm.putMemory(self.id,[1, 0, 0])

        #print names
        #print angles
        time.sleep(0.1)



  def conditionalActivate(self):
    if self.messages is not None:
        for index, i in enumerate(self.messages):
            #print self.mm.getMessageValue(i)
            if self.mm.getMessageValue(i)[0] is 1 and self.active is False: 
              #Incremement timer
              self.timer = self.timer + 1
              if self.timer == self.messageDelays[index]:
                self.active = True
                self.activeHist = True
                #print str(self.id) + "Activated by atom " + str(i) + " with message" + str(self.mm.getMessageValue(i))
                self.mm.putMemory(self.id,[1,0,0])#Active signal
            
          
  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)


    
          
  def exit(self):
    print "exiting"
    self.isRunning=False
    ALModule.exit(self)
