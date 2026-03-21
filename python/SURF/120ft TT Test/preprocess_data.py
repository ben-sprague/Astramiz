import argparse
import queue

import pandas as pd
import numpy as np
import xarray as xr
from scipy.interpolate import make_interp_spline
from matplotlib import pyplot as plt
from datetime import datetime

from speedOfSound import speed_of_sound

from numpy.polynomial.polynomial import Polynomial

from line_of_sight import *
from stokes import StokesWave


click_queue = queue.Queue()

def unpackTxt(file):
    '''
    Docstring for unpackTxt

    Unpack txt files with misc data (mostly SONAR and wave generator parameters) logged during data collection
    
    :param file: Path to file
    '''
    #Read the sonar parameters file generated after each trial
    #and use that to start the parameters dictonary

    param_dict = {}
    dict_labels = ['angle', 'period', 'num_samples', 'tx_duration', 'temp', 'commanded_T', 'commanded_H', 'target_distance'] #labels for each parameter value, order is determined by the order they appear in the output txt file
    for i, line in enumerate(file):
        label = dict_labels[i]
        #Rip parameter value (ie. number) out of full string
        parameter_value = float(line[line.rfind(" ") + 1:])
        param_dict[label] = parameter_value
        #Do special things based on each value
        match label:
            case "angle":
                pass #Do nothing 
            case "period":
                #Convert the sample period from the input units (25ns increments) to seconds
                param_dict["period"] = param_dict["period"]*25*10**(-9)
            case "tx_duration":
                #Convert the sample period from the input units (microseconds) to seconds
                param_dict["tx_duration"] = param_dict["tx_duration"]*10**(-6)
            case "temp":
                #Calculate the speed of sound
                param_dict["c sound"] = speed_of_sound(0,param_dict["temp"],0)
            case "T":
                pass #Do nothing 
            case "H":
                pass #Do nothing 
            case "Target Dist":
                pass #Do nothing 

    #Compute things that need multiple values
    param_dict['distance per sample'] = param_dict['c sound']*param_dict['period']/2 #one way distance in meters

    return param_dict

def unpackWaveData(file):
    '''
    Docstring for unpackWaveData

    Unpack excel files from USNA hydrolab with wave data (sea surface elevation and heave)
    
    :param file: Path to file
    '''
    #Read wave data from the lab provided excel file and 
    #change the time so the t=0 datum is when 
    #the SONAR enters the water

    #Unpack wave data from excel file
    wave_data = pd.read_excel(file, usecols='A:E', skiprows=list(range(1,6)), names = ['Time','SonHt', 'SonWav', 'IceHt', 'IceWav'], index_col=0)
    wave_data.index = wave_data.index.astype(float) #convert indexes (times) from strings to floats
    wave_data = wave_data/100 #convert cm to meters

    time = list(wave_data.index)
    #Find the time at which the SONAR enters the water
    SONAR_ENTRANCE_HEIGHT = 0.08 #Sonar was measured to enter the water at a heave of 8cm above the resting height

    sonar_lift_index = (wave_data.iloc[:,0]>SONAR_ENTRANCE_HEIGHT).argmax()
    # plt.plot(wave_data.index, wave_data)
    # plt.show()
    post_sonar_entrance_index = np.nonzero((wave_data.iloc[sonar_lift_index:,0]-SONAR_ENTRANCE_HEIGHT)<0)[0][0]
    sonar_entrance_bracket_rows = wave_data.iloc[sonar_lift_index+post_sonar_entrance_index-1:sonar_lift_index+post_sonar_entrance_index+1,:].sort_values(by=['SonHt']) #The rows of the wave data array that bracket the SONAR entrance
    wave_sync_time = np.interp(SONAR_ENTRANCE_HEIGHT, sonar_entrance_bracket_rows['SonHt'],sonar_entrance_bracket_rows.index)
    #Set the t=0 datum to when the sonar enters the water
    wave_data.index = wave_data.index - wave_sync_time

    #Remove all data before the datum
    wave_data = wave_data.loc[wave_data.index>=0,:]

    return wave_data

