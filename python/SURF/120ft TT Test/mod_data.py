import xarray as xr
import pandas as pd
import numpy as np

import argparse
import os

from stokes import StokesWave

if __name__ == "__main__":
    #Setup argument parser
    parser = argparse.ArgumentParser()
    #Data file paths
    parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with .nc files")

    args = parser.parse_args()
    input_path = args.input_dir

    abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(abs_path)

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
                TANK_DEPTH = 1.61
                wave = StokesWave(ds.attrs['commanded_T'], ds.attrs['commanded_H'], TANK_DEPTH)
                ds = ds.assign_attrs({'wavelength': wave.L})
                ds = ds.assign_attrs({'tank_depth': TANK_DEPTH})
                ds.to_netcdf(os.path.join(f'{input_path}/../newData',file))