import os
import sys

lib_path = os.path.abspath('../')
sys.path.append(lib_path)

from time import time, sleep
from random import Random
#import cma
#import statsmodels.api as sm
import collections, numpy as np # arange, cos, size, eye, inf, dot, floor, outer, zeros, linalg.eigh, sort, argsort, random, ones,...
from numpy import inf, array, dot, exp, log, sqrt, sum   # to access the built-in sum fct:  __builtins__.sum or del sum removes the imported sum and recovers the shadowed
#import inspyred
#from Tkinter import *
#import itertools
from naoqi import ALProxy
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import FeedForwardNetwork
#from pybrain.structure import LinearLayer, SigmoidLayer
#from pybrain.structure import FullConnection
#from pybrain.datasets import SupervisedDataSet
#from pybrain.supervised.trainers import BackpropTrainer
#from pybrain.tools.neuralnets import NNregression 
#from pybrain.tools.plotting import MultilinePlotter
#import pyentropy as ent
#
#Skeleton by Dave Snowdon (2013, thanks Dave!) 

#ROBOT_IP = "192.168.43.232" #"Systemss-MacBook-Pro-2.local" #"169.254.29.204"
ROBOT_IP = "ctf.local"
ROBOT_PORT = 9559
INPUTSIZE = 26+18
OUTPUTSIZE = 26
HIDDENSIZE = 5
PREDICTSIZE = 1

class MotorBabbling(object):
     def __init__(self, motion, memory, sonar, posture):
         self.motionProxy = motion
         self.memoryProxy = memory
         self.sonarProxy = sonar
         self.postureProxy = posture
         self.useSensors    = True
         self.inputLength = 26+18
         self.outputLength = 26
         self.sonarProxy.subscribe("Closed-Loop Motor Babbling") #Start the sonor
         self.set_stiffness(0.3)
         self.net = buildNetwork(INPUTSIZE,HIDDENSIZE,OUTPUTSIZE)


         # Access global joint limits.
         self.Body = motion.getLimits("Body")
         self.bangles =  [1] * 26
         self.othersens = [2] * 18
         self.sMemory = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory = np.array([0]*OUTPUTSIZE)
     

         self.rand = Random()
         self.rand.seed(int(time()))
         
         
     def set_stiffness(self, val):
         self.motionProxy.setStiffnesses("Body", val)

     def get_sensor_values(self): 
         sensorAngles = self.motionProxy.getAngles("Body", self.useSensors)
         sen = self.memoryProxy.getListData(["Device/SubDeviceList/US/Left/Sensor/Value",
                                             "Device/SubDeviceList/US/Right/Sensor/Value",
                                             "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value", 
                                             "Device/SubDeviceList/LHand/Touch/Left/Sensor/Value", 
                                             "Device/SubDeviceList/LHand/Touch/Right/Sensor/Value",
                                             "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
                                             "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value"
                                             ])
         
         sensorAngles.extend(sen)
         return sensorAngles

     
     def rest(self):
         fractionMaxSpeed  = 1.0
         bodyLyingDefaultAngles = [-0.20406389236450195, 0.16256213188171387, 1.5784441232681274,
                                   0.2469320297241211, 0.5199840068817139, -0.052114009857177734,
                                   -1.1029877662658691, 0.1711999773979187, 0.013848066329956055,
                                   0.13503408432006836, 0.0061779022216796875, 0.47856616973876953,
                                   0.9225810170173645, 0.04912996292114258, 0.013848066329956055,
                                   -0.14568805694580078, 0.3021559715270996, -0.09232791513204575,
                                   0.9320058226585388, 0.0031099319458007812, 1.7718119621276855,
                                   -0.13503408432006836, 1.515550136566162, 0.12429594993591309,
                                   1.348344087600708, 0.14719998836517334]
         motorAngles = bodyLyingDefaultAngles
         
         #Check that the specified angles are within limits
         for index,i in enumerate(self.Body):
              if motorAngles[index] < i[0]/2:
                   motorAngles[index] = i[0]/2
              if motorAngles[index] > i[1]/2:
                   motorAngles[index] = i[1]/2
                   
         self.motionProxy.setAngles("Body", motorAngles, fractionMaxSpeed)
         sleep(0.1)


     def set_motor_values(self, ma):

         fractionMaxSpeed  = 1.0
         bodyLyingDefaultAngles = [-0.20406389236450195, 0.16256213188171387, 1.5784441232681274,
                                   0.2469320297241211, 0.5199840068817139, -0.052114009857177734,
                                   -1.1029877662658691, 0.1711999773979187, 0.013848066329956055,
                                   0.13503408432006836, 0.0061779022216796875, 0.47856616973876953,
                                   0.9225810170173645, 0.04912996292114258, 0.013848066329956055,
                                   -0.14568805694580078, 0.3021559715270996, -0.09232791513204575,
                                   0.9320058226585388, 0.0031099319458007812, 1.7718119621276855,
                                   -0.13503408432006836, 1.515550136566162, 0.12429594993591309,
                                   1.348344087600708, 0.14719998836517334]
         motorAngles = bodyLyingDefaultAngles
         motorAngles = ma      

         #Check that the specified angles are within limits
         for index,i in enumerate(self.Body):
              if motorAngles[index] < i[0]/2:
                   motorAngles[index] = i[0]/2
              if motorAngles[index] > i[1]/2:
                   motorAngles[index] = i[1]/2

         #Set the motor angle we're actually optimizing.
         #print(ma)
         #print(val)
         #self.motionProxy.angleInterpolationWithSpeed("Body", motorAngles, fractionMaxSpeed)
         self.motionProxy.setAngles("Body", motorAngles, fractionMaxSpeed)


     def compute_new_motor_angles(self, sv):
            #Return desired joint angle.
            #print(sv)
            motorRaw = self.net.activate(sv)   
            #Bound each joint
            motorBounded = motorRaw
          
            return list(motorBounded)
 
     def event_loop(self):#Simple event loop. 
         while True:
             sensedAngles = self.get_sensor_values()
             motorAngles  = self.compute_new_motor_angles(sensedAngles)
             self.set_motor_values(motorAngles)
             sleep(0.1)

  
  

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
 #   posture.goToPosture("LyingBack", 1.0)
 #   time.sleep(1.0)
 #   print posture.getPostureFamily()

    mb = MotorBabbling(motion, memory, sonar, posture)
 
    #Run Simple Event Loop (for testing only) 
    mb.event_loop()

    #Run simple co-evolutionary system. 
 

    
if __name__ == "__main__":
    sys.exit(main())



"""
  BODY CONTROL NAMES
  
  case "naoAcademics": 
    Head     = [HeadYawAngle, HeadPitchAngle]; 
    LeftArm  = [ShoulderPitchAngle, +ShoulderRollAngle, 
                +ElbowYawAngle, +ElbowRollAngle, WristYawAngle, HandAngle]; 
    RightArm = [ShoulderPitchAngle, -ShoulderRollAngle, 
                -ElbowYawAngle, -ElbowRollAngle, WristYawAngle, HandAngle]; 
    LeftLeg  = [HipYawPitchAngle, +HipRollAngle, 
                HipPitchAngle, KneePitchAngle, AnklePitchAngle, +AnkleRollAngle]; 
    RightLeg = [HipYawPitchAngle, -HipRollAngle, 
                HipPitchAngle, KneePitchAngle, AnklePitchAngle, -AnkleRollAngle] 



 """

