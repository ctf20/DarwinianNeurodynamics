import os
import sys

lib_path = os.path.abspath('../')
sys.path.append(lib_path)

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
from naoqi import ALProxy
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.neuralnets import NNregression 
from pybrain.tools.plotting import MultilinePlotter
import pyentropy as ent

#Skeleton by Dave Snowdon (2013, thanks Dave!) 


#ROBOT_IP = "169.254.29.204" #"Systemss-MacBook-Pro-2.local" #"169.254.29.204"
ROBOT_IP = "ctf.local"
ROBOT_PORT = 9559
ASSESSMENT_PERIOD = 50
GOAL_BABBLE_PERIOD = 100
INPUTSIZE = 2
OUTPUTSIZE = 1
HIDDENSIZE = 2
PREDICTSIZE = 1
PRUNE_THRESHOLD = 2

#Files for saving stuff to. 
projdir = os.path.dirname(os.getcwd())
time_file_name = '{0}/timeSeries.txt'.format(projdir)
time_file = open(time_file_name, 'w')

#Files for saving stuff to. 
projdir = os.path.dirname(os.getcwd())
dbn_file_name = '{0}/dataforDBN.txt'.format(projdir)
dbn_file = open(dbn_file_name, 'w')


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

         #Hierarchical Control Networks 
         self.netH1 = buildNetwork(INPUTSIZE,HIDDENSIZE,OUTPUTSIZE)
         self.netH2 = buildNetwork(INPUTSIZE,HIDDENSIZE,OUTPUTSIZE)
         self.sMemory1 = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.sMemory2 = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory1 = np.array([0]*OUTPUTSIZE)
         self.mMemory2 = np.array([0]*OUTPUTSIZE)
         

         # Access global joint limits.
         self.Body = motion.getLimits("Body")
         self.bangles =  [1] * 26
         self.othersens = [2] * 18
         self.sMemory = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory = np.array([0]*OUTPUTSIZE)
         self.cl = curiosityLoop()

         self.rand = Random()
         self.rand.seed(int(time()))

         #Initialize a model dictionary
         self.models = dict()
         

         
     def updateModels(self, sensedAngles, index_m,index_s,mot_t,sens_t,sens_t2, motor_state_t, motor_state_t_p1):
         #Maintain a dictionary of models which store pure data.
         #1. Check if the key already exists
         k = "m" + str(index_m) + "_s" + str(index_s)
         if k not in self.models:
              #2. If its not, then create the key and enter the new value into a list of values
              self.models[k] = []
              self.models[k].append([mot_t, sens_t, sens_t2, motor_state_t, motor_state_t_p1])  
         else:
              self.models[k].append([mot_t, sens_t, sens_t2, motor_state_t, motor_state_t_p1]) 
              pass
         dbn_file.write(str(sensedAngles))         
         dbn_file.write("\n")
          

         
         pass
         
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
         sleep(0.5)


     def set_motor_values(self, ma,val):

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


     def set_motor_valuesH(self, ma1,ma2, val1, val2):

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
         motorAngles[val1] = ma1[0]
         motorAngles[val2] = ma2[0]

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
             sensedAngles = self.get_sensor_values()
             motorAngles  = self.compute_new_motor_angles(sensedAngles)
             self.set_motor_values(motorAngles)
             sleep(0.3)

     def calcGoalScore(self, j): #J[0] contains the joint position(s) to be tested.
          #self.rest()
          #print("testing" + str(j) )
          
          #Get sensor state at t
          sensedAngles = self.get_sensor_values()
          pv = sensedAngles[self.x2]

          #Get  motor state at t
          motor_state_t = sensedAngles[self.x1]

          #Set motors and do the action 
          self.set_motor_values(j, self.x1)
          
          sleep(0.3)

          #Get new sensor values at t+1
          sensedAngles = self.get_sensor_values()
          pv2 = sensedAngles[self.x2]
          
          #Get motor state at t+1
          motor_state_t_p1 = sensedAngles[self.x1]
          
          #Update the inverse and the forward models here (for single sm contingency pairs)
          self.updateModels(sensedAngles, self.x1,self.x2,j[0],pv,pv2, motor_state_t, motor_state_t_p1)
          
          f = pow(pv2-self.randomGoal,2)
          #print( "Now pos = " + str(pv2) + "Goal = " + str(self.randomGoal) + ": Fitness = " + str(f)+ "\n")
          #print(self.x1, self.x2, pv, pv2, f)
          return f

     def goalBabble(self, x):
         print("Doing goal babbling now\n")
         p = self.net.params
         p[:] = x[3]
         
         i = 0
         self.sMemory = np.array([1]*(INPUTSIZE + PREDICTSIZE))
         self.mMemory = np.array([0]*OUTPUTSIZE)
         self.rest()
         sensedAngles = self.get_sensor_values()
         pv = sensedAngles[x[2]]
         #Choose a goal sensor value in the range of the predicted angle
         #self.randomGoal = self.rand.uniform(self.Body[x[1]][0],self.Body[x[1]][1])
         for i in range(2):
              self.randomGoal = self.rand.uniform(-0.5,0.5)
              print(self.randomGoal)
              #CMA-ES can be used to discover joint angles that get
              #closer to the goal state!!!!!!!!
              self.x1 = x[1]
              self.x2 = x[2]
              print("Range motor = " + str(self.Body[x[1]][0]) +  " " + str(self.Body[x[1]][1]))
              initG = [self.rand.uniform(self.Body[x[1]][0],self.Body[x[1]][1]),self.rand.uniform(self.Body[x[1]][0],self.Body[x[1]][1])]
              print("Initial motor  = " + str(initG))
 #             res = cma.fmin(self.calcGoalScore, initG, (self.Body[x[1]][1]- self.Body[x[1]][0])/10.0,maxfevals=200, verb_disp=1, bounds=[self.Body[x[1]][0]-1, self.Body[x[1]][1]+1] )
