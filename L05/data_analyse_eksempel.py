# read men/women height weight data..

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Load data - vægt data (kvinder/mænd)
data = np.loadtxt('height_weight.csv', delimiter=';', skiprows=1)
X = data[:,1:3]
y = data[:,0]


#%% plot 2D - "korrelationsplot"

Xmen = X[:5000,:]
plt.scatter(Xmen[:,0], Xmen[:,1], s=1)
plt.xlabel('vægt')
plt.ylabel('højde')


#%% basal statistik

x1 = Xmen[:,0] # vægt
x2 = Xmen[:,1] # højde

m1 = np.mean(x1)
s1 = np.std(x1)
v1 = np.var(x1)

xarr = np.linspace(np.min(x1), np.max(x1), 500)
fig, ax = plt.subplots(2,1, figsize=(10,20)) 
ax[0].hist(x1, bins=100) # histogram
ax[1].plot(xarr, norm.pdf(xarr, m1, s1)) # prob. dens. func.

#%% korrelation

corrcoef = np.corrcoef(Xmen.T) # obs: rækker=variable, kolonner=samples (modsat normalt..)



    
