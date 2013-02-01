import os
import sys
import time
import numpy as np
from pybrain.tools.shortcuts import buildNetwork
import pickle

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
          #The pickled archieve will be used to construct the higher order actions.
          pickle.dump(self.archieve, open("saveArchieve.p","wb"))
          #favorite_color = pickle.load( open( "saveArchieve.p", "rb" ) )
          #print(favorite_color)
          pass

     def addToArchieveH(self, individ):
          self.archieve.append(individ)
          #Files for saving stuff to.
          projdir = os.path.dirname(os.getcwd())
          arch_file_name = '{0}/archiveH.txt'.format(projdir)
          arch_file = open(arch_file_name, 'w')
          arch_file.write(str(self.archieve))
          arch_file.write("\n")
          arch_file.close()
          #print("Should be writing this indiv to file now" + str(self.archieve))

          #Pickle this archieve also, so that we can re-load it later.
          #The pickled archieve will be used to construct the higher order actions.
          pickle.dump(self.archieve, open("saveArchieveH.p","wb"))
          #favorite_color = pickle.load( open( "saveArchieve.p", "rb" ) )
          #print(favorite_color)
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


     def getSimilarityH(self, x):
          penalty = 0
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

     #Hierarchical Genotype Generation, points to 2 primitive archieved entities.  
     def generateLoopH(self, random, args):
          #The hierarchical loop is defined by referring to
          #1. N archieve individuals.
          #2. Logical interactions between these elements,
          #   e.g. X then Y, or X and Y active simultaneously
          #3. Restrictions.

          #Choose two random primitive archieve elements.
          #Load the archieve 
          primitives = pickle.load( open( "saveArchieveLongRun.p", "rb" ) )
          print("primitive length = " + str(len(primitives)))
          prim1 = random.randint(0,len(primitives)-1)
          prim2 = random.randint(0,len(primitives)-1)
          #Which primitives sensory state should MI be determined on,
          #for fitness calculation.
          pred = random.randint(0,1)
          return list([pred, primitives[prim1], primitives[prim2]])

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

     #Hierarchical loop mutations 
     def loopVariatorH(self, random, candidates, args):
          mutants = []
          inputL = args.get('inputLength', 26+18)
          outputL = args.get('outputLength', 26)
          for c in candidates:
               print(c)
               print(type(c))
               #Mutate each of the units in the first smp unit 
               #Mutate the candidate c
               if random.uniform(0,1) < 0.1:
                    c[1].candidate[0] = [random.randint(0,inputL-1), random.randint(0,inputL-1)]
                    print("Mutating c0\n")
               if random.uniform(0,1) < 0.1:
                    c[1].candidate[1] = random.randint(0,outputL-1)
                    print("Mutating c1\n")
               if random.uniform(0,1) < 0.1:
                    c[1].candidate[2] = random.randint(0,inputL-1)
                    print("Mutating c2\n")
              
               for ix,x in enumerate(c[1].candidate[3]):
                    x = x + random.gauss(0,0.1)
                    c[1].candidate[3][ix] = x
                    #print(random.gauss(0,0.1))
                    #print("Mutating w \n")

   
               if random.uniform(0,1) < 0.1:
                    c[2].candidate[0] = [random.randint(0,inputL-1), random.randint(0,inputL-1)]
                    print("Mutating c0\n")
               if random.uniform(0,1) < 0.1:
                    c[2].candidate[1] = random.randint(0,outputL-1)
                    print("Mutating c1\n")
               if random.uniform(0,1) < 0.1:
                    c[2].candidate[2] = random.randint(0,inputL-1)
                    print("Mutating c2\n")
               for ix,x in enumerate(c[2].candidate[3]):
                    x = x + random.gauss(0,0.1)
                    c[2].candidate[3][ix] = x
       


               mutants.append(c)
          return mutants


def main (argv=None):
    print("In main\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
