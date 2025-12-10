from speedOfSound import speed_of_sound
from raytrace import raytrace
import numpy as np
from matplotlib import pyplot as plt

from scipy.interpolate import make_interp_spline


import seaborn as sns
import seaborn.objects as so


def plotDepthData(ax, measurment, z, title, xlabel, yaxis_vis):
    ax.plot(measurment,z)
    ax.invert_yaxis()
    ax.grid(True)
    #ax.set_title(title)
    ax.set_xlabel(xlabel)
    if yaxis_vis:
        ax.set_ylabel('Depth [m]')
    else:
        ax.set_yticklabels([])

def ctd_trace(s,t,z, theta0, x0, y0, t_span):

    cc = speed_of_sound(s, t, z)

    return raytrace(x0,y0,theta0,t_span,z,cc)

def ctd_trace_interp(s,t,z, theta0, x0, y0, t_span, num_interp_points):

    cc = speed_of_sound(s, t, z)

    spline = make_interp_spline(z,cc,3)

    depth_diff = np.diff(z)
    #interpolate profile from z=0 to start of ctd data
    shallow_depths = np.array(np.arange(0,z[0],depth_diff[0]/(num_interp_points+1)))
    shallow_p = np.poly1d(np.polyfit(z[0:5], cc[0:5],1))
    cc_shallow = shallow_p(shallow_depths)
    new_depths = np.array([])
    for i, depth in enumerate(z[0:-2]):
        new_diff = depth_diff[i]/(num_interp_points+1)
        app_list = [depth]
        for n in range(0, num_interp_points):
            app_list.append(depth+new_diff*(n+1))
        new_depths = np.append(new_depths, np.array(app_list))
    new_depths = np.append(new_depths, np.array([z[-1]]))
    
    cc_new = np.append(cc_shallow, spline(new_depths))

    all_depths = np.append(shallow_depths, new_depths)

    return raytrace(x0,y0,theta0,t_span,all_depths,cc_new), all_depths, cc_new

def plot_trace(s,t,z,trace,plot_profile=False):
    cc = speed_of_sound(s, t, z)
    
    g = np.diff(cc)

    if plot_profile:
        #Display Depth Profile
        profile_plot, (s_ax, t_ax, c_ax, g_ax) = plt.subplots(1,4,figsize = [12,6])
        plotDepthData(s_ax, s, z, "Salinity", "Salinity (psu)", True)
        plotDepthData(t_ax, t, z, "Temperature", "Temperature (C)", False)
        plotDepthData(c_ax, cc, z, "Speed of Sound", "Speed of Sound (m/s)", False)
        plotDepthData(g_ax, g, z[0:-1], "Speed of Sound Gradient", "Speed of Sound Gradient (1/s)", False)
        profile_plot.suptitle("Depth Profile")



    xf = trace['x']
    zf = trace['z']
    theta0 = trace['theta0']

    trace_plot, (ax1,ax2) = plt.subplots(1,2, width_ratios=[1,5], figsize = [14,6])
    sns.lineplot(x=cc,y=z,ax=ax1,orient='y')
    #ax1.set_title('Sound Speed Profile')
    ax1.set_xlabel('Sound Speed [m/s]')
    ax1.set_ylabel('Depth [m]')
    ax1.set_xlim((np.min(cc)-5, np.max(cc)+5))
    for m in range (0, len(theta0)):
        sns.lineplot(x=xf[m],y=zf[m],label = f"{theta0[m]} degrees", ax=ax2)
    #ax2.set_title(f'{max(trace['t'])}s One Way Ray Trace')
    ax2.set_xlabel('Distance [m]')
    ax2.set_label('Depth [m]')
    ax2.legend()

    cutoff_plot = False #Set true to cutoff y axis below the sound propagation path (plus 5%), set false to show full sound speed profile

    if cutoff_plot:
        ax1.set_ylim((ylim := (np.max([np.max(zf[m]) for m in range(0, len(theta0))])*1.05), 0))
        ax2.set_ylim(ylim, 0)

        max_depth_indi = np.argmin(np.abs(z-ylim))
        min_viewable_c = np.min(cc[0:max_depth_indi])
        max_viewable_c = np.max(cc[0:max_depth_indi])
        ax1.set_xlim((min_viewable_c-2,max_viewable_c+2))
    else:
        ax1.set_ylim((np.max(z)*1.05, 0))
        ax2.set_ylim((max(z)*1.05, 0))

    ax2.set_xlim((0,max(list(np.max(xf[m]) for m in range(0,len(theta0))))))

    return trace_plot, ax1, ax2