from line_of_sight import sea_surface_height
import numpy as np
from matplotlib import pyplot as plt



waveProps = {
    'amp': 1,
    'phase': 0,
    'omega': 2*np.pi*0.5,
    'k': 2*np.pi/6,
}

x_vals = np.linspace(0,12,300)

plt.plot(x_vals, sea_surface_height(x_vals, 0, waveProps))
plt.show()

