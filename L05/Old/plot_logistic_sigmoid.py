#%%
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

w1 = 2 # e.g. 0, 2, 
w2 = 3 # e.g. 0, 3,

x = np.arange(-15,15,0.1)
y = np.arange(-15,15,0.1)
X,Y = np.meshgrid(x,y)
Z = 1/(1 + np.exp(-(w1*X + w2*Y)))

# Plot a basic wireframe.
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0)
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

