###
# Roughly model sound propagation in the 120ft Tow Tank in the US Naval Academy Hydrolab
# The tow tank is 120ft long, 8ft wide, and 5ft deep
#The bottom and sides of the tank and generally smooth and flat with some small features (generally pockets)
#The tank is fresh water

from traceTools import *
from speedOfSound import speed_of_sound
import numpy as np
from matplotlib import pyplot as plt

#Experiment conditions
temp_f = 68 #Temperature of the water in Fahrenheit, the temperature is assumed constant throughout the tank
temp_c = (temp_f-32)/1.8 #Temperature of the water in Celcius

h_tank_ft = 5.2 #Water depth in feet
h_tank_m = h_tank_ft/3.281 #Water depth in meters

#Set up temperature, pressure, salinity, and speed of sound gradients
n_points = 100
temp_gradient = np.full(n_points, temp_c) #Constant temperature
depth_gradient = np.linspace(0,h_tank_m, n_points)
salnity_gradient = np.zeros(n_points) #Fresh water tank
c = speed_of_sound(salnity_gradient, depth_gradient, temp_gradient)

trace = ctd_trace(salnity_gradient, temp_gradient, depth_gradient, 50, 0, 0.01, 0.05)
xf = trace['x']
zf = trace['z']
fig, ax = plt.subplots()
ax.plot(xf[0], zf[0])
ax.grid(True)
ax.invert_yaxis()
plt.show()



