from preprocess_data import findWaveTrain
import xarray as xr
import argparse

from numpy.polynomial.polynomial import Polynomial
from scipy.fft import rfft, fftfreq
from scipy.optimize import fsolve, minimize_scalar

from line_of_sight import *

TANK_DEPTH = 4.9 #meters
g = 9.81 #m/s^s

#Setup argument parser
parser = argparse.ArgumentParser()
#Data file paths
parser.add_argument('--inputLocation', required=True, type=str, help='Path to CSV file of SONAR returns over time')
parser.add_argument('--outputLocation', required=True, type=str, help='Path to CSV file of SONAR returns over time')

args = parser.parse_args()
#Parse Arguments
inPath = args.inputLocation
outPath = args.outputLocation

ds = xr.open_dataset(inPath)
#Retime ds from ns to ms
ds['time'] = ds['time'].astype('timedelta64[ms]')
ds['time']= ds['time'].assign_attrs({'time_unit': 'ms'})
df = ds[['heave', 'sea_surface_height']].to_pandas()
df = df.rename(columns={'heave': 'Heave', 'sea_surface_height':'Sea Surface Height'})
train_time = findWaveTrain(df)
ds = ds.assign_attrs({'wave_start_time': train_time})

#Calculate when there is line of sight

#Perform fft on wave data
wave_start_id = np.argmin(abs(ds['time'].to_numpy()-ds.attrs['wave_start_time'].astype('timedelta64[ms]')))

wave_df = ds.isel(time = slice(wave_start_id, None))[['sea_surface_height', 'heave']].to_pandas()
N = wave_df.shape[0]
t_test = wave_df.index[-1] - wave_df.index[0] #total series time
delta_t = (t_test/(N-1)).total_seconds() #time between samples
yf = rfft(wave_df['sea_surface_height'].to_numpy())[1:N//2]
xf = fftfreq(N, delta_t)[1:N//2]

#Use top 10 harmonics to recreate signal
n = 11
top_indi = np.argpartition(abs(yf), -n)[-n:]
top_yf = yf[top_indi]
top_xf = xf[top_indi]

amp = np.abs(2.0/N*top_yf)
phase = np.angle(2.0/N*top_yf)
#Use deep water approximation as intial guess for fsolve
L_deep = g/2/np.pi/top_xf**2
#Numerically solve full airy wave equation to get wave length
wave_length = fsolve(lambda Li: wave_length_difference(Li, 1/top_xf), L_deep)

waveProps = {
    'amp': amp,
    'phase': phase,
    'omega': 2*np.pi*top_xf,
    'k': 2*np.pi/wave_length
}



fig, (ax1, ax2, ax3,ax4) = plt.subplots(4,1)
t = np.linspace(0,t_test.total_seconds(),10000)
t_plot = (t+wave_df.index[0].total_seconds())*1000
ax1.plot(wave_df['sea_surface_height'])
ax1.plot(t_plot,sea_surface_height(0,t,waveProps))

ax2.plot(wave_df['heave'])
ax2.plot(t_plot,sea_surface_height(ds.attrs['target_distance'],t,waveProps))

ax3.plot(xval := np.linspace(ds.attrs['target_distance'],0,10000), sea_surface_height(0,xval,waveProps))

ax4.plot(xf[:40], 2.0/N * np.abs(yf[0:40]))
print(max(top_xf))
ax4.plot(top_xf, 2.0/N*np.abs(top_yf), 'bo')

plt.show()



in_sight = []

for i, time in enumerate(wave_df.index):
    z_sonar = wave_df['heave'].iloc[i] - ds.attrs['sonar_draft']
    z_ice = wave_df['sea_surface_height'].iloc[i] - ds.attrs['target_draft']
    x_sonar = ds.attrs['target_distance']
    time = time.total_seconds() - wave_df.index[0].total_seconds()
    los_polynomial = Polynomial([z_ice, (z_sonar-z_ice)/x_sonar])
    in_sight.append(does_intersect(time, x_sonar, z_ice, z_sonar, waveProps))

wave_df.loc[:, 'los'] = in_sight

#Pack Data
#Add NaN values for all values before the wave train arrives
padded_in_sight = np.concatenate((np.full(ds['time'].size - wave_df.index.size, np.NaN), np.array(in_sight)))
ds = ds.assign(dict(los = ('time', padded_in_sight, {
    'units': 'Boolean',
    'long_name': 'Line of Sight',})))
pass

ds.to_netcdf(outPath)
print(f"Saved to {outPath}")