from naoqi import *

# create python module
class atom4_moduleClass(ALModule):
  """Visual object recognition module"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    event_name = "PictureDetected"
    
    self.memory=ALProxy("ALMemory")
    self.motion=ALProxy("ALMotion")
    
    self.onLocation = [0,0]
    self.motion.setStiffnesses("Head",0.8)
#    self.onHeadPosition = [0,0,0,0,0,0]
 
  def dataChanged(self, strVarName, value, strMessage):
    """callback when previously programmed image is recognized"""

    print "datachanged", strVarName, " ", value, " ", strMessage
    global count
    count = count - 1

  def start(self):
    """Starts sound tracker"""
    try:
       self.memory.unsubscribeToEvent("PictureDetected",self.getName())
    except:
       pass
    self.memory.subscribeToEvent("PictureDetected",self.getName(),"dataChanged")
    print "started subscrube to picturedetected"
    
  def finish(self):
    """module bla"""
    try:
      self.memory.unsubscribeToEvent("PictureDetected",self.getName())
    except:
      pass
    self.isRunning = False

  def exit(self):
    try:
      self.memory.unsubscribeToEvent("PictureDetected",self.getName())
    except:
      pass
    self.isRunning=False
    ALModule.exit(self)
