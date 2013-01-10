import sys
import time
import random
import cma
import statsmodels.api as sm
import collections, numpy as np # arange, cos, size, eye, inf, dot, floor, outer, zeros, linalg.eigh, sort, argsort, random, ones,...
from numpy import inf, array, dot, exp, log, sqrt, sum   # to access the built-in sum fct:  __builtins__.sum or del sum removes the imported sum and recovers the shadowed

#Skeleton by Dave Snowdon

#TODO: 1. Add touch sensors because then granger causality should reward action
#         policies that reward activation of the touch sensors... etc...
#      2. Visualize the fitness increase and the final evolved controller functions.
#      3. Add a population of regression predictors with pruning and use these to define
#         actor fitness, e.g. actors resulting in the most non-pruned (viable)
#         predictors survive. 
#      4. Include Deep Belief Networks in the fitness function, where fitness is a property
#         of the quality of the DBN that is learned (????)
#      5. Include central accelerometers and gyroscopes in the sensor vector. Movements may evolve that improve predictability of those elements.

from naoqi import ALProxy
from pybrain.tools.shortcuts import buildNetwork

ROBOT_IP = "Systemss-MacBook-Pro-2.local" #"169.254.29.204"
ROBOT_PORT = 9559
ASSESSMENT_PERIOD = 20
NUM_PREDICTORS = 10

class MotorBabbling(object):
     def __init__(self, motion, memory, sonar, posture):
         self.motionProxy = motion
         self.memoryProxy = memory
         self.sonarProxy = sonar
         self.postureProxy = posture
         self.names  = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw']
         self.useSensors    = True
         self.inputLength = 15
         self.outputLength = 5
         self.net = buildNetwork(self.inputLength,10,self.outputLength)
         self.sonarProxy.subscribe("Closed-Loop Motor Babbling") #Start the sonor
         self.set_stiffness(0.3)
         
         # Set global joint limits.
         self.LShoulderPitch = motion.getLimits("LShoulderPitch")
         self.LShoulderRoll = motion.getLimits("LShoulderRoll")
         self.LElbowYaw = motion.getLimits("LElbowYaw")
         self.LElbowRoll = motion.getLimits("LElbowRoll")
         self.LWristYaw = motion.getLimits("LWristYaw")
         #print "L Shoulder Limits = "  + str(LShoulderPitch[0][0]) + str(LShoulderPitch[0][1])
         self.sMemory = np.array([1,1,1,1,1,2,2,2,2,2,2,2,2,2,2])
         self.mMemory = np.array([0,0,0,0,0])
         self.predictors = self.makePredictors(NUM_PREDICTORS)

     def makePredictors(self, val):
          net = []; 
          for i in range(val):
               net.append(buildNetwork(self.inputLength,3,self.outputLength))
          return net

     def updatePredictors(self):
         #States stored in sMemory and mMemory are to be used.  
         pass

         
     def set_stiffness(self, val):
         self.motionProxy.setStiffnesses("LShoulderPitch", val)
         self.motionProxy.setStiffnesses("LShoulderRoll", val)
         self.motionProxy.setStiffnesses("LElbowYaw", val)
         self.motionProxy.setStiffnesses("LElbowRoll", val)
         self.motionProxy.setStiffnesses("LWristYaw", val)

     def get_sensor_values(self):
         sensorAngles = self.motionProxy.getAngles(self.names, self.useSensors)

         #lsonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
         #rsonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
         sen = self.memoryProxy.getListData(["Device/SubDeviceList/US/Left/Sensor/Value",
                                             "Device/SubDeviceList/US/Right/Sensor/Value",
                                             "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value", 
                                             "Device/SubDeviceList/LHand/Touch/Left/Sensor/Value", 
                                             "Device/SubDeviceList/LHand/Touch/Right/Sensor/Value",
                                             "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/Value"
                                             ])
         
         sensorAngles.extend(sen)
         if (sensorAngles[7] > 0 or sensorAngles[8] > 0 or sensorAngles[9] > 0):
              print("TOUCH SENSOR TOUCHED\n")
         print(str(sensorAngles[10]) + " " +
               str(sensorAngles[11]) + " " +
               str(sensorAngles[12]) + " " +
               str(sensorAngles[13]) + " " +
               str(sensorAngles[14]))   
         return sensorAngles

     def set_motor_values(self, motorAngles):