def unpackSonarData(file):
    '''
    Docstring for unpackSonarData

    Unpack csv file SONAR data
    
    :param file: Path to file
    '''
    #Read sonar data from the test, put the column headers in
    #terms of distance (instead of sample number) and change the time
    #so that the t=0 datum is when the SONAR enters the water

    #Read SONAR data
    sonar_df = pd.read_csv(file, index_col='time')

    sonar_df.drop(sonar_df.columns[0], axis=1, inplace=True) #Drop column of row indeicies at the left of the dataframe
    sonar_df.index = sonar_df.index.astype(float) #convert indexes (times) from strings to floats
    sonar_df.columns = sonar_df.columns.astype(float) #convert columns (ranges) from strings to floats

    #Put column headers in terms of distance (in meters)
    current_column_names  = sonar_df.columns.to_list() #List of current column names. The first column is 'time' and then the rest at the sample number from 0 to n
    new_column_names = {}
    for name in current_column_names:
        new_column_names[name] = name*param_dict['distance per sample']
    sonar_df.rename(columns=new_column_names, inplace=True)

    #Get rid of garbage data very close to the sensor (assumed to be the first half meter)
    sonar_df = sonar_df.loc[:, sonar_df.columns>0.5]

    #Change time datum
    #Take a slice of the data on either side of the target distance (to allow for sensor error)
    SLICE_SIZE = 0.25 #Size of slice to take on either side of the target distance
    target_dist = param_dict['target_distance']

    #Get the index of the column within the slice with the strongest first return
    slice_start_indi = (sonar_df.columns>target_dist-SLICE_SIZE).argmax()
    max_column_indi = sonar_df.loc[sonar_df.index[0], (sonar_df.columns > target_dist-SLICE_SIZE) & (sonar_df.columns < target_dist+SLICE_SIZE)].argmax()
    max_column = sonar_df.iloc[:,max_column_indi+slice_start_indi]

    
    #Go down this column to determine where the SONAR return drops out (ie when the SONAR was removed from the water)
    DROPOUT_THRESHOLD_PERCENT = 20 #percent of the intial return value that is considered a dropout
    dropout_threshold = DROPOUT_THRESHOLD_PERCENT/100*max_column.iloc[0]
    dropout_start_indi = (max_column<dropout_threshold).idxmax()
    submerged_time = (max_column.loc[dropout_start_indi:]>dropout_threshold).idxmax()
    param_dict["timestamp"] = datetime.fromtimestamp(submerged_time).isoformat()
    
    input_str = ''
    datum_correct = ''

    while not (datum_correct == 'y' or datum_correct == 'Y'):
        #Show plot of where the cut will be made to the user to allow them to confirm
        WINDOW_MAX = 1500
        plt.imshow(sonar_df.iloc[0:WINDOW_MAX,:].to_numpy())
        plt.plot(max_column_indi+slice_start_indi, sonar_df.index.get_loc(submerged_time), 'ro')
        plt.title("Confirm time datum location")
        plt.show(block=False)

        input_str = input("Is the displayed time datum location correct? (Y/n) ")
        datum_correct = input_str if input_str else 'y'
        plt.close()

        if not (datum_correct == 'y' or datum_correct == 'Y'):
            #Manually set datum
            fig, ax = plt.subplots()
            ax.imshow(sonar_df.iloc[0:WINDOW_MAX,:].to_numpy())
            plt.title("Set time datum location")
            fig.canvas.mpl_connect('button_press_event', time_onClick)
            plt.show()
            if not click_queue.empty():
                #If there is data from a click in the queue
                submerged_time = sonar_df.index[round(click_queue.get())]
                click_queue.task_done()
            else:
                #If no data in the queue (likey because the user closed the window)
                print("Data not saved")
                exit()
    
    #Reset the datum
    sonar_df.index = list((float(n)-submerged_time) for n in sonar_df.index)

    #discard data before the datum
    return sonar_df.loc[((float(n)>=0) for n in sonar_df.index), :]

def time_onClick(event):
    click_queue.put(event.ydata)
    plt.close()

def findWaveTrain(wave_df):
    '''
    Docstring for findWaveTrain

    Prompt user to select start/end of wave train from sea surface elevation data
    
    :param wave_df: Dataframe of wave data
    '''
    fig, ax = plt.subplots()
    ax.plot(wave_df.index.total_seconds(), wave_df.loc[:,'SonWav'], 'b-')
    ax.plot(wave_df.index.total_seconds(), wave_df.loc[:, 'IceWav'], 'r--')
    plt.title("Select wave train")
    plt.legend(['SONAR Wave Height','Ice Wave Height'])
    fig.canvas.mpl_connect('button_press_event', wave_onClick)
    plt.show()

    if not click_queue.empty():
        #If there is data from a click in the queue
        wave_start_time = click_queue.get()
        click_queue.task_done()
        return np.timedelta64(int(wave_start_time*1e9), 'ns')
    
    else:
        #If no data in the queue (likey because the user closed the window)
        print("Data not saved")
        exit()

