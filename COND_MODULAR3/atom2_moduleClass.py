from naoqi import *

# create python module
class atom2_moduleClass(ALModule):
  """Speech events processing module"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.speech=ALProxy("ALSpeechRecognition")
    self.speech.setLanguage('English')
    self.speech.setWordListAsVocabulary(['start','finish','nao'])
    self.memory=ALProxy("ALMemory")
 
  def callbackWordRecognized(self,var,val,msg):
    """callback when a word is recognized"""
    print "callbackWordRecognized var=",var," val=",val," msg=",msg
    # Find word with maximum confidence
    max=0.0
    maxword=''
    for i in range(0,len(val),2):
      if val[i+1]>max:
        max=val[i+1]
        maxword=val[i]
    # Confidence threshold
    if max<0.05: return

    # Find confidence ratio of 2nd best word w.r.t. max word
    maxratio=0.0
    for i in range(0,len(val),2):
      if val[i]==maxword: continue
      ratio=val[i+1]/max
      print ratio
      if ratio>maxratio: maxratio=ratio    
    # Confidence ratio threshold (ambiguous recognition)
    if maxratio>0.5: return
      
    # Create ALMemory event 'word_'+recognizedword
    print 'Word found:', maxword
    self.memory.raiseMicroEvent("word_"+maxword,"")
    

  def start(self):
    """Starts the word detection module, """
    try:
       self.memory.unsubscribeToEvent("WordRecognized",self.getName())
    except:
       pass
    self.memory.subscribeToEvent("WordRecognized",self.getName(),"callbackWordRecognized")
      

  def finish(self):
    """module bla"""
    try:
      self.memory.unsubscribeToEvent("WordRecognized",self.getName())
    except:
      pass
    self.isRunning = False

 
  def exit(self):
    try:
      self.memory.unsubscribeToEvent("WordRecognized",self.getName())
    except:
      pass
    self.isRunning=False
    ALModule.exit(self)
