from traceTools import *
import numpy as np

z = np.linspace(0,10,1000)
s = np.zeros(z.size)
a = 0.12 #Thermal gradient (deg C/m)
a0 = 60
t = a0-a*z
theta0 = np.array([3, 5, 7])

trace = cdt_trace(s,z,t, theta0, 0,0,0.07)

plot_trace(s,z,t,trace)