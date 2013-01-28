import os
import sys
import time
import numpy as np
from pybrain.tools.shortcuts import buildNetwork

lib_path = os.path.abspath('../')
sys.path.append(lib_path)

class curiosityLoop(object):
     def __init__(self):
         self.archieve = []
         
         pass
     
     def addToArchieve(self, individ):
          self.archieve.append(individ)
          #Files for saving stuff to.
          projdir = os.path.dirname(os.getcwd())
          arch_file_name = '{0}/archive.txt'.format(projdir)
          arch_file = open(arch_file_name, 'w')
          arch_file.write(str(self.archieve))
          arch_file.write("\n")
          arch_file.close()
          #print("Should be writing this indiv to file now" + str(self.archieve))

          #Pickle this archieve also, so that we can re-load it later.
          
          pass

     def getSimilarity(self, x):
          penalty = 0
          for a in self.archieve:
               #print(type(a.candidate))
               a2 = a.candidate
               #Add a linear penilty of 1 if the sensory stream predicted is the same as one that already exists.
               if a2[2] is x[2]:
                    penalty = penalty + 1
               #Add another penalty (less than 1) if the motor dimension is the same as another one
               if a2[1] is x[1]:
                    penalty = penalty + 0.1
          return penalty           


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
          hs = args.get('HIDDENSIZE', 2)
          net = buildNetwork(2,hs,1)
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
               #print(c)
               #Mutate the candidate c
               if random.uniform(0,1) < 0.1:
                    c[0] = [random.randint(0,inputL-1), random.randint(0,inputL-1)]
                    print("Mutating c0\n")
               if random.uniform(0,1) < 0.1:
                    c[1] = random.randint(0,outputL-1)
                    print("Mutating c1\n")
               if random.uniform(0,1) < 0.1:
                    c[2] = random.randint(0,inputL-1)
                    print("Mutating c2\n")
               for ix,x in enumerate(c[3]):
                    x = x + random.gauss(0,0.1)
                    c[3][ix] = x
                    #print(random.gauss(0,0.1))
                    #print("Mutating w \n")

               #print("Mutant:=", c)
               mutants.append(c)
          return mutants

def main (argv=None):
    print("In main\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
