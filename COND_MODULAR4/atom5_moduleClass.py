from naoqi import *
import math
import almath

# create python module
class atom5_moduleClass(ALModule):
  """Landmark detection module prints info about landmarks detected"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.memory = ALProxy("ALMemory")
    self.motion = ALProxy("ALMotion")
    self.markProxy = ALProxy("ALLandMarkDetection")
    self.period = 500
 
  def start(self):
    """Starts landmark detector and subscribes to landmark detected event"""
    try:
       self.markProxy.unsubscribe(self.getName())
       self.memory.unsubscribeToEvent("LandmarkDetected", self.getName())
    except:
       pass
    self.markProxy.subscribe(self.getName(),self.period, 0.0)
    #self.memory.subscribeToEvent("LandmarkDetected", self.getName(),"LandMarkFound")
    
    #print "started subscribe to landmark detected"

    #Quiz memory to determine if a landmark was detected.
    #print self.memory.getData("LandmarkDetected")

  def LandMarkFound(self, a, b, c):
      self.memory.unsubscribeToEvent("LandmarkDetected", self.getName())
    # Check whether we got a valid output.
      print "LM START \n"
      print b
      print "LM END \n"
      self.memory.subscribeToEvent("LandmarkDetected", self.getName(),"LandMarkFound")

##      try:
##        #Browse markInfoArray to get info for each detected mark
##        for markInfo in markInfoArray:
##          markShapeInfo = markInfo[0]
##          markExtraInfo = markInfo[1]
##          print "mark  ID: %d" % (markExtraInfo[0])
##          print "  alpha %.3f - beta %.3f" % (markShapeInfo[1], markShapeInfo[2])
##          print "  width %.3f - height %.3f" % (markShapeInfo[3], markShapeInfo[4])
##      except Exception, e:
##        print "Naomarks detected, but it seems getData is invalid. ALValue ="
##        print val
##        print "Error msg %s" % (str(e))   else:
      #print "No landmark detected, shoudlnt really be here"

  def getNaoSpaceLandmark(self):
    # Wait for a mark to be detected.
    landmarkTheoreticalSize = 0.06 #in meters
    currentCamera = "CameraTop"
    markData = self.memory.getData("LandmarkDetected")
    while (len(markData) == 0):
        markData = self.memory.getData("LandmarkDetected")
    print markData
    # Retrieve landmark center position in radians.
    wzCamera = markData[1][0][0][1]
    wyCamera = markData[1][0][0][2]

    # Retrieve landmark angular size in radians.
    angularSize = markData[1][0][0][3]

    # Compute distance to landmark.
    distanceFromCameraToLandmark = landmarkTheoreticalSize / ( 2 * math.tan( angularSize / 2))

    # Get current camera position in NAO space.
    transform = self.motion.getTransform(currentCamera, 2, True)
    transformList = almath.vectorFloat(transform)
    robotToCamera = almath.Transform(transformList)

    # Compute the rotation to point towards the landmark.
    cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)

    # Compute the translation to reach the landmark.
    cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)

    # Combine all transformations to get the landmark position in NAO space.
    robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform *cameraToLandmarkTranslationTransform

    print "x " + str(robotToLandmark.r1_c4) + " (in meters)"
    print "y " + str(robotToLandmark.r2_c4) + " (in meters)"
    print "z " + str(robotToLandmark.r3_c4) + " (in meters)"



  def finish(self):
    """module bla"""
    try:
      self.markProxy.unsubscribe(self.getName())
 #     self.memory.unsubscribeToEvent("LandmarkDetected", self.getName())
    except:
      pass
    self.isRunning = False
    print "Unsubscribed to landmark detected"

  def exit(self):
    try:
      self.markProxy.unsubscribe(self.getName())
 #     self.memory.unsubscribeToEvent("LandmarkDetected", self.getName())
    except:
      pass
    self.isRunning=False
    ALModule.exit(self)
