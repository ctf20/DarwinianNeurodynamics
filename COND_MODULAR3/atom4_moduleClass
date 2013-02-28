from naoqi import *

# create python module
class atom3_moduleClass(ALModule):
  """Sound tracking module"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.memory=ALProxy("ALMemory")
    self.motion=ALProxy("ALMotion")
    
    self.onLocation = [0,0]
    self.motion.setStiffnesses("Head",0.8)
#    self.onHeadPosition = [0,0,0,0,0,0]
 
  def callbackMoveHeadtoSound(self,p, q, r):
    print q
    print "\n";
    if q[1][2] >= 0.6:
      self.onLocation = [q[1][0],q[1][1]]
 #     self.onHeadPosition = [r[0],r[1],r[2],r[3],r[4],r[5]]
      self.motion.changeAngles("Head", self.onLocation, 0.2)
     
          
  def start(self):
    """Starts sound tracker"""
    try:
       self.memory.unsubscribeToEvent("ALAudioSourceLocalization/SoundLocated",self.getName())
    except:
       pass
    self.memory.subscribeToEvent("ALAudioSourceLocalization/SoundLocated",self.getName(),"callbackMoveHeadtoSound")
    print "started subscrube to sound"
    
  def finish(self):
    """module bla"""
    try:
      self.memory.unsubscribeToEvent("ALAudioSourceLocalization/SoundLocated",self.getName())
    except:
      pass
    self.isRunning = False

  def exit(self):
    try:
      self.memory.unsubscribeToEvent("ALAudioSourceLocalization/SoundLocated",self.getName())
    except:
      pass
    self.isRunning=False
    ALModule.exit(self)
