import xarray as xr
import pandas as pd
import numpy as np

import argparse


import seaborn as sns
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import os

def draw_los_shading(ds, ax):
    working_df = ds['los'].to_pandas()
    last_change = working_df.iloc[0]
    last_change_x = working_df.index[0]
    labeled = False
    start_time = working_df.index[0]
    for index, value in working_df.items():
        if (working_state := value) != last_change:
            row_num = working_df.index.get_loc(index)
            if last_change == 0:
                #If this is the end of a False section (ie the target was not in sight)
                pass
            else:
                #If this is the end of a True section (ie the target was in sight)
                if labeled:
                    ax.axvspan(xmin = (last_change_x).total_seconds(), 
                        xmax = (working_df.index[row_num-1]).total_seconds(), 
                        facecolor = "0.4",
                        alpha = 0.2,
                        edgecolor = None,
                        lw = 0,)
                else:
                    ax.axvspan(xmin = (last_change_x).total_seconds(), 
                        xmax = (working_df.index[row_num-1]).total_seconds(), 
                        facecolor = "0.4",
                        alpha = 0.2,
                        lw = 0,
                        edgecolor = None,
                        label = "Line of Sight")
                    labeled = True
            last_change = working_state
            last_change_x = index    

# def generateTicks(raw_labels, interval, axis_length):
#     rounding_percision = int(np.ceil(-np.log10(interval)))
#     labels = [np.ceil(raw_labels[0]*10**rounding_percision)/10**rounding_percision]
#     while labels[-1]+interval < raw_labels[-1]:
#         labels.append(np.round(labels[-1]+interval, rounding_percision))

#     label_indi = []
#     for label in labels:
#         label_indi.append(np.argmin(abs(raw_labels-label)))

#     label_pos = np.array(label_indi)/raw_labels.size*axis_length
#     return label_pos, labels

def makePlot(ds):
    search_range_id = np.argmin(abs(ds['range'].to_numpy()-ds.attrs['target_distance']))
    fig, ax1 = plt.subplots(figsize = (12,7))
    # fig.tight_layout()
    
    start_time = ds['time'].to_numpy()[0].astype(np.float64)
    end_time = ds['time'].to_numpy()[-1].astype(np.float64)

    # ds.isel(time = slice(wave_start_id, None), range = search_range_id)['sonar_return'].plot(color = "red")
    # ax2 = plt.twinx()
    # ds.isel(time = slice(wave_start_id, None))['heave'].plot(color = "blue")
    # ds.isel(time = slice(wave_start_id, None))['sea_surface_height'].plot(color = "black")

    pos = plt.imshow(plotted_data := ds['sonar_return'].T.to_pandas(),
                        cmap='YlGnBu',
                        vmin=0,
                        vmax=255,
                        extent= (start_time/1000,end_time/1000,plotted_data.index[-1],plotted_data.index[0]),
                        aspect='auto',
                        #cbar_label="SONAR Return Stregnth [0-255]",
                        #orientation="h",
                        #ax=ax1
                        )
    
    max_range = plotted_data.index[-1]

    half_wavelength = ds.attrs['wavelength']/2

    first_line = True
    for half_wavelength_number in range(1,int(max_range//half_wavelength)+1):
        if first_line:
            #Add label to line for legend
            ax1.plot((start_time/1000, end_time/1000), (half_wavelength_number*half_wavelength, half_wavelength_number*half_wavelength), 'k--', label = 'Half Wavelengths')
            first_line = False 
        else:
            #Omit label
            ax1.plot((start_time/1000, end_time/1000), (half_wavelength_number*half_wavelength, half_wavelength_number*half_wavelength), 'k--')

    ax1.plot((start_time/1000, end_time/1000), (ds.attrs['target_distance'], ds.attrs['target_distance']), 'r--', label = 'Target Range')

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

    draw_los_shading(ds, ax1)

    ax1.legend(loc = 4)


    ax1.set_aspect('auto')
    
    ax1.set_title("SONAR Return")

    fig.suptitle(f'Target Distance: {ds.attrs['target_distance']}m')

    return fig, ax1
    #plt.tight_layout()

    # plt.show()


if __name__ == "__main__":
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

    sns.set_theme(style='white', palette = 'muted', context="paper")

    # ds = xr.open_dataset('/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/marked data/test17.nc')
    # ds = ds.isel(time = slice(0, np.argmin(abs(ds['time'].to_numpy()-np.array([40000]).astype('timedelta64[ms]')))))
    # makePlot(ds, '/Users/ben/Desktop/astramiz/python/SURF/120ft TT Test/test17.png')

    if os.path.isdir(input_path := os.path.join(file_dir,args.input_dir)):
        files = os.listdir(input_path)
        files.sort()

        for index, file in enumerate(files):
            print(os.path.join(input_path, file))
            if file[0] != '.':
                ds = xr.open_dataset(os.path.join(input_path, file), decode_timedelta=True)
                fileName = file.split('.')[0]
                outFile = os.path.join(file_dir, output_path, f"{fileName}.png")
                makePlot(ds)
                plt.savefig(outFile)
                print(f"Saved to {outFile}")
                plt.close()
            