#              res = cma.fmin(self.calcGoalScore, initG, 0.1,maxfevals=200, verb_disp=1, bounds=[-10,10])
              res = cma.fmin(self.calcGoalScore, initG, 0.1,maxfevals=50, verb_disp=1)

   #           cma.plot()
#              cma.show()

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
 #        self.postureProxy.applyPosture("LyingBack", 1.0)
         self.rest()

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
         #The agent x is compared with the archieve in order to see what fitness decrement it will be penalized by based on its similarity to the archieve.
         fitnessMod = self.cl.getSimilarity(x)
         print("fit mod = " + str(fitnessMod))
         fitness = fitness - fitnessMod
         
         return fitness
         #return np.random.randn(1)[0]

     #Hierarchical Calculate Fitness 
     def calculateFitnessH(self, x):
          #Take the hierarchical genotype, execute it, return its fitness.
          
          weights1 = x[1].candidate[3]
          weights2 = x[2].candidate[3]
          p1 = self.netH1.params
          p2 = self.netH2.params
          p1[:] = weights1
          p2[:] = weights2
          #Initialize data structures for fitness test of this actor. 
          fitness = 0
          i = 0
          self.sMemory1 = np.array([1]*(INPUTSIZE + PREDICTSIZE))
          self.sMemory2 = np.array([1]*(INPUTSIZE + PREDICTSIZE))
          self.mMemory1 = np.array([0]*OUTPUTSIZE)
          self.mMemory2 = np.array([0]*OUTPUTSIZE)
          
          self.rest()
          while i < ASSESSMENT_PERIOD: #Run behaviour and store the sensorimotor data
               sensedAngles = self.get_sensor_values()
               sv1 = [sensedAngles[x[1].candidate[0][0]], sensedAngles[x[1].candidate[0][1]]]
               sv2 = [sensedAngles[x[2].candidate[0][0]], sensedAngles[x[2].candidate[0][1]]]
               pv1 = sensedAngles[x[1].candidate[2]]
               pv2 = sensedAngles[x[2].candidate[2]]
               motorAngles1 = self.compute_new_motor_angles(sv1)
               motorAngles2 = self.compute_new_motor_angles(sv2)
               self.set_motor_valuesH(motorAngles1, motorAngles2, x[1].candidate[1], x[2].candidate[1])
               self.addToMemory1(np.hstack( (np.array(sv1), (np.array(pv1)) )), np.array(motorAngles1))               
               self.addToMemory2(np.hstack( (np.array(sv2), (np.array(pv2)) )), np.array(motorAngles2))
               sleep(0.1)
               i = i + 1

          smMatrix = np.array(np.hstack((self.sMemory1,self.sMemory2, self.mMemory1, self.mMemory2)))
          print(smMatrix)
          fitness = self.getFitnessH(smMatrix)
          #The agent x is compared with the archieve in order to see what fitness decrement it will be penalized by based on its similarity to the archieve.
          fitnessMod = self.cl.getSimilarity(x)
          print("fit mod H = " + str(fitnessMod))
          fitness = fitness - fitnessMod
          return fitness


     def addToMemory(self, sensors,motors): #Store the sm state into memory
          self.sMemory = np.row_stack((self.sMemory,sensors))
          self.mMemory = np.row_stack((self.mMemory,motors))
          pass

     def addToMemory1(self, sensors,motors): #Store the sm state into memory
          self.sMemory1 = np.row_stack((self.sMemory1,sensors))
          self.mMemory1 = np.row_stack((self.mMemory1,motors))
          pass
     def addToMemory2(self, sensors,motors): #Store the sm state into memory
          self.sMemory2 = np.row_stack((self.sMemory2,sensors))
          self.mMemory2 = np.row_stack((self.mMemory2,motors))
          pass


     def pesos_conexiones(self,n):
          for mod in n.modules:
               for conn in n.connections[mod]:
                    print conn
                    for cc in range(len(conn.params)):
                         print conn.whichBuffers(cc), conn.params[cc]

                         
     def getFitness(self, smMatrix): #Store the sm state into memory
          fit = 0

          #Fitness function (4) ******************************************
          #Mutual Information between motor command and predicted sensory state. 
          sp = smMatrix[1:,3]
          mot = smMatrix[1:,2]
          spQ = ent.quantise(sp,10)
          motQ = ent.quantise(mot,10)
          s = ent.DiscreteSystem(spQ[0],(1,10), motQ[0],(1,10))
          print(str(spQ[0]) + "\n" + str(motQ[0]))
          s.calculate_entropies(method='pt', calc=['HX', 'HXY'])
          mutInf = s.I()
          fit = mutInf
          print(fit)
          return fit
