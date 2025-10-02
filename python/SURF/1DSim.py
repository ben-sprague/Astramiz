from SeaSurface import SeaSurface
from LineOfSight import LineOfSight
import numpy as np
from matplotlib import pyplot as plt

sea = SeaSurface([0.1, 0.3, 0.2,0, 0.5], 0, 0.01,[0, 0.1, 0.3, 5, 3])
los = LineOfSight(sea, 0, 5, 0)
mini_result = los.solve_intersection()
x = np.linspace(0,10,1000)
z = sea.height(x,np.zeros((1,1000)))
plt.plot(x,z)
plt.plot(x,sea.particle_velocity(x,np.zeros((1,1000)),-1)[0])
# if mini_result is not None:
#     plt.plot(mini_result, sea.height(mini_result,0), 'o')
plt.show()