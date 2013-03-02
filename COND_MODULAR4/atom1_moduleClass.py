from naoqi import *

class atom1_moduleClass(ALModule):
  """Movement tracking python module"""

  def __init__(self,name):
    ALModule.__init__(self,name)
    #self.tts=ALProxy("ALTextToSpeech")
    self.motion=ALProxy("ALMotion")
    print "__init__"
    self.BIND_PYTHON(self.getName(), "setParameter")
    self.movementdetection = ALProxy( "ALMovementDetection" )
    self.memory = ALProxy("ALMemory")
    self.movementdetection.setSensitivity(0.8)
    self.isRunning = False
    self.previousJointAngles = self.motion.getAngles("Head", True)
    self.currentJointAngles = self.motion.getAngles("Head", True)
    self.motion.setStiffnesses("Body", 0.0)
    self.motion.setStiffnesses("Head",0.6)
    
  def processEvent(self, *_args):
    self.processRunning = 1
    
    """method to process movement and move the head to it"""
    print "process Event top "
    print "process Event top  2"

    self.previousJointAngles = self.currentJointAngles
    #motion=ALProxy("ALMotion", "naoFernando.local", 9559)
    self.currentJointAngles = self.motion.getAngles("Head", True)    
    if(self.currentJointAngles != self.previousJointAngles):
      return
    data = self.memory.getData("MovementDetection/MovementInfo")
    result = data[0][0]
    self.motion.setAngles("Head", [self.currentJointAngles[0]  + result[0], self.currentJointAngles[1]  + result[1]], 0.1)
#    print result
#    yaw = self.currentJointAngles[0] + result[0]
#    pitch = self.currentJointAngles[1] + result[1]
#    yaw = clip( yaw, -1.0, 1.0)
#    pitch = clip( pitch, -0.45, -0.10)
#    print "processing"
#    self.motion.setAngles("Head", [yaw, pitch], 0.1)

  def exit(self):
    """destroy the module"""
    print "exit"
    self.isRunning = False
    ALModule.exit(self)

  def start(self):
    """Starts the movement detection module, it gets movement events, and sends them to the process Event method"""
    self.movementdetection.subscribe(self.getName())
    self.memory.subscribeToMicroEvent("MovementDetection/MovementDetected", self.getName(), "tracking", "processEvent")
    self.isRunning = True
    self.motion.setAngles("Head", [0.0, 0.1], 0.1)

  def finish(self):
    """module bla"""
    #self.memory.unsubscribeToEvent("WordRecognized", self.getName())
    self.memory.unsubscribeToMicroEvent("MovementDetection/MovementDetected", self.getName())
    self.movementdetection.unsubscribe(self.getName())
    self.isRunning = False


  def callback(self,var,val, msg):
      """module bla"""
      print val
                
