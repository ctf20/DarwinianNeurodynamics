from pylab import *

#Read the data from the file for plotting using unpickle. 

X = np.linspace(-np.pi, np.pi, 256,endpoint=True)
C,S = np.cos(X), np.sin(X)
plot(X,C)
plot(X,S)

show()
