from naoqi import *

class atom0_moduleClass(ALModule):
  """module description"""

  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning = True
    self.tts=ALProxy("ALTextToSpeech")
    print "__init__"

  def modulemethod(self,a):
    """method description  (mandatory to have the method published)"""
    print "inside module method: "+str(a)
    self.tts.say(str(a))
    
  def exit(self):
    """destroy the module"""
    print "exit"
    self.isRunning = False
    ALModule.exit(self)

  def start(self):
    """module bla"""
    memory = ALProxy("ALMemory")
    memory.subscribeToEvent("WordRecognized", self.getName(), "callback")

  def finish(self):
    """module bla"""
    memory = ALProxy("ALMemory")
    memory.unsubscribeToEvent("WordRecognized", self.getName())

  def callback(self,var,val, msg):
      """module bla"""
      print val
                
