import numpy as np
import pandas as pd
import argparse

from numpy.polynomial.polynomial import Polynomial
from scipy.optimize import fsolve
from line_of_sight import *
from stokes import StokesWave

from matplotlib import pyplot as plt

def calc_in_sight_percent(T,height,rel_distance):
    #TANK_DEPTH = 4.9 #meters, 380ft TT
    TANK_DEPTH = 1.61 #meters, 120ft TT
    SONAR_DRAFT = 0.08 #meters
    TARGET_DRAFT = 0.1 #meters
    g = 9.81 #m/s^s

    D_T = 0.01 #time step to use when constructing waveform

    wave = StokesWave(T, height, TANK_DEPTH)


    distance = wave.L*rel_distance
    wave_length = wave.L
    time = np.arange(0,T, D_T)
    target_heave = wave.calculateWave(0,time)-TARGET_DRAFT
    sonar_heave = wave.calculateWave(distance,time)-SONAR_DRAFT

    in_sight = []

    for i, t in enumerate(time):
        z_sonar = sonar_heave[i]
        z_ice = target_heave[i]
        x_sonar = distance
        los_polynomial = Polynomial([z_ice, (z_sonar-z_ice)/x_sonar])
        in_sight.append(does_intersect(t, x_sonar, z_ice, z_sonar, wave))

    in_sight = np.array(in_sight)

    num_in_sight = np.count_nonzero(in_sight)
    total_samples = np.size(in_sight)

    steepness = height/wave_length

    return (100*(1-(num_in_sight/total_samples)), wave_length, distance, steepness)
    # print(f"Out of sight {100*(1-(num_in_sight/total_samples))}% of wave cycle")
    # print(f"Wave length {wave_length}m")
    # print(f"Distance {distance}m")

    # fig1, ax1 = plt.subplots()
    # ax1.plot(time,target_heave)
    # ax1.plot(time,sonar_heave)
    # ax1.plot(time,in_sight)

    # QUERY_TIME = 0.1
    # fig2, ax2 = plt.subplots()
    # z_ice = sea_surface_height(0,QUERY_TIME,waveProps)[0]-TARGET_DRAFT
    # z_sonar = sea_surface_height(distance,QUERY_TIME,waveProps)[0]-SONAR_DRAFT
    # ax2.plot(d_x:=np.arange(0,distance,0.01), sea_surface_height(d_x,QUERY_TIME,waveProps))
    # los_polynomial = Polynomial([z_ice, (z_sonar-z_ice)/x_sonar])
    # ax2.plot(d_x, los_polynomial(d_x))
    # print(does_intersect(QUERY_TIME, x_sonar, z_ice, z_sonar, waveProps))

    # plt.show()

if __name__ == '__main__':
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    parser.add_argument('--input', required=True, type=str, help='Input File')

    args = parser.parse_args()
    #Parse Arguments
    input_file_name = args.input
    raw_df = pd.read_csv(input_file_name, skip_blank_lines=True)
    T_df = raw_df['T']
    H_df = raw_df['H']
    x_df = raw_df['Rel X']
    percent = np.full((raw_df.shape[0],),np.nan)
    length = np.full((raw_df.shape[0],),np.nan)
    abs_distance = np.full((raw_df.shape[0],),np.nan)
    steepness = np.full((raw_df.shape[0],),np.nan)


    for i in range(len(percent)):
        T = T_df.iloc[i]
        H = H_df.iloc[i]
        x = x_df.iloc[i]
        (percent[i], length[i], abs_distance[i], steepness[i]) = calc_in_sight_percent(T,H,x)
    
    out_df = pd.concat([raw_df, pd.DataFrame([percent, length, abs_distance, steepness], index=['Out of Sight Percent', 'Wave Length', 'Abs Distance', 'Steepness']).T], axis=1)
    print(out_df)
    out_df.to_csv('output.csv', index=None)