##          #Fitness function (3) *************************************************************
##          #Record the sm data for this loop and consider its properties
##          #print(smMatrix)
##          #print(len(smMatrix))
##
##          time_file.write("\n".join(str(elem) for elem in smMatrix))
##          time_file.write("\n")
##          np.savetxt("timeSeries2.csv", smMatrix, delimiter=",")
##
##          #net = buildNetwork(3,10,1, bias = True)
##          net = FeedForwardNetwork()
##          inp = LinearLayer(3)
##          h1 = SigmoidLayer(10)
##          outp = LinearLayer(1)
##          # add modules
##          net.addOutputModule(outp)
##          net.addInputModule(inp)
##          net.addModule(h1)
##          # create connections
##          iToH = FullConnection(inp, h1)
##          hToO = FullConnection(h1, outp)
##          net.addConnection(iToH)
##          net.addConnection(hToO)
##          # finish up
##          net.sortModules()
##
##          ds = SupervisedDataSet(3, 1)
##
##          trainSet = []
##          for index_x, x in enumerate(smMatrix):
##               if index_x > 0 and index_x < len(smMatrix)-1:
##                    #trainSet.append( [smMatrix[index_x][0], smMatrix[index_x][1], smMatrix[index_x][2], smMatrix[index_x+1][3] ] )
##                    ds.addSample(([smMatrix[index_x][0], smMatrix[index_x][1], smMatrix[index_x][2]]), (smMatrix[index_x+1][3]))
##          #print(trainSet)
##          #print(ds)
##          trainer = BackpropTrainer(net, ds, weightdecay=0.01)
##          err = trainer.trainUntilConvergence(maxEpochs = 50)
##          #Visualize the network performance and structure.
##
##          #nn = NNregression(ds, epoinc = 10)
##          #nn.setupNN()
##          #nn.runTraining()
##          #self.pesos_conexiones(net)
##          #print("Input to hidden", iToH.params)
##          #print("H to output", hToO.params)
##          #print(iToH.params)
##          n1 = iToH.params
##          n1a= zip(*[iter(n1)]*3)
##          n2 = hToO.params
##          
##          sums = []
##          for x in n1a:
##               sumr = 0
##               for y in x:
##                    sumr = sumr + abs(y)
##               sums.append(sumr)
##                         
##          sums2 = []
##          for x in n2:
##               sums2.append(abs(x))
##          
##          #Choose those neurons that have inputs below a threshold value
##          a1 = [index for index,value in enumerate(sums) if value > 2.0]
##          a2 = [index for index,value in enumerate(sums2) if value > 0.5]
##          inter = len(set(a1).intersection( set(a2) ))
##          fit = inter
##          #fit = sum(n1a[:]) + sum(n2[:])
##          print fit
##          return fit

          #Fitness functions (1) ************************************************************
          #1. Maximize sonar values.
          #print(smMatrix)
          #fit = sum(smMatrix[:])
          #print fit
          #return fit

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

                         
     def getFitnessH(self, smMatrix): #Store the sm state into memory
          fit = 0

          #Fitness function (1) ******************************************
          #Mutual Information between two motors and the first prediced sensor dimension
          
          sp = smMatrix[1:,2] #Only predicts the first sensory outcome. 
          mot1 = smMatrix[1:,6]
          mot2 = smMatrix[1:,7]
          spQ = ent.quantise(sp,10)
          motQ1 = ent.quantise(mot1,10)
          motQ2 = ent.quantise(mot2,10)
