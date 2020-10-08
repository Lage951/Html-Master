#%%

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.neural_network import MLPRegressor
import numpy as np


#%% data

x = np.linspace(-10,10,1000)
y = 2*np.tanh(2*x - 12) - 3*np.tanh(2*x - 4)

plt.plot(x,y, '.')

x = x.reshape(-1,1) # Scikit-algoritmer kræver (:,1)-format


#%% fit model

mlp = MLPRegressor(activation = 'tanh', # aktiveringsfunktion 
                   hidden_layer_sizes = 2, # antal skjulte neuroner
                   alpha = 1e-5, # regulariseringsparameter, her meget lille
                   solver = 'lbfgs', # quasi-Newton solver
                   max_iter=1000,
                   verbose = True)
mlp.fit(x,y)

plt.plot(x,y)
plt.plot(x, mlp.predict(x), 'rx', ms=1)

mlp.coefs_ # w-parametre
mlp.intercepts_ # = bias led

#%% data 2 - Til øvelserne..

x = np.linspace(-3,3,1000)
y = np.sinc(x)

plt.plot(x,y, '.')

x = x.reshape(-1,1) # Scikit-algoritmer kræver (:,1)-format