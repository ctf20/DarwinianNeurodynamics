from naoqi import *
import math
import almath
import random
import copy
# create python module
class sharedDataClass(ALModule):
  """Create an sharedData instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.memory = ALProxy("ALMemory")
    self.motion = ALProxy("ALMotion")
    self.motion.setSmartStiffnessEnabled(True)


#    listA = self.memory.getDataListName()
#    mapNumToKey = {}
#    for index,key in enumerate(listA):
#      mapNumToKey[index] = self.memory.getData(key)

    #Converts a genotype number to a data name in ALMemory 
    self.numToData = {1: "Device/SubDeviceList/ChestBoard/Button/Sensor/Value",
                   2: "Device/SubDeviceList/LFoot/Bumper/Left/Sensor/Value",
                   3: "Device/SubDeviceList/LFoot/Bumper/Right/Sensor/Value",
                   4: "Device/SubDeviceList/RFoot/Bumper/Left/Sensor/Value",
                   5: "Device/SubDeviceList/RFoot/Bumper/Right/Sensor/Value",
                   6: "Device/SubDeviceList/HeadPitch/Position/Actuator/Value",
                   7: "Device/SubDeviceList/HeadYaw/Position/Actuator/Value",
                   8: "Device/SubDeviceList/LAnklePitch/Position/Actuator/Value",
                   9: "Device/SubDeviceList/LAnkleRoll/Position/Actuator/Value",
                   10: "Device/SubDeviceList/LElbowRoll/Position/Actuator/Value",
                   11: "Device/SubDeviceList/LElbowYaw/Position/Actuator/Value",
                   12: "Device/SubDeviceList/LHand/Position/Actuator/Value",
                   13: "Device/SubDeviceList/LHipPitch/Position/Actuator/Value",
                   14: "Device/SubDeviceList/LHipRoll/Position/Actuator/Value",
                   15: "Device/SubDeviceList/LHipYawPitch/Position/Actuator/Value",
                   16: "Device/SubDeviceList/LKneePitch/Position/Actuator/Value",
                   17: "Device/SubDeviceList/LShoulderPitch/Position/Actuator/Value",
                   18: "Device/SubDeviceList/LShoulderRoll/Position/Actuator/Value",
                   19: "Device/SubDeviceList/LWristYaw/Position/Actuator/Value",
                   20: "Device/SubDeviceList/RAnklePitch/Position/Actuator/Value",
                   21: "Device/SubDeviceList/RAnkleRoll/Position/Actuator/Value",
                   22: "Device/SubDeviceList/RElbowRoll/Position/Actuator/Value",
                   23: "Device/SubDeviceList/RElbowYaw/Position/Actuator/Value",
                   24: "Device/SubDeviceList/RHand/Position/Actuator/Value",
                   25: "Device/SubDeviceList/RHipPitch/Position/Actuator/Value",
                   26: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   27: "Device/SubDeviceList/RHipRoll/Position/Actuator/Value",
                   28: "Device/SubDeviceList/RKneePitch/Position/Actuator/Value",
                   29: "Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value",
                   30: "Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value",
                   31: "Device/SubDeviceList/RWristYaw/Position/Actuator/Value",
                   32: "Device/SubDeviceList/HeadPitch/Hardness/Actuator/Value",
                   33: "Device/SubDeviceList/HeadYaw/Hardness/Actuator/Value",
                   34: "Device/SubDeviceList/LAnklePitch/Hardness/Actuator/Value",
                   35: "Device/SubDeviceList/LAnkleRoll/Hardness/Actuator/Value",
                   36: "Device/SubDeviceList/LElbowRoll/Hardness/Actuator/Value",
                   37: "Device/SubDeviceList/LElbowYaw/Hardness/Actuator/Value",
                   38: "Device/SubDeviceList/LHand/Hardness/Actuator/Value",
                   39: "Device/SubDeviceList/LHipPitch/Hardness/Actuator/Value",
                   40: "Device/SubDeviceList/LHipRoll/Hardness/Actuator/Value",
                   41: "Device/SubDeviceList/LHipYawPitch/Hardness/Actuator/Value",
                   42: "Device/SubDeviceList/LKneePitch/Hardness/Actuator/Value",
                   43: "Device/SubDeviceList/LShoulderPitch/Hardness/Actuator/Value",
                   44: "Device/SubDeviceList/LShoulderRoll/Hardness/Actuator/Value",
                   45: "Device/SubDeviceList/LWristYaw/Hardness/Actuator/Value",
                   46: "Device/SubDeviceList/RAnklePitch/Hardness/Actuator/Value",
                   47: "Device/SubDeviceList/RAnkleRoll/Hardness/Actuator/Value",
                   48: "Device/SubDeviceList/RElbowRoll/Hardness/Actuator/Value",
                   49: "Device/SubDeviceList/RElbowYaw/Hardness/Actuator/Value",
                   50: "Device/SubDeviceList/RHand/Hardness/Actuator/Value",
                   51: "Device/SubDeviceList/RHipPitch/Hardness/Actuator/Value",
                   52: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   53: "Device/SubDeviceList/RHipRoll/Hardness/Actuator/Value",
                   54: "Device/SubDeviceList/RKneePitch/Hardness/Actuator/Value",
                   55: "Device/SubDeviceList/RShoulderPitch/Hardness/Actuator/Value",
                   56: "Device/SubDeviceList/RShoulderRoll/Hardness/Actuator/Value",
                   57: "Device/SubDeviceList/RWristYaw/Hardness/Actuator/Value",
                   58: "Device/SubDeviceList/HeadPitch/Position/Sensor/Value",
                   59: "Device/SubDeviceList/HeadYaw/Position/Sensor/Value",
                   60: "Device/SubDeviceList/LAnklePitch/Position/Sensor/Value",
                   61: "Device/SubDeviceList/LAnkleRoll/Position/Sensor/Value",
                   62: "Device/SubDeviceList/LElbowRoll/Position/Sensor/Value",
                   63: "Device/SubDeviceList/LElbowYaw/Position/Sensor/Value",
                   64: "Device/SubDeviceList/LHand/Position/Sensor/Value",
                   65: "Device/SubDeviceList/LHipPitch/Position/Sensor/Value",
                   66: "Device/SubDeviceList/LHipRoll/Position/Sensor/Value",
                   67: "Device/SubDeviceList/LHipYawPitch/Position/Sensor/Value",
                   68: "Device/SubDeviceList/LKneePitch/Position/Sensor/Value",
                   69: "Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value",
                   70: "Device/SubDeviceList/LShoulderRoll/Position/Sensor/Value",
                   71: "Device/SubDeviceList/LWristYaw/Position/Sensor/Value",
                   72: "Device/SubDeviceList/RAnklePitch/Position/Sensor/Value",
                   73: "Device/SubDeviceList/RAnkleRoll/Position/Sensor/Value",
                   74: "Device/SubDeviceList/RElbowRoll/Position/Sensor/Value",
                   75: "Device/SubDeviceList/RElbowYaw/Position/Sensor/Value",
                   76: "Device/SubDeviceList/RHand/Position/Sensor/Value",
                   77: "Device/SubDeviceList/RHipPitch/Position/Sensor/Value",
                   78: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   79: "Device/SubDeviceList/RHipRoll/Position/Sensor/Value",
                   80: "Device/SubDeviceList/RKneePitch/Position/Sensor/Value",
                   81: "Device/SubDeviceList/RShoulderPitch/Position/Sensor/Value",
                   82: "Device/SubDeviceList/RShoulderRoll/Position/Sensor/Value",
                   83: "Device/SubDeviceList/RWristYaw/Position/Sensor/Value",
                   84: "Device/SubDeviceList/HeadPitch/ElectricCurrent/Sensor/Value",
                   85: "Device/SubDeviceList/HeadYaw/ElectricCurrent/Sensor/Value",
                   86: "Device/SubDeviceList/LAnklePitch/ElectricCurrent/Sensor/Value",
                   87: "Device/SubDeviceList/LAnkleRoll/ElectricCurrent/Sensor/Value",
                   88: "Device/SubDeviceList/LElbowRoll/ElectricCurrent/Sensor/Value",
                   89: "Device/SubDeviceList/LElbowYaw/ElectricCurrent/Sensor/Value",
                   90: "Device/SubDeviceList/LHand/ElectricCurrent/Sensor/Value",
                   91: "Device/SubDeviceList/LHipPitch/ElectricCurrent/Sensor/Value",
                   92: "Device/SubDeviceList/LHipRoll/ElectricCurrent/Sensor/Value",
                   93: "Device/SubDeviceList/LHipYawPitch/ElectricCurrent/Sensor/Value",
                   94: "Device/SubDeviceList/LKneePitch/ElectricCurrent/Sensor/Value",
                   95: "Device/SubDeviceList/LShoulderPitch/ElectricCurrent/Sensor/Value",
                   96: "Device/SubDeviceList/LShoulderRoll/ElectricCurrent/Sensor/Value",
                   97: "Device/SubDeviceList/LWristYaw/ElectricCurrent/Sensor/Value",
                   98: "Device/SubDeviceList/RAnklePitch/ElectricCurrent/Sensor/Value",
                   99: "Device/SubDeviceList/RAnkleRoll/ElectricCurrent/Sensor/Value",
                   100: "Device/SubDeviceList/RElbowRoll/ElectricCurrent/Sensor/Value",
                   101: "Device/SubDeviceList/RElbowYaw/ElectricCurrent/Sensor/Value",
                   102: "Device/SubDeviceList/RHand/ElectricCurrent/Sensor/Value",
                   103: "Device/SubDeviceList/RHipPitch/ElectricCurrent/Sensor/Value",
                   104: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   105: "Device/SubDeviceList/RHipRoll/ElectricCurrent/Sensor/Value",
                   106: "Device/SubDeviceList/RKneePitch/ElectricCurrent/Sensor/Value",
                   107: "Device/SubDeviceList/RShoulderPitch/ElectricCurrent/Sensor/Value",
                   108: "Device/SubDeviceList/RShoulderRoll/ElectricCurrent/Sensor/Value",
                   109: "Device/SubDeviceList/RWristYaw/ElectricCurrent/Sensor/Value",
                   110: "Device/SubDeviceList/HeadPitch/Temperature/Sensor/Value",
                   111: "Device/SubDeviceList/HeadYaw/Temperature/Sensor/Value",
                   112: "Device/SubDeviceList/LAnklePitch/Temperature/Sensor/Value",
                   113: "Device/SubDeviceList/LAnkleRoll/Temperature/Sensor/Value",
                   114: "Device/SubDeviceList/LElbowRoll/Temperature/Sensor/Value",
                   115: "Device/SubDeviceList/LElbowYaw/Temperature/Sensor/Value",
                   116: "Device/SubDeviceList/LHand/Temperature/Sensor/Value",
                   117: "Device/SubDeviceList/LHipPitch/Temperature/Sensor/Value",
                   118: "Device/SubDeviceList/LHipRoll/Temperature/Sensor/Value",
                   119: "Device/SubDeviceList/LHipYawPitch/Temperature/Sensor/Value",
                   120: "Device/SubDeviceList/LKneePitch/Temperature/Sensor/Value",
                   121: "Device/SubDeviceList/LShoulderPitch/Temperature/Sensor/Value",
                   122: "Device/SubDeviceList/LShoulderRoll/Temperature/Sensor/Value",
                   123: "Device/SubDeviceList/LWristYaw/Temperature/Sensor/Value",
                   124: "Device/SubDeviceList/RAnklePitch/Temperature/Sensor/Value",
                   125: "Device/SubDeviceList/RAnkleRoll/Temperature/Sensor/Value",
                   126: "Device/SubDeviceList/RElbowRoll/Temperature/Sensor/Value",
                   127: "Device/SubDeviceList/RElbowYaw/Temperature/Sensor/Value",
                   128: "Device/SubDeviceList/RHand/Temperature/Sensor/Value",
                   129: "Device/SubDeviceList/RHipPitch/Temperature/Sensor/Value",
                   130: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   131: "Device/SubDeviceList/RHipRoll/Temperature/Sensor/Value",
                   132: "Device/SubDeviceList/RKneePitch/Temperature/Sensor/Value",
                   133: "Device/SubDeviceList/RShoulderPitch/Temperature/Sensor/Value",
                   134: "Device/SubDeviceList/RShoulderRoll/Temperature/Sensor/Value",
                   135: "Device/SubDeviceList/RWristYaw/Temperature/Sensor/Value",
                   136: "Device/SubDeviceList/US/Left/Sensor/Value",
                   137: "Device/SubDeviceList/US/Right/Sensor/Value",
                   138: "Device/SubDeviceList/InertialSensor/GyroscopeX/Sensor/Value",
                   139: "Device/SubDeviceList/InertialSensor/GyroscopeY/Sensor/Value",
                   140: "Device/SubDeviceList/InertialSensor/GyroscopeZ/Sensor/Value",
                   141: "Device/SubDeviceList/InertialSensor/AccelerometerX/Sensor/Value",
                   142: "Device/SubDeviceList/InertialSensor/AccelerometerY/Sensor/Value",
                   143: "Device/SubDeviceList/InertialSensor/AccelerometerZ/Sensor/Value",
                   144: "Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value",
                   145: "Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value",
                   146: "Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value",
                   147: "Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value",
                   148: "Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value",
                   149: "Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value",
                   150: "Device/SubDeviceList/LFoot/FSR/TotalWeight/Sensor/Value",
                   151: "Device/SubDeviceList/RFoot/FSR/FrontLeft/Sensor/Value",
                   152: "Device/SubDeviceList/RFoot/FSR/FrontRight/Sensor/Value",
                   153: "Device/SubDeviceList/RFoot/FSR/RearLeft/Sensor/Value",
                   154: "Device/SubDeviceList/RFoot/FSR/RearRight/Sensor/Value",
                   155: "Device/SubDeviceList/RFoot/FSR/TotalWeight/Sensor/Value",
                   156: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   157: "Device/SubDeviceList/LFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   158: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/X/Sensor/Value",
                   159: "Device/SubDeviceList/RFoot/FSR/CenterOfPressure/Y/Sensor/Value",
                   160: "Device/SubDeviceList/Head/Touch/Front/Sensor/Value",
                   161: "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value",
                   162: "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value",
                   163: "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value",
                   164: "Device/SubDeviceList/LHand/Touch/Left/Sensor/Value",
                   165: "Device/SubDeviceList/LHand/Touch/Right/Sensor/Value",
                   166: "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value",
                   167: "Device/SubDeviceList/RHand/Touch/Left/Sensor/Value",
                   168: "Device/SubDeviceList/RHand/Touch/Right/Sensor/Value",
                   169: "footContact",
                   170: "leftFootContact",
                   171: "rightFootContact",
                   172: "leftFootTotalWeight",
                   173: "rightFootTotalWeight",
                   174: "BodyStiffnessChanged",
                   175: "RightBumperPressed",
                   176: "LeftBumperPressed",
                   177: "ChestButtonPressed",
                   178: "FrontTactilTouched",
                   179: "RearTactilTouched",
                   180: "MiddleTactilTouched",
                   181: "HotJoinDetected",
                   182: "HandRightBackTouched",
                   183: "HandRightLeftTouched",
                   184: "HandRightRightTouched",
                   185: "HandLeftBackTouched",
                   186: "HandLeftLeftTouched",
                   187: "HandLeftRightTouched",
                   188: "WordRecognized"}
 #                  189: "RedBallDetected"}
                   #Further data can be entered into the ALMemory with insertData by action atoms as required.
                   #And then they can raise events to put data into this space as needed.

   #Converts a genotype number to a event name in ALMemory 
    self.numToEvent = {1 : "FaceDetected",
                  2 : "WordRecognized",
                  3 : "SoundLocated",
                  4 : "SoundDetected",
                  5 : "redBallDetected",
                  6 : "PictureDetected",
                  7 : "MovementDetected",
                  8 : "LandmarkDetected",
                  9 : "HotJoinDeteced"}
    #Again, further events can be added as required.
    # Example showing how to get the names of all the joints in the body.
    bodyNames = self.motion.getBodyNames("Body")
    self.numToMotion = {}
    j = 1
    for i in bodyNames:
      self.numToMotion[j] = i
      j = j + 1


    self.numToMesg = {}#Initially empty dictionary of message numbers. 



    #print self.numToMotion
    #exit(0)
  
 
    



  def getRandomMemoryInputs(self, n):
    length = len(self.numToData)
    return [random.randint(1,length) for r in xrange(n)] 

  def getRandomMemoryMesgInputs(self, n):
    length = len(self.numToMesg)
    if length > 0:
      return [random.randint(1,length) for r in xrange(n)]
    else:
      return [1 for r in xrange(n)]

  def getRandomEventInputs(self, n):
    length = len(self.numToEvent)
    return [random.randint(1,length) for r in xrange(n)] 

  def getRandomMotors(self, n):
    length = len(self.numToMotion)
    a= list(set([random.randint(1,length) for r in xrange(n)]))
    while len(a) is not n:
      a = list(set([random.randint(1,length) for r in xrange(n)]))
    return a            

  def getRandWithinRanges(self, val):
    return [[20*(random.random()-1.0), 20*(random.random())] for r in xrange(len(val))]

  def insertData(self, val):
    ld = len(self.numToData)
    self.numToData[ld+1] = val
    print "Inserted Data " + str(val) + "to position " + str(ld+1)

  def insertMesg(self, val):
    ld = len(self.numToMesg)
    self.numToMesg[ld+1] = val

  def insertEvent(self, val):
    le = len(self.numToEvent)
    self.numToEvent[le+1] = val

  def getLengthData(self):
    print len("Number of datakeys = " + str(self.numToData))
    
  def getLengthEvents(self):
    print len("Number of events = " + str(self.numToEvent))

  def getDataName(self, i):
    return self.numToData[i]

  def getMesgName(self, i):
    return self.numToMesg[i]

  def getEventName(self, i):
    return self.numToEvent[i]
  
  def getMotorName(self, i):
    return self.numToMotion[i]
  
  def start(self):
    """Start actor module"""
    try:
        print "Starting shared data module"
        pass
    except:
        pass
   
  def finish(self):
    """module bla"""
    try:
        pass
    except:
        pass
    self.isRunning = False

  def exit(self):
    print "Exiting sharedData"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