##         if motorAngles is None:
##             motorAngles  = [random.uniform(-2.0857, 2.0857), random.uniform(-0.3142, 1.3265),  random.uniform(-2.0857, 2.0857),random.uniform(-1.5446, -0.0349), random.uniform(-1.8238, 1.8238 ) ]
##             print("Using random values")
##         else:
##             print("Motor angles = "+str(motorAngles))
         if motorAngles[0] < self.LShoulderPitch[0][0]: 
             motorAngles[0] = self.LShoulderPitch[0][0]
         elif motorAngles[0] > self.LShoulderPitch[0][1]: 
             motorAngles[0] = self.LShoulderPitch[0][1]
             
         if motorAngles[1] < self.LShoulderRoll[0][0]: 
             motorAngles[1] = self.LShoulderRoll[0][0]
         elif motorAngles[1] > self.LShoulderRoll[0][1]: 
             motorAngles[1] = self.LShoulderRoll[0][1]
             
         if motorAngles[2] < self.LElbowYaw[0][0]: 
             motorAngles[2] = self.LElbowYaw[0][0]
         elif motorAngles[2] > self.LElbowYaw[0][1]: 
             motorAngles[2] = self.LElbowYaw[0][1]
            
         if motorAngles[3] < self.LElbowRoll[0][0]: 
             motorAngles[3] = self.LElbowRoll[0][0]
         elif motorAngles[3] > self.LElbowRoll[0][1]: 
             motorAngles[3] = self.LElbowRoll[0][1]          

         if motorAngles[4] < self.LWristYaw[0][0]: 
             motorAngles[4] = self.LWristYaw[0][0]
         elif motorAngles[4] > self.LWristYaw[0][1]: 
             motorAngles[4] = self.LWristYaw[0][1] 

         fractionMaxSpeed  = 1.0
         self.motionProxy.setAngles(self.names, motorAngles, fractionMaxSpeed)

     def compute_new_motor_angles(self, sensedAngles):
            #Return desired joint angles.
            motorRaw = self.net.activate(sensedAngles)   
            #Bound each joint
            motorBounded = motorRaw
          
            return list(motorBounded)
 
     def event_loop(self):
         while True:
             sensedAngles =self.get_sensor_values()
             #print("Sensed angles = "+str(sensedAngles))
             motorAngles = self.compute_new_motor_angles(sensedAngles)
             #print("Motor angles = "+str(motorAngles))
             self.set_motor_values(motorAngles)
             #self.set_motor_values(None)
             time.sleep(0.3)

     def calculateFitness(self, x):     #Return the fitness based on genotype numpy.ndarray as input controller parameters
         #Re-program the PyBrain network with the parameters specified by the genotype x.
         #print(str(x))
         p = self.net.params
         p[:] = x
         #print(str(self.net.params))
         
         #Initialize data structures for fitness test of this actor. 
         fitness = 0
         i = 0
         self.sMemory = np.array([1,1,1,1,1,2,2,2,2,2,2,2,2,2,2])
         self.mMemory = np.array([0,0,0,0,0])
         #Reset the initial position of the robot using a behaviour. 
         self.postureProxy.applyPosture("LyingBack", 1.0) 
         
         while i< ASSESSMENT_PERIOD: #Run behaviour and store the sensorimotor data
               sensedAngles = self.get_sensor_values()
               #print("Sensed angles = "+str(sensedAngles))
               motorAngles = self.compute_new_motor_angles(sensedAngles)
               self.set_motor_values(motorAngles)
               self.addToMemory(np.array(sensedAngles), np.array(motorAngles))
               self.updatePredictors()
               time.sleep(0.02)
               i = i + 1
         smMatrix = np.array(np.hstack((self.sMemory,self.mMemory)))
         #print(smMatrix.shape)
         fitness = self.getFitness(smMatrix)
         return fitness
         #return np.random.randn(1)[0]

     def addToMemory(self, sensors,motors): #Store the sm state into memory
          self.sMemory = np.row_stack((self.sMemory,sensors))
          self.mMemory = np.row_stack((self.mMemory,motors))

          pass

     def getFitness(self, smMatrix): #Store the sm state into memory
          fit = 0
          
          
          #Fitness functions (1) ************************************************************
          #1. Maximize sonar values.
          #print(smMatrix)
          fit = -sum(smMatrix[:,0]) + sum(smMatrix[:,1])
          print fit
          return fit

          #Fitness function (2) *************************************************************
          #2. Calculate granger causality between the motor actions and the sensor actions.
          #print(smMatrix)
          #For each motor timeseries
          #Not really sure this is going to work (increase fitness) and even if it does, what this will mean in terms of behaviour. 
