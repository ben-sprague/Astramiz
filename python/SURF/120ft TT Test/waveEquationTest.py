from wave import solve_wave
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt

from scipy.fft import rfft, fftfreq
from scipy.optimize import fsolve
from line_of_sight import wave_length_difference, sea_surface_height

import pandas as pd

TANK_DEPTH=1.6
TARG_DIST=2.9
g=9.81

data = pd.read_excel('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/waveTestData.xlsx')

N = data.shape[0]

t_test = data.iloc[-1,0] - data.iloc[0,0] #total series time
delta_t = (t_test/(N-1)) #time between samples


yf_ice = rfft(data.iloc[1,:].to_numpy())[1:N//2]
yf_sonar = rfft(data.iloc[2,:].to_numpy())[1:N//2]
xf = fftfreq(N, delta_t)[1:N//2]

#Ice Data FFT
yf_ice = rfft(data.iloc[:,1].to_numpy())[1:N//2]
yf_sonar = rfft(data.iloc[:,2].to_numpy())[1:N//2]
xf = fftfreq(N, delta_t)[1:N//2]

#Use top harmonics to recreate signal
n = int(np.round(0.1*xf.size)) #number of harmonics to use
ice_amps = np.abs(2.0/N*yf_ice)
sonar_amps = np.abs(2.0/N*yf_sonar)
amp_mean = np.mean(np.vstack((ice_amps, sonar_amps)), axis=0)
top_indi = np.argpartition(amp_mean, -(n))[-(n):]
top_yf_ice = yf_ice[top_indi]
top_amp_mean = amp_mean[top_indi]
top_xf = xf[top_indi]

amp = top_amp_mean
phase = np.angle(2.0/N*top_yf_ice)
#Use deep water approximation as intial guess for fsolve
L_deep = g/2/np.pi/top_xf**2
#Numerically solve full airy wave equation to get wave length
wave_length = fsolve(lambda Li: wave_length_difference(Li, 1/top_xf, TANK_DEPTH), L_deep)

k = 2*np.pi/wave_length

phase_speed = np.sqrt(g/k*np.tanh(k*TANK_DEPTH))

waveProps = {
    'amp': amp,
    'phase': phase,
    'omega': 2*np.pi*top_xf,
    'k': k,
    'c': phase_speed
}
#Show plot of where the cut will be made to the user to allow them to confirm
fig, (ax1, ax2, ax3,ax4) = plt.subplots(4,1)
t = np.linspace(0,t_test,10000)
t_plot = (t+data.iloc[0,0].total_seconds())
ax1.plot(data.iloc[:,0], data.iloc[:,1])
ax1.plot(t_plot,sea_surface_height(0,t,waveProps))

ax2.plot(data.iloc[:,0], data.iloc[:,2])
ax2.plot(t_plot,sea_surface_height(TARG_DIST,t,waveProps))

ax3.plot(xval := np.linspace(TARG_DIST,0,5000), sea_surface_height(xval,0,waveProps))

ax4.plot(xf[:40], amp_mean[0:40])
print(max(amp_mean))
ax4.plot(top_xf, top_amp_mean, 'bo')
plt.show()




positions = np.arange(0,12,dx)
times = np.arange(0,5,dt)

bc_i = np.sin(-omega*times)
bc_end = np.sin(k*12-omega*times+0.05)

iv = np.sin(k*positions)
iv_t = -omega*np.cos(k*positions)

fig, ax = plt.subplots()
line, = ax.plot(positions, iv)

def update(i, line):
    line.set_data(positions, solve_wave(iv, iv_t, bc_i, bc_end, 12, i*dt, dx, dt, c))
    return line,

ani = FuncAnimation(fig, update, 600,
                              fargs=[line], blit=True)
ani.save('animation_drawing.mp4', writer='ffmpeg', fps=30)

