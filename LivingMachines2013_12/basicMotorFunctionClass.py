from naoqi import *
import math
import almath
from time import time, sleep
# create python module
class basicMotorFunctionClass(ALModule):
  """Create a basic motor function instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.motion = ALProxy("ALMotion", "ctf.local", 9559)
    self.Body = self.motion.getLimits("Body")
    self.set_stiffness(1.0)


  def set_stiffness(self, val):
         self.motion.setStiffnesses("Body", val)
    
  def rest(self):
         #print "putting into rest state"
         fractionMaxSpeed  = 1.0
 #        self.motion.setStiffnesses("Body", 1.0)

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
                   
         self.motion.setAngles("Body", motorAngles, fractionMaxSpeed)
 #        self.motion.setStiffnesses("Body",0.0)
         sleep(0.3)
        # print "end of rest state"

 
  def start(self):
    """Start basic motor function module"""
    try:
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
    print "Exit basic motor function module"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
