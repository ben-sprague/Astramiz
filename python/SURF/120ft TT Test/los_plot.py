import xarray as xr
import pandas as pd
import numpy as np

import argparse


import seaborn as sns
import seaborn.objects as so
import seaborn_image as isns
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import os

def draw_los_shading(ds, ax):
    wave_start_id = np.argmin(abs(ds['time'].to_numpy()-ds.attrs['wave_start_time'].astype('timedelta64[ms]')))
    working_df = ds.isel(time = slice(wave_start_id, None))['los'].to_pandas()
    last_change = working_df.iloc[0]
    last_change_x = working_df.index[0]
    labeled = False
    start_time = working_df.index[0]
    for index, value in working_df.items():
        if (working_state := value) != last_change:
            row_num = working_df.index.get_loc(index)
            if last_change == 1:
                #If this is the end of a True section (ie the target was in sight)
                pass
            else:
                #If this is the end of a False section (ie the target was not in sight)
                if labeled:
                    ax.axvspan(xmin = (last_change_x-start_time).total_seconds()*1000, 
                        xmax = (working_df.index[row_num-1]-start_time).total_seconds()*1000, 
                        facecolor = "0.4",
                        alpha = 0.4,
                        edgecolor = None,
                        lw = 0,)
                else:
                    ax.axvspan(xmin = (last_change_x-start_time).total_seconds()*1000, 
                        xmax = (working_df.index[row_num-1]-start_time).total_seconds()*1000, 
                        facecolor = "0.4",
                        alpha = 0.4,
                        lw = 0,
                        edgecolor = None,
                        label = "No Line of Sight")
                    labeled = True
            last_change = working_state
            last_change_x = index    

def generateTicks(raw_labels, interval, axis_length):
    rounding_percision = int(np.ceil(-np.log10(interval)))
    labels = [np.ceil(raw_labels[0]*10**rounding_percision)/10**rounding_percision]
    while labels[-1]+interval < raw_labels[-1]:
        labels.append(np.round(labels[-1]+interval, rounding_percision))

    label_indi = []
    for label in labels:
        label_indi.append(np.argmin(abs(raw_labels-label)))

    label_pos = np.array(label_indi)/raw_labels.size*axis_length
    return label_pos, labels

def makePlot(ds, out_name):
    search_range_id = np.argmin(abs(ds['range'].to_numpy()-ds.attrs['target_distance']))
    fig, (ax2, ax1) = plt.subplots(2,1,figsize = (12,7), gridspec_kw={'width_ratios': [1], 'height_ratios': [1,1]}, sharex=False)
    # fig.tight_layout()
    wave_start_id = np.argmin(abs(ds['time'].to_numpy()-ds.attrs['wave_start_time'].astype('timedelta64[ms]')))

    duration = (ds['time'][-1]-ds['time'][wave_start_id]).astype(np.float64)

    WINDOW_SIZE = 35



    # ds.isel(time = slice(wave_start_id, None), range = search_range_id)['sonar_return'].plot(color = "red")
    # ax2 = plt.twinx()
    # ds.isel(time = slice(wave_start_id, None))['heave'].plot(color = "blue")
    # ds.isel(time = slice(wave_start_id, None))['sea_surface_height'].plot(color = "black")


    pos = plt.imshow(plotted_data := ds.isel(time = slice(wave_start_id, None), 
                        range = slice(search_range_id-WINDOW_SIZE,search_range_id+10))['sonar_return'].T.to_pandas(),
                        cmap='YlGnBu',
                        vmin=0,
                        vmax=255,
                        extent= (0,duration,0,duration/4),
                        #cbar_label="SONAR Return Stregnth [0-255]",
                        #orientation="h",
                        #ax=ax1
                        )


    axins1 = inset_axes(
        ax1,
        width="1%",  
        height="100%", 
        bbox_to_anchor=(1.01, 0., 1, 1),
        bbox_transform=ax1.transAxes,
        loc="lower left",
        borderpad=0,
        )

    fig.colorbar(pos, cax=axins1, label = "SONAR Return Intensity")

    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Range [m]")

    ytick_pos, yticks_label = generateTicks(plotted_data.index.to_numpy(), 0.1, duration.to_numpy()/4)
    ax1.set_yticks(ytick_pos)
    ax1.set_yticklabels(np.flip(yticks_label))

    xtick_pos, xticks_label = generateTicks(plotted_data.columns.total_seconds(), 2, duration.to_numpy())
    ax1.set_xticks(xtick_pos)
    ax1.set_xticklabels(xticks_label)

    draw_los_shading(ds, ax1)

    ds.isel(time = slice(wave_start_id, None))['heave'].plot(color='red', ax=ax2, label = 'SONAR Heave')
    ds.isel(time = slice(wave_start_id, None))['sea_surface_height'].plot(color='blue', ax=ax2, label = 'Sea Surface Elevation at Target')

    ax2.set_xbound(ds.isel(time = slice(wave_start_id, None))['time'][0].astype(np.float64), ds.isel(time = slice(wave_start_id, None))['time'][-1].astype(np.float64))
    ax2.set(xlabel = None, xticks = [], ylabel = 'Elevation [m]')
    ax2.legend(loc = 4)
    ax1.legend(loc = 4)


    ax2.set_aspect('auto')
    ax1.set_aspect('auto')
    
    ax1.set_title("SONAR Return")
    ax2.set_title("SONAR and Target Elevation")

    #plt.tight_layout()

    # plt.show()
    
    plt.savefig(out_name)
    print(f"Saved to {out_name}")

#Setup argument parser
parser = argparse.ArgumentParser()
#Data file paths
parser.add_argument('--outputLocation', required=True, type=str, help='Path to save plots to')
parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with .nc files")

args = parser.parse_args()
input_path = args.input_dir
output_path = args.outputLocation

abs_path = os.path.abspath(__file__)
file_dir = os.path.dirname(abs_path)

sns.set_theme(style='white', palette = 'muted', context="talk")

ds = xr.open_dataset('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/marked data/test19.nc')
ds = ds.isel(time = slice(0, np.argmin(abs(ds['time'].to_numpy()-np.array([40000]).astype('timedelta64[ms]')))))
makePlot(ds, '/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/test19.png')

# if os.path.isdir(input_path := os.path.join(file_dir,args.input_dir)):
#     files = os.listdir(input_path)
#     files.sort()

#     for index, file in enumerate(files):
#         ds = xr.open_dataset(os.path.join(input_path, file))
#         fileName = file.split('.')[0]
#         outFile = os.path.join(file_dir, output_path, f"{fileName}.png")
#         makePlot(ds, outFile)
        