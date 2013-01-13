import os
import sys
from time import time, sleep
from random import Random
import cma
import statsmodels.api as sm
import collections, numpy as np # arange, cos, size, eye, inf, dot, floor, outer, zeros, linalg.eigh, sort, argsort, random, ones,...
from numpy import inf, array, dot, exp, log, sqrt, sum   # to access the built-in sum fct:  __builtins__.sum or del sum removes the imported sum and recovers the shadowed
import inspyred
from Tkinter import *
import itertools
from curiosityLoop import curiosityLoop


#Skeleton by Dave Snowdon (2013, thanks Dave!) 

from naoqi import ALProxy
from pybrain.tools.shortcuts import buildNetwork

#ROBOT_IP = "169.254.29.204" #"Systemss-MacBook-Pro-2.local" #"169.254.29.204"
ROBOT_IP = "ctf.local"
ROBOT_PORT = 9559
ASSESSMENT_PERIOD = 10
INPUTSIZE = 2
OUTPUTSIZE = 1
HIDDENSIZE = 10
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
         self.set_stiffness(0.1)
         self.net = buildNetwork(INPUTSIZE,HIDDENSIZE,OUTPUTSIZE)

         # Access global joint limits.
         self.Body = motion.getLimits("Body")
         self.bangles =  [1] * 26
         self.othersens = [2] * 18
         self.sMemory = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory = np.array([0]*OUTPUTSIZE)
         self.cl = curiosityLoop()
         
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

     def set_motor_values(self, ma,val):

         fractionMaxSpeed  = 0.8
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
         motorAngles[val] = ma[0]        

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
            #Return desired joint angles.
            motorRaw = self.net.activate(sv)   
            #Bound each joint
            motorBounded = motorRaw
          
            return list(motorBounded)
 
     def event_loop(self):#Simple event loop. 
         while True:
             sensedAngles =self.get_sensor_values()
             motorAngles = self.compute_new_motor_angles(sensedAngles)
             self.set_motor_values(motorAngles)
             sleep(0.3)

     def calculateFitness(self, x):     #Return the fitness based on genotype numpy.ndarray as input controller parameters
         #Re-program the PyBrain network with the parameters specified by the Loop genotype. 
         #print(str(x[3]))
         p = self.net.params
         p[:] = x[3] #Assign the weights from curiosityLoop genome to the controller network 
         #print(str(self.net.params))
         
         #Initialize data structures for fitness test of this actor. 
         fitness = 0
         i = 0
         self.sMemory = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory = np.array([0]*OUTPUTSIZE)
         #Reset the initial position of the robot using a behaviour. 
         #self.postureProxy.applyPosture("LyingBack", 1.0) 
         
         while i < ASSESSMENT_PERIOD: #Run behaviour and store the sensorimotor data
               sensedAngles = self.get_sensor_values()
               #print("sen1 = " + str(x[0][0]))
               #print("sen2 = " + str(x[0][1]))
               sv = [sensedAngles[x[0][0]], sensedAngles[x[0][1]]]
               pv = sensedAngles[x[2]]#Angles we wish to predict. 
               motorAngles = self.compute_new_motor_angles(sv)
               #print("motor " + str(x[1]))
               self.set_motor_values(motorAngles, x[1])
               self.addToMemory(np.hstack((np.array(sv), (np.array(pv)))), np.array(motorAngles))
               sleep(0.1)
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
          
          
          #Fitness function (3) *************************************************************
          #Record the sm data for this loop and consider its properties
          print(smMatrix)
          
     
          #Fitness functions (1) ************************************************************
          #1. Maximize sonar values.
          #print(smMatrix)
          fit = sum(smMatrix[:])
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
##                          #dataS = noise + dataS
##                          dataM = smMatrix[:,index_x]
##                          noise = np.random.random(dataM.shape)*0.0000000001
##                          #dataM = noise + dataM
##                          grData = np.column_stack((dataS, dataM))
##                          print(grData)
##                          #grData = np.diff(grData,axis = 0) #Take 1st derivative of GR data. 
##                          #model = sm.tsa.VAR(grData)
##                          #results = model.fit(maxlags = 3, ic='aic')
##                          #print(str(index_x) + " " + str(index_y) + "\n")
##                          r = sm.tsa.stattools.grangercausalitytests(grData,maxlag = 2, verbose = True)
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
##          print("Fitness = " + str(pairWiseGranger))
##          pw = pairWiseGranger
##          return pw


     
     def sphere(self, x):
          """Sphere (squared norm) test objective function"""
          # return np.random.rand(1)[0]**0 * sum(x**2) + 1 * np.random.rand(1)[0]
          return sum((x+0)**2)

     def noise(self, x, func=sphere, fac=10, expon=1):
          f = func(self, x)
          #R = np.random.randn(1)[0]
          R = np.log10(f) + expon * abs(10-np.log10(f)) * np.random.rand(1)[0]
          return f + 10**R  # == f + f**(1+0.5*RN)

     def evaluateLoop(self, candidates, args):
          fitness = []
          for cs in candidates:
               fit = self.calculateFitness(cs)
               fitness.append(fit)
          return fitness


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
    #mb.event_loop()
    
    #Run CMA-ES on big network optimization (won't work, its too big) 
    #res = cma.fmin(mb.calculateFitness, 0.0*(np.random.random_sample(736,)-0.5), 1, verb_disp=1)
    #cma.plot()
    #cma.show()

