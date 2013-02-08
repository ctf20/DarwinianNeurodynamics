import os
import sys


class Actor(object):
    def __init__(self):
        self.archieve = []
        print("Making actor\n")
        self.type = 0 #Controller type 
        #0 = DEFAULT = FFNN
        #1 = CTRNN
        #2 = CMA-ES with fitness = Euclidean distance from target.
        #3 = Above exploration phase + LWPR Learns an inverse model allowing movement to targets more efficiently.
        #4 = Other actor type submitted by user
        
        self.num_sens_inputs = 3 #Default no inputs
        self.num_mot_outputs = 3 #Default no outputs
        self.num_target_inputs = 3; #Default no sensory targets.
        

        pass


def main (argv=None):
    print("In actor\n")
    pass

if __name__ == "__main__":
    sys.exit(main())
