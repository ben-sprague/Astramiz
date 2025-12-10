import xarray as xr
import pandas as pd
import numpy as np


import seaborn as sns
import seaborn.objects as so
from matplotlib import pyplot as plt

#Read Data File
ds = xr.open_dataset("./python/SURF/120ft TT Test/marked data/test21.nc")

sns.set_theme()
sns.set_context("poster")

wave_start_id = np.argmin(abs(ds['time'].to_numpy()-ds.attrs['wave_start_time'].astype('timedelta64[ms]')))

ax = ds['heave'].isel(time = slice(1000, None)).plot()
ds['sea_surface_height'].isel(time = slice(1000, None)).plot()
ax2 = plt.twinx()
search_range_id = np.argmin(abs(ds['range'].to_numpy()-ds.attrs['target_distance']))
ds.isel(time = slice(1000, None), range = search_range_id)['sonar_return'].plot(color='red')
plt.show()


