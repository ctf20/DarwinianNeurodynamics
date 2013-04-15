from naoqi import *
import math
import almath
import random
import copy
import pickle
import itertools
import networkx as nx
import matplotlib.pyplot as plt



# create python module
class drawMolClass(ALModule):
  """Create drawClass instance"""
  
  def __init__(self,name):
    ALModule.__init__(self,name)
    self.isRunning=True
    self.G = nx.DiGraph()
    
  def drawMol(self):
 #    plt.figure()
     plt.figure(2)
     plt.clf()
     pos1 = nx.circular_layout(self.G)
 #   nx.draw(self.G, pos1)
 #    print self.G.nodes()
     #Draw sensory nodes in one colour.
     labels = {}
     for n,d in self.G.nodes_iter(data=True):
      #print d
      labels[n] = d['mot']
      
      if d['typeN'] == "sensory":
       nx.draw_networkx_nodes(self.G,pos1, nodelist=[n] ,node_color='c', label = str(d['mot']))
      if d['typeN'] == "motorP":
       nx.draw_networkx_nodes(self.G,pos1, nodelist=[n] ,node_color='r', label = str(d['mot']))
      if d['typeN'] == "motorIzh":
       nx.draw_networkx_nodes(self.G,pos1, nodelist=[n] ,node_color='b', label = str(d['mot']))

      # print "Tim = " + str(d['tim'])
      if d['act'] == True and d['typeN'] == "motorP":
       nx.draw_networkx_nodes(self.G,pos1, node_size=2000, nodelist=[n] ,node_color='r', label = str(d['mot']))
      if d['act'] == True and d['typeN'] == "motorIzh":
       nx.draw_networkx_nodes(self.G,pos1, node_size=2000, nodelist=[n] ,node_color='b', label = str(d['mot']))
             
     nx.draw_networkx_edges(self.G,pos1,alpha = 0.5, width = 6)
     nx.draw_networkx_labels(self.G,pos1,labels,font_size=10,font_family='sans-serif')
     plt.draw()
  
     
  def updateMoleculeInit(self, num, actors):
    act = actors[num]
    #Add num id atom to the graph.
    self.G.clear()
    plt.figure(2)
#    plt.clf()
 #   self.G.add_node(act.id, typeN = act.type, mot = act.motors, sens = act.sensors, tim = act.timer)
 #   self.drawMol()

  def updateMolecule(self, actors):
    plt.figure(2)
 #   plt.clf()
    self.G.clear()
    #Go through finding the active atoms and adding them!
    for k,act in actors.iteritems():
        if act.activeHist is True:
            self.G.add_node(act.id, typeN = act.type, mot = act.motors, sens = act.sensors, act = act.active)
    for k,act in actors.iteritems():
        if act.activeHist is True:
            if act.messages is not None:
                for j,mesg in enumerate(act.messages):
                    self.G.add_edge(act.id, mesg)

    self.drawMol()
    
      


  def exit(self):
    print "Exiting drawClass"
    try:
        pass
    except:
        pass
    self.isRunning=False
    ALModule.exit(self)
