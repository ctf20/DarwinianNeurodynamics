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
                     
          net = buildNetwork(2,10,1)
          weightsL = len(net.params)
          #print(weightsL)
          x = list([(random.uniform(-1, 1)) for i in range(weightsL)])
          predictOut = random.randint(0,inputL-1)

          return list([senseIn, motorOut, predictOut, x])
          #return list([(random.uniform(-1, 1)) for i in range(736)])

     #Does mutation of all the curiosity loop genomes. 
     def loopVariator(self, random, candidates, args):
          mutants = []
          inputL = args.get('inputLength', 26+18)
          outputL = args.get('outputLength', 26)
          for c in candidates:
               #Mutate the candidate c
               if random.uniform(0,1) < 0.1:
                    c[0] = [random.randint(0,inputL-1), random.randint(0,inputL-1)]
               if random.uniform(0,1) < 0.1:
                    c[1] = random.randint(0,outputL-1)
               if random.uniform(0,1) < 0.1:
                    c[2] = random.randint(0,inputL-1)
               for x in c[3]:
                    x = x + random.gauss(0,0.1)

               #The controller weights should be mutated by Gaussian mutationc
               mutants.append(c)
          return mutants

def main (argv=None):
    print("In main\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