#Run an evolutionary algorithm.
##    projdir = os.path.dirname(os.getcwd())
##    stat_file_name = '{0}/statsFile.csv'.format(projdir)
##    ind_file_name = '{0}/indFile.csv'.format(projdir)
##    stat_file = open(stat_file_name, 'w')
##    ind_file = open(ind_file_name, 'w')
##    rand = Random()
##    rand.seed(int(time()))
##    ec = inspyred.ec.EvolutionaryComputation(rand)
##    ec.terminator = inspyred.ec.terminators.evaluation_termination
##    ec.observer = inspyred.ec.observers.file_observer
##    ec.selector = inspyred.ec.selectors.tournament_selection
##    ec.replacer = inspyred.ec.replacers.generational_replacement
##    ec.variator = [inspyred.ec.variators.blend_crossover, inspyred.ec.variators.gaussian_mutation]
##    final_pop = ec.evolve(generator = mb.generate_FNN_weights,
##                          evaluator = mb.evaluate_FNN,
##                          pop_size=50,
##                          maximize=True,
##                          num_selected=50,
##                          tournament_size=2,
##                          num_elites=1,
##                          mutation_rate=0.3,
##                          max_evaluations=600,
##                          FNN_weights = 736,
##                          gaussian_stdev = 0.1,
##                          statistics_file=stat_file,
##                          individuals_file=ind_file)
##    stat_file.close()
##    ind_file.close()
##    # Sort and print the fittest individual, who will be at index 0.
##    final_pop.sort(reverse=True)
##    best = final_pop[0]
##    components = best.candidate
##    print('\nFittest individual:')
##    print(best)

    projdir = os.path.dirname(os.getcwd())
    stat_file_name = '{0}/statsFile.csv'.format(projdir)
    ind_file_name = '{0}/indFile.csv'.format(projdir)
    stat_file = open(stat_file_name, 'w')
    ind_file = open(ind_file_name, 'w')
    rand = Random()
    rand.seed(int(time()))
    ec = inspyred.ec.EvolutionaryComputation(rand)
    ec.terminator = inspyred.ec.terminators.evaluation_termination
    ec.observer = inspyred.ec.observers.file_observer
    ec.selector = inspyred.ec.selectors.tournament_selection
    ec.replacer = inspyred.ec.replacers.generational_replacement
    ec.variator = mb.cl.loopVariator
    final_pop = ec.evolve(generator = mb.cl.generateLoop,
                          evaluator = mb.evaluateLoop,
                          pop_size=10,
                          maximize=True,
                          num_selected=10,
                          tournament_size=2,
                          num_elites=1,
                          mutation_rate=0.3,
                          max_evaluations=600,
                          gaussian_stdev = 0.1,
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          inputLength = mb.inputLength, 
                          outputLength = mb.outputLength)
    stat_file.close()
    ind_file.close()
    # Sort and print the fittest individual, who will be at index 0.
    final_pop.sort(reverse=True)
    best = final_pop[0]
    components = best.candidate
    print('\nFittest individual:')
    print(best)

if __name__ == "__main__":
    sys.exit(main())