def wave_onClick(event):
    click_queue.put(event.xdata)
    plt.close()

def mergeData(sonar_df, wave_df):
    '''
    Docstring for mergeData

    Recify sampling rate difference between SOANR and wave data by interpolating SONAR data at each 
    point of wave data and return as xarray Dataset
    
    :param sonar_df: Pandas dataframe with SONAR data
    :param wave_df: Pandas dataframe with wave data
    '''
    #Merge the SONAR and wave data into one xarray dataset
    times = wave_df.index.rename("time") #The times from the wave df are used as the base times because they are guarenteed to be evenly spaced
    sonar_times = sonar_df.index
    
    retimed_sonar_df = pd.DataFrame(index=times, columns=sonar_df.columns)
    for range in sonar_df.columns:
        #Make a BSpline from each range in the SONAR data to interpolate with
        range_data = sonar_df.loc[:,range]
        spline = make_interp_spline(sonar_times,range_data,1) #linear interpolation
        #Use spline to interpolate for each time from the wave data
        retimed_sonar_df.loc[:, range] = list(spline(time.total_seconds()) for time in times)
        retimed_sonar_df.loc[retimed_sonar_df.loc[:, range]<0, range] = 0

    retimed_sonar_df = retimed_sonar_df.astype(float)

    return xr.Dataset(
        data_vars = dict(
            SonHt = ("time", wave_df.loc[:,"SonHt"], {
                'units': 'meters',
                'long_name': 'SONAR Heave',
            }),
            SonWav = ("time", wave_df.loc[:,"SonWav"], {
                'units': 'meters',
                'long_name': 'SONAR Sea Surface Elevation',
            }),
            IceHt = ("time", wave_df.loc[:,"IceHt"], {
                'units': 'meters',
                'long_name': 'Ice Heave',
            }),
            IceWav = ("time", wave_df.loc[:,"IceWav"], {
                'units': 'meters',
                'long_name': 'Ice Sea Surface Elevation',
            }),
            sonar_return = (["time", "range"], retimed_sonar_df,{
                'insturment': 'Blue Robotics Ping360',
                'units': 'return strength (0-255)',
                'long_name': 'SONAR Return Intensity',
            }),
        ),
        coords = dict(
            time = (('time',),times,{
                'time_unit': 'ms',
                'long_name': 'Time',
            }),
            range=(('range',),retimed_sonar_df.columns,{
                'units': 'meters',
                'long_name': 'Range',
            })
        ),
    )

