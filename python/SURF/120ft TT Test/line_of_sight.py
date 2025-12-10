import xarray as xr
import numpy as np
from numpy.polynomial.polynomial import Polynomial
from scipy.fft import rfft, fftfreq
from scipy.optimize import fsolve, minimize_scalar

import matplotlib.pyplot as plt

import argparse

TANK_DEPTH = 4.9 #meters
g = 9.81 #m/s^s


def wave_length_difference(Li, T):
    #Solve for the difference between Li and the Li in the airy wave equation
    return Li - (g*T**2/2/np.pi)*np.tanh(2*np.pi*TANK_DEPTH/Li)

def sea_surface_height(x, t, waveProps):
    if type(x) is not np.ndarray and type(t) is np.ndarray:
        x = np.full_like(t, x)
    elif type(x) is np.ndarray and type(t) is not np.ndarray:
        t = np.full_like(x, t)
    elif type(x) is not np.ndarray and type(t) is not np.ndarray:
        x = np.array([x])
        t = np.array([t])
        
    num_el = len(x)

    heights = []

    for i in range (0,num_el):
        heights.append(np.sum(waveProps['amp']*np.cos(waveProps['k']*x[i]+waveProps['omega']*t[i]+waveProps['phase'])))
    
    return np.array(heights)

def calc_height_difference(x, t, polynomial, waveProps):
    return sea_surface_height(x, t, waveProps) - polynomial(x)

def does_intersect(t, x_sonar, z_ice, z_sonar, waveProps):
    los_polynomial = Polynomial([z_ice, (z_sonar-z_ice)/x_sonar])
    mini_result = minimize_scalar(lambda x: calc_height_difference(x, t, los_polynomial, waveProps), bounds = (0, x_sonar))
    if mini_result.fun < 0:
        return False
    else:
        return True
    
def draw_los_shading(df, ax):
    last_change = df['los'].iloc[0]
    last_change_x = df.index[0]
    for index, row in df.iterrows():
        if (working_state := row['los']) != last_change:
            if last_change:
                #If this is the end of a True section (ie the target was in sight)
                pass
            else:
                #If this is the end of a False section (ie the target was not in sight)
                row_num = df.index.get_loc(index)
                ax.axvspan(last_change_x.total_seconds()*1000, df.index[row_num-1].total_seconds()*1000, facecolor='0.1', alpha = 0.3)
            last_change = working_state
            last_change_x = index


#ds = xr.open_dataset("/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/marked data/test21.nc")
if __name__ == '__main__':
    import argparse

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



    #Perform fft on wave data
    wave_start_id = np.argmin(abs(ds['time'].to_numpy()-ds.attrs['wave_start_time'].astype('timedelta64[ms]')))

    wave_df = ds.isel(time = slice(wave_start_id, None))[['sea_surface_height', 'heave']].to_pandas()
    N = wave_df.shape[0]
    t_test = wave_df.index[-1] - wave_df.index[0] #total series time
    delta_t = (t_test/(N-1)).total_seconds() #time between samples
    yf = rfft(wave_df['sea_surface_height'].to_numpy())[1:N//2]
    xf = fftfreq(N, delta_t)[1:N//2]

    #Use top 10 harmonics to recreate signal
    n = 6
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

    ax3.plot(xval := np.linspace(ds.attrs['target_distance'],0,10000), sea_surface_height(xval,0,waveProps))

    ax4.plot(xf[:100], 2.0/N * np.abs(yf[0:100]))
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
        plt.close()
        plt.plot(xval, sea_surface_height(xval,time, waveProps))
        plt.plot(xval, los_polynomial(xval))
        plt.show()

    wave_df.loc[:, 'los'] = in_sight

    #Pack Data
    #Add NaN values for all values before the wave train arrives
    padded_in_sight = np.concatenate((np.full(ds['time'].size - wave_df.index.size, np.NaN), np.array(in_sight)))
    ds = ds.assign(dict(los = ('time', padded_in_sight, {
        'units': 'Boolean',
        'long_name': 'Line of Sight',})))
    pass

    # ds.to_netcdf(outPath)
    # print(f"Saved to {outPath}")







    # f_dom_indi = np.argmax(np.abs(yf[0:N//2]))
    # f_dom = xf[f_dom_indi]
    # coeff_dom = 2.0/N*yf[f_dom_indi]
    # amp_dom = abs(coeff_dom)
    # phase_dom = np.angle(coeff_dom)


    # plt.show()


