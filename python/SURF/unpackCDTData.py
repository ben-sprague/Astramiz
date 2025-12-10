#Import module to read NOAA WOD CDT Data
#https://github.com/IQuOD/wodpy
from wodpy import wod

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

import json

def writeCDTJson(profile, path):
    data_dict = {"latitude": profile.latitude(), "longitude":profile.longitude()}
    data_dict["p"] = profile.p().tolist()
    data_dict["s"] = profile.s().tolist()
    data_dict["t"] = profile.t().tolist()
    data_dict["z"] = profile.z().tolist()
    profile_datetime = profile.datetime()
    data_dict['year'] = profile_datetime.year
    data_dict['month'] = profile_datetime.month
    data_dict['day'] = profile_datetime.day
    with open(f"{path}/{data_dict['month']}_{data_dict['day']}_{data_dict['year']}_{profile.cruise()}.json", 'w') as file:
        file.write(json.dumps(data_dict, indent=4))


profiles = []
i = 0
# load all profiles
with open('/Users/ben/Desktop/astramiz/python/SURF/cdt_data/ocldb1760714262.834944.CTD','r') as fid:
    profile = wod.WodProfile(fid)
    while not profile.is_last_profile_in_file(fid):
    #for i in range (10):
        if (month:=profile.datetime().year) >= 2016:
            profiles.append(profile)
            writeCDTJson(profile, ".")
        profile = wod.WodProfile(fid)

lat = []
long = []
for profile in profiles:
    lat.append(profile.latitude())
    long.append(profile.longitude())

map = Basemap(projection='nplaea',boundinglat=60,lat_0 = 75,lon_0=180,resolution='l')

map.fillcontinents(color='coral',lake_color='aqua')
# draw the edge of the map projection region (the projection limb)
map.drawmapboundary(fill_color='aqua')
# draw lat/lon grid lines every 30 degrees.
map.drawmeridians(np.arange(0,360,30))
map.drawparallels(np.arange(60,90,30))
(x,y) = map(long, lat)
cs = map.scatter(x,y,3,marker='o',color='k')
plt.show()

# plt.plot(profiles[1].p(), -profiles[1].z())
# plt.show()