##          pairWiseGranger = 0; 
##          for index_x, x in np.ndenumerate(smMatrix[0]):
##              if np.equal(x,0):
##                  for index_y, y in np.ndenumerate(smMatrix[0]):
##                      if np.equal(y,1) or np.equal(y,2):
##                          dataS = smMatrix[:,index_y]
##                          noise = np.random.random(dataS.shape)*0.0000000001
##                          dataS = noise + dataS
##                          dataM = smMatrix[:,index_x]
##                          noise = np.random.random(dataM.shape)*0.0000000001
##                          dataM = noise + dataM
##                          grData = np.column_stack((dataS, dataM))
##                          #print(grData)
##                          grData = np.diff(grData,axis = 0) #Take 1st derivative of GR data. 
##                          #model = sm.tsa.VAR(grData)
##                          #results = model.fit(maxlags = 3, ic='aic')
##                          #print(str(index_x) + " " + str(index_y) + "\n")
##                          r = sm.tsa.stattools.grangercausalitytests(grData,maxlag = 2, verbose = False)
##                          a = r[2] #Consider the 3rd order model only for now, so we select for high granger causality 3rd order models.
##                          b = a[0]
##                          c1 = b['lrtest']
##                          c2 = b['params_ftest']
##                          c3 = b['ssr_ftest']
##                          c4 = b['ssr_chi2test']
##                          c1F = 0
##                          c2F = 0
##                          c3F = 0
##                          c4F = 0
###                          if c1[1] > 0.00:#If this test is significant then use the F score in the fitness function 
###                              c1F = c1[0]
##                          if c2[1] > 0.05:#Do this for all 4 kinds of granger test. 
##                              c2F = c2[0]
###                          if c3[1] > 0.00:
###                              c3F = c3[0]
###                          if c4[1] > 0.00:
###                              c4F = c4[0]
##                          #print(str(c1F) + " " + str(c2F) + " " + str(c3F) + " " + str(c4F))
##                          pairWiseGranger = pairWiseGranger + c1F + c2F + c3F + c4F
##
##          print("Fitness = " + str(-pairWiseGranger))
##          pw = -pairWiseGranger
##          return pw

          #Fitness function (3) *************************************************************
          #Fitness is the total summed value of the touch sensors over an episode. 
          
          

     
     def sphere(self, x):
          """Sphere (squared norm) test objective function"""
          # return np.random.rand(1)[0]**0 * sum(x**2) + 1 * np.random.rand(1)[0]
          return sum((x+0)**2)

     def noise(self, x, func=sphere, fac=10, expon=1):
          f = func(self, x)
          #R = np.random.randn(1)[0]
          R = np.log10(f) + expon * abs(10-np.log10(f)) * np.random.rand(1)[0]
          return f + 10**R  # == f + f**(1+0.5*RN)

def main (argv=None):
    motion = None
    try:
        motion = ALProxy("ALMotion", ROBOT_IP, ROBOT_PORT)
    except:
        print("failed to create motion proxy")
        return

    memory = None
    try:
        memory = ALProxy("ALMemory", ROBOT_IP, ROBOT_PORT)
    except:
        print("failed to create memory proxy")
        return

    sonar = None
    try:
        sonar = ALProxy("ALSonar", ROBOT_IP, ROBOT_PORT)
    except:
        print("failed to create sonar proxy")
        return
    posture = None
    try:
        posture = ALProxy("ALRobotPosture", ROBOT_IP, ROBOT_PORT)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e
    posture.goToPosture("LyingBack", 1.0)
    time.sleep(1.0)
    print posture.getPostureFamily()

##    # Example showing how to get the limits for the whole body
##    name = "Body"
##    limits = motion.getLimits(name)
##    jointNames = motion.getBodyNames(name)
##    for i in range(0,len(limits)):
##        print jointNames[i] + ":"
##        print "minAngle", limits[i][0],\
##            "maxAngle", limits[i][1],\
##            "maxVelocity", limits[i][2],\
##            "maxTorque", limits[i][3]
## 
##    
   
    mb = MotorBabbling(motion, memory, sonar, posture)
    res = cma.fmin(mb.calculateFitness, 0.0*(np.random.random_sample(215,)-0.5), 1, verb_disp=1)
    cma.plot()
    cma.show()

if __name__ == "__main__":
    sys.exit(main())