if __name__ == '__main__':
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    # parser.add_argument('--sonarData', required=True, type=str, help='Path to CSV file of SONAR returns over time')
    # parser.add_argument('--sonarParams', required=True, type=str, help='Path to txt file of SONAR parameters')
    parser.add_argument('--test_num', required=True, type=int)
    # parser.add_argument('--waveData', required=True, type=str, help='Path to xlsx file of wave data')
    parser.add_argument('--rootDir', required=False, default='.', type=str, help='Path to root directory for all data. Default is the current directory')
    parser.add_argument('--outputLocation', required=True, type=str, help='NetCF file to output to')
    parser.add_argument('--outputToRootDir', action='store_true', default=False, help = 'Use the root dir argument as the base directory for the output file (otherwise the current directory is used). Default false')
    
    #Hand input data
    # parser.add_argument('--sonarDraft', required=True, type=float, help='Draft of the SONAR in meters')
    # parser.add_argument('--targetDraft', required=True, type=float, help='Draft of the target in meters')
    SONAR_DRAFT = 0.1
    TARGET_DRAFT = 0.0984

    args = parser.parse_args()
    #Parse Arguments
    root_dir = f'{args.rootDir}/'
    csv_file_path = f'{root_dir}data{args.test_num}.csv'
    txt_file_path = f'{root_dir}data{args.test_num}.txt'
    wave_file_path = f'{root_dir}data{args.test_num}.xlsx'

    #Unpack TXT file with extra test information
    with open(txt_file_path, 'r') as file:
            param_dict = unpackTxt(file)
    #Add hand input data to the parameters dictonary
    param_dict['sonar_draft'] = SONAR_DRAFT #in meters
    param_dict['target_draft'] = TARGET_DRAFT #meters
    param_dict['notes'] = input("Notes: ")

    #Unpack wave profile data
    wave_df = unpackWaveData(wave_file_path)
    wave_df.index = pd.to_timedelta(wave_df.index, unit='s')

    data_good = ''
    input_str = ''
    while not (data_good == 'y' or data_good == 'Y'):
        #Have user select where wavetrain starts and ends
        wave_start_time = findWaveTrain(wave_df)
        wave_end_time = findWaveTrain(wave_df)
        wave_start_id = np.argmin(abs(wave_df.index.to_numpy().astype('timedelta64[ms]')-wave_start_time.astype('timedelta64[ms]')))
        wave_end_id = np.argmin(abs(wave_df.index.to_numpy().astype('timedelta64[ms]')-wave_end_time.astype('timedelta64[ms]')))

        sliced_wave_df = wave_df.iloc[wave_start_id:wave_end_id, :] #Discard data outside of user selected range
        
        wave = StokesWave(param_dict['commanded_T'], param_dict['commanded_H'], TANK_DEPTH)
        phase = wave.find_phase(sliced_wave_df['IceWav'], 0)
        wave.set_phase(phase)
        wave_length = wave.L

        #Show plot of where the cut will be made to the user to allow them to confirm
        fig, (ax1, ax2, ax3) = plt.subplots(3,1)
        fig.tight_layout()
        ax1.plot(sliced_wave_df.index.total_seconds(), sliced_wave_df['IceWav'], label = "Measured")
        ax1.plot(sliced_wave_df.index.total_seconds(),wave.calculateWave(0,sliced_wave_df.index.total_seconds()).reshape((-1,)), label = "Stokes Wave")
        ax1.set_title("Target (Ice)")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Profile (m)")
        ax1.legend()

        ax2.plot(sliced_wave_df.index.total_seconds(), sliced_wave_df['SonWav'], label = "Measured")
        ax2.plot(sliced_wave_df.index.total_seconds(),wave.calculateWave(param_dict['target_distance'],sliced_wave_df.index.total_seconds()).reshape((-1,)), label = "Stokes Wave")
        ax2.set_title("Target (SONAR)")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Profile (m)")
        ax2.legend()

        ax3.plot(xval := np.linspace(param_dict['target_distance'],0,5000), wave.calculateWave(xval,sliced_wave_df.index.total_seconds()[0]))
        ax3.set_title("Spacial Sea Surface Profile")
        ax3.set_xlabel("Distance from Ice (m)")
        ax3.set_ylabel("Profile (m)")

        plt.show(block=False)

        input_str = input("Is the displayed data acceptable? (Y/n) ")
        data_good = input_str if input_str else 'y'
        plt.close()

    sonar_df = unpackSonarData(csv_file_path)

    ds = mergeData(sonar_df, sliced_wave_df)

    ds = ds.assign_attrs(param_dict)
    sd = ds.assign_attrs({'processing_date': datetime.now().isoformat()})
    ds = ds.assign_attrs({'wave_start_time': wave_start_time})
    ds = ds.assign_attrs({'wave_end_time': wave_end_time})

    #Retime ds from ns to ms
    ds['time'] = ds['time'].astype('timedelta64[ms]')
    ds['time']= ds['time'].assign_attrs({'time_unit': 'ms'})


    ###Prepare to solve if there is a line of sight###

    in_sight = []

    for i, time in enumerate(sliced_wave_df.index):
        z_sonar = sliced_wave_df['SonHt'].iloc[i] - ds.attrs['sonar_draft']
        z_ice = sliced_wave_df['IceHt'].iloc[i] - ds.attrs['target_draft']
        x_sonar = ds.attrs['target_distance']
        time = time.total_seconds()
        los_polynomial = Polynomial([z_ice, (z_sonar-z_ice)/x_sonar])
        # plt.close()
        # plt.plot(x_val:=np.linspace(0,x_sonar,1000), wave.calculateWave(x_val,time,waveProps))
        # plt.plot(x_val, los_polynomial(x_val))
        in_sight.append(does_intersect(time, x_sonar, z_ice, z_sonar, wave))
    #Pack Data
    #Add NaN values for all values before the wave train arrives and after it departs
    ds = ds.assign(dict(los = ('time', in_sight, {
        'units': 'Boolean',
        'long_name': 'Line of Sight',})))
    pass


    if args.outputToRootDir:
        output_path = f"{root_dir+args.outputLocation}{args.test_num}.nc"
    else:
        output_path = f"./{args.outputLocation+args.test_num}.nc"
    #Retime wave start and stop times
    ds = ds.assign_attrs({'wave_start_time': ds.attrs['wave_start_time'].astype('timedelta64[ms]').astype(int)})
    ds = ds.assign_attrs({'wave_end_time': ds.attrs['wave_end_time'].astype('timedelta64[ms]').astype(int)})
    ds.to_netcdf(output_path)
    print(f"Saved to {output_path}")


    
