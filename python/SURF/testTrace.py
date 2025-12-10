
from traceTools import *
import json

import numpy as np

import seaborn as sns
import seaborn.objects as so

sns.set_theme(style='whitegrid', palette = 'muted', context='poster')
#sns.set_context("poster")

file_path = "/Users/ben/Desktop/astramiz/python/SURF/9_14_2016_42089.json"

with open(file_path, 'r') as file:
    data = json.load(file)
    s = np.array(data['s'])
    z = np.array(data['z'])
    t = np.array(data['t'])

c_coarse = speed_of_sound(s, t, z)

num_div = 3

theta0 = np.array([5,8,12])

trace, z_fine, c_fine = ctd_trace_interp(s,t,z,theta0,0,0.1,15, num_div)

fig, ax1, ax2 = plot_trace(s,t,z,trace)
#sns.lineplot(x=c_fine, y=z_fine, ax=ax1, orient='y', linestyle='dotted', label = 'Interpolated')
#ax1.legend(loc = 'lower center')
sns.lineplot(x = [0, 23000],y = np.full((2,),np.max(z)), ax=ax2, linestyle = 'dashed', label = 'Seafloor')
ax2
plt.show()