#          print(motQ1[0])
#          print(motQ2[0])
          motQ = np.row_stack((motQ1[0],motQ2[0]))
#          print(motQ)
          s = ent.DiscreteSystem(motQ,(2,10), spQ[0],(1,10))
          print(str(spQ[0]) + "\n" + str(motQ))
          s.calculate_entropies(method='pt', calc=['HX', 'HXY'])
          mutInf = s.I()
          fit = mutInf
          print(fit)
          return fit

          #Fitness function (2)  ******************************************
          #MI between both motors and both sensors 
##          sp1 = smMatrix[1:,2]
##          sp2 = smMatrix[1:,5]
##          mot1 = smMatrix[1:,6]
##          mot2 = smMatrix[1:,7]
##          spQ1 = ent.quantise(sp1,10)
##          spQ2 = ent.quantise(sp2,10)
##          motQ1 = ent.quantise(mot1,10)
##          motQ2 = ent.quantise(mot2,10)
###          print(motQ1[0])
###          print(motQ2[0])
##          motQ = np.row_stack((motQ1[0],motQ2[0]))
##          spQ = np.row_stack((spQ1[0],spQ2[0]))
##
###          print(motQ)
##          s = ent.DiscreteSystem(motQ,(2,10), spQ,(2,10))
##          print(str(spQ) + "\n" + str(motQ))
##          s.calculate_entropies(method='plugin', calc=['HX', 'HXY'])
##          mutInf = s.I()
##          fit = mutInf
##          print(fit)
##          return fit
##
     
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
          #print(type(fitness))
          return fitness
     #Function called at each generation, can be used to do other things than
     #search for new SM contingencies.


     def evaluateLoopH(self, candidates, args):
          fitness = []
          for cs in candidates:
               fit = self.calculateFitnessH(cs)
               fitness.append(fit)
          #print(type(fitness))
          return fitness
     
     def myObserver(self, population, num_generations, num_evaluations, args):
         best = max(population)
         print('{0:6} -- {1} : {2}'.format(num_generations, 
                                      best.fitness, 
                                      str(best.candidate)))
         
         #Store the best candidate in an archieve and use this to punish exisiting solutions in the population.
         #1. On convergence, or simply every M generations, move the best individual into an archieve...
         #2. Later the archieve may also be used to bias the varation operator (but not yet).
         #Depending on the state of the archieve, do goal-babbling

         if num_generations%5 is 0 and best.fitness > 3.0:
              self.cl.addToArchieve(best)
 #             self.goalBabble(best.candidate)

         #add models to a file every now and again
         if num_generations%10 is 0:
              projdir = os.path.dirname(os.getcwd())
              arch_file_name = '{0}/models.txt'.format(projdir)
              arch_file = open(arch_file_name, 'w')
              arch_file.write(str(self.models))
              arch_file.write("\n")
              arch_file.close()

     
     def myObserverH(self, population, num_generations, num_evaluations, args):
         best = max(population)
         print('{0:6} -- {1} : {2}'.format(num_generations, 
                                      best.fitness, 
                                      str(best.candidate)))
         
         #Store the best candidate in an archieve and use this to punish exisiting solutions in the population.
         #1. On convergence, or simply every M generations, move the best individual into an archieve...
         #2. Later the archieve may also be used to bias the varation operator (but not yet).
         #Depending on the state of the archieve, do goal-babbling

         if num_generations%5 is 0 and best.fitness > 3.0:
              self.cl.addToArchieveH(best)
 #             self.goalBabble(best.candidate)
         
 

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
    
    #Primitive action evolution (evolving primitive reflexes???)
    ec = inspyred.ec.EvolutionaryComputation(mb.rand)
    #ec = inspyred.ec.emo.NSGA2(rand)
    #ec = inspyred.ec.GA(rand)
    #ec = inspyred.ec.ES(rand)
    ec.terminator = inspyred.ec.terminators.evaluation_termination
    ec.observer = [inspyred.ec.observers.file_observer, mb.myObserver]
    ec.selector = inspyred.ec.selectors.tournament_selection
    ec.replacer = inspyred.ec.replacers.generational_replacement
    ec.variator = mb.cl.loopVariator
    final_pop = ec.evolve(generator = mb.cl.generateLoop,
                          evaluator = mb.evaluateLoop,
                          pop_size=1,
                          maximize=True,
                          num_selected=1,
                          tournament_size=2,
                          num_elites=0,
                          HIDDENSIZE = 2,
                          max_evaluations=2,
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          inputLength = mb.inputLength, 
                          outputLength = mb.outputLength)
    stat_file.close()
    ind_file.close()
    time_file.close()
