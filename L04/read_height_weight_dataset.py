# read men/women height weight data..
# OBS: Enhed er hhv. pound og inch

import matplotlib.pyplot as plt
import numpy as np

# Load data
data = np.loadtxt('height_weight.csv', delimiter=';', skiprows=1)
X = data[:,1:3]
y = data[:,0]

pound2kg = 0.453592 
inch2cm = 2.54
Xw = pound2kg*X[:,1]
Xh = inch2cm*X[:,0]

print('weight :', np.mean(Xw), 'height:', np.mean(Xh))


#%% input data - scatter plot

idx_men = y == 0
plt.scatter(Xw[idx_men], Xh[idx_men], s=0.1, c='b')
idx_women = y == 1
plt.scatter(Xw[idx_women], Xh[idx_women], s=0.1, c='r')


#%% input-output relation

# køn som funk af w/h
plt.plot(Xw, y, 'r.', markersize=1)
plt.plot(Xh, y, 'r.', markersize=1)

#%% distribution - e.g. weight

plt.hist([Xw[idx_men], Xw[idx_women]], bins=50)





    
