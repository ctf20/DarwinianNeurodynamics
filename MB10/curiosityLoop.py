import sys
import time
import numpy as np
from pybrain.tools.shortcuts import buildNetwork

class curiosityLoop(object):
     def __init__(self):
         pass
     
     #Inspyred methods for evolutionary computation
     def generateLoop(self, random, args):
          #2 integers showing where inputs are from
          #1 integer showing which motor is controlled.
          #The weights of the network
          #1 integer showing which sensor is to be predicted.
          inputL = args.get('inputLength', 26+18)
          outputL = args.get('outputLength', 26)
          
          senseIn = [random.randint(0,inputL-1), random.randint(0,inputL-1)]
          motorOut = random.randint(0,outputL-1)
                     
          net = buildNetwork(inputL,10,outputL-1)
          weightsL = len(net.params)
          x = list([(random.uniform(-1, 1)) for i in range(weightsL)])
          predictOut = random.randint(0,inputL-1)

          return list([senseIn, motorOut, predictOut, x])
          #return list([(random.uniform(-1, 1)) for i in range(736)])

     #Does mutation of all the curiosity loop genomes. 
     def loopVariator(self, random, candidates, args):
          mutants = []
          for c in candidates:
               mutants.append(c)
          return mutants

def main (argv=None):
    print("In main\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
