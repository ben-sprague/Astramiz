from stokes import StokesWave
from line_of_sight import does_intersect
import numpy as np
import matplotlib.pyplot as plt

TANK_DEPTH = 1.61
SONAR_DRAFT = 0.08 #meters
TARGET_DRAFT = 0.1 #meters

T = 2 #seconds
wave_height = 0.2 #meters

wave = StokesWave(T, wave_height, TANK_DEPTH)

wave_length = wave.L
rel_dist = 0.75

t = np.arange(0, 3*T, 0.01)
los = np.full_like(t, np.nan)

target_heave = wave.calculateWave(0,t)
sonar_heave = wave.calculateWave(rel_dist*wave_length,t)

for i in range (los.size):
    los[i] = not(does_intersect(t[i], rel_dist*wave_length, target_heave[i]-TARGET_DRAFT, sonar_heave[i]-SONAR_DRAFT, wave))

plt.plot(t, target_heave, label = 'Target Heave')
plt.plot(t, sonar_heave, label = 'SONAR Heave')
plt.plot(t, los, label = 'LOS')
plt.show()