#    inspyred.ec.analysis.generation_plot(stat_file_name)

    #************************************************************************
    #Now evolve hierarchical actions (combining reflexes in interesting ways) 
    print("Starting hierarchical action evolution\n")

    stat_file_name = '{0}/statsFileH.csv'.format(projdir)
    ind_file_name = '{0}/indFileH.csv'.format(projdir)
    stat_file = open(stat_file_name, 'w')
    ind_file = open(ind_file_name, 'w')
    ec = inspyred.ec.EvolutionaryComputation(mb.rand)
    ec.terminator = inspyred.ec.terminators.evaluation_termination
    ec.observer = [inspyred.ec.observers.file_observer, mb.myObserverH]
    ec.selector = inspyred.ec.selectors.tournament_selection
    ec.replacer = inspyred.ec.replacers.generational_replacement
    ec.variator = mb.cl.loopVariatorH
    final_pop = ec.evolve(generator = mb.cl.generateLoopH,
                          evaluator = mb.evaluateLoopH,
                          pop_size=10,
                          maximize=True,
                          num_selected=10,
                          tournament_size=2,
                          num_elites=0,
                          HIDDENSIZE = 2,
                          max_evaluations=5000,
                          statistics_file=stat_file,
                          individuals_file=ind_file,
                          inputLength = mb.inputLength, 
                          outputLength = mb.outputLength)
    stat_file.close()
    ind_file.close()
    time_file.close()
    inspyred.ec.analysis.generation_plot(stat_file_name)
    

##    if True:
##        final_arc = ec.archive
##        print('Best Solutions: \n')
##        for f in final_arc:
##            print(f)
##        import pylab
##        x = []
##        y = []
##        for f in final_arc:
##            x.append(f.fitness[0])
##            y.append(f.fitness[1])
##        pylab.scatter(x, y, color='b')
##        pylab.savefig('{0} Example ({1}).pdf'.format(ea.__class__.__name__, 
##                                                     problem.__class__.__name__), 
##                      format='pdf')
##        pylab.show()

    # Sort and print the fittest individual, who will be at index 0
    final_pop.sort(reverse=True)
    best = final_pop[0]
    components = best.candidate
    print('\nFittest individual:')
    print(best)

    
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

