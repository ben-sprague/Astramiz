import argparse
import queue
import os

from full_sonar_plot import makePlot

import pandas as pd
import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import seaborn as sns

click_queue = queue.Queue()

def click_callback(event):
    click_queue.put(event.ydata)
    plt.close()


if __name__ == "__main__":
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    parser.add_argument('--outputLocation', required=True, type=str, help='Path to save data to')
    parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with .nc files")

    args = parser.parse_args()
    input_path = args.input_dir
    output_path = args.outputLocation

    abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(abs_path)

    sns.set_theme(style='white', palette = 'muted', context="paper")

    # ds = xr.open_dataset('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/marked data/test17.nc')
    # ds = ds.isel(time = slice(0, np.argmin(abs(ds['time'].to_numpy()-np.array([40000]).astype('timedelta64[ms]')))))
    # makePlot(ds, '/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/test17.png')

    df = pd.DataFrame(columns=['file_num','int_return', 'perst_return', 'difference'])
    if os.path.isdir(input_path := os.path.join(file_dir,args.input_dir)):
        files = os.listdir(input_path)
        files.sort()

        for index, file in enumerate(files):
            print(os.path.join(input_path, file))
            if file[0] != '.':
                ds = xr.open_dataset(os.path.join(input_path, file), decode_timedelta=True)
                fileName = file.split('.')[0]
                outFile = os.path.join(file_dir, output_path, f"{fileName}.png")

                workingRow = np.full((4,),np.nan)
                workingRow[0] = fileName.split('test')[1]
                dataRecived = False
                while not(dataRecived):
                    fig, ax = makePlot(ds)
                    fig.canvas.mpl_connect('button_press_event', click_callback)
                    fig.suptitle('Select Intermittent Return')
                    plt.show()

                    if not click_queue.empty():
                        #If there is data from a click in the queue
                        workingRow[1] = click_queue.get()
                        click_queue.task_done()
                        dataRecived = True
                    
                    else:
                        #If no data in the queue (likey because the user closed the window)
                        print("Data not saved")
                
                dataRecived = False
                while not(dataRecived):
                    fig, ax = makePlot(ds)
                    fig.canvas.mpl_connect('button_press_event', click_callback)
                    fig.suptitle('Select Persistent Return')
                    plt.show()

                    if not click_queue.empty():
                        #If there is data from a click in the queue
                        workingRow[2] = click_queue.get()
                        click_queue.task_done()
                        dataRecived = True
                    
                    else:
                        #If no data in the queue (likey because the user closed the window)
                        print("Data not saved")
                        plt.close()
                
                workingRow[3] = workingRow[2] - workingRow[1]

                df = pd.concat([df, pd.DataFrame([workingRow], columns=df.columns)], ignore_index=True)
                df.to_csv(f'{args.outputLocation}returnDistances.csv')