"""
Function to plot meridional overturning, zonal wind speed, and eddy flux convergences

"""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from data_handling import time_means
from physics import mass_streamfunction, gradients as gr
import sh
from pylab import rcParams

    
rcParams['figure.figsize'] = 12, 7
rcParams['font.size'] = 18
rcParams['text.usetex'] = True
    
plot_dir = '/scratch/rg419/plots/paper_1_figs/revisions/'
mkdir = sh.mkdir.bake('-p')
mkdir(plot_dir)


def uv_partitioning(data, start_index, lons):
    
    a= 6376.0e3 #radius used in model
    coslat = np.cos(data.lat * np.pi/180)
    
    u_ztav = data.ucomp[start_index:start_index+4,:,:,:].sel(lon=lons).mean(('xofyear','lon')) 
    v_ztav = data.vcomp[start_index:start_index+4,:,:,:].sel(lon=lons).mean(('xofyear','lon'))
    
    uv_eddy = data.ucomp_vcomp[start_index:start_index+4,:,:,:].sel(lon=lons).mean(('xofyear','lon')) - u_ztav * v_ztav 
    
    uv_conv = -86400. * gr.ddy( uv_eddy , uv=True)
    
    #uv_conv = xr.DataArray( cfd( (uv_eddy*coslat*coslat).values, data.lat*np.pi/180, 1 ), [('pfull', data.pfull ), ('lat', data.lat)])
    #uv_conv = -86400.*uv_conv/coslat/coslat/a

    return uv_conv, u_ztav
    
    
def u_psi(run, bef_aft, lonin=[-1.,361.]):
    
    data = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/' + run + '.nc')
    
    if lonin[1]>lonin[0]:
        lons = [data.lon[i] for i in range(len(data.lon)) if data.lon[i] >= lonin[0] and data.lon[i] < lonin[1]]
    else:
        lons = [data.lon[i] for i in range(len(data.lon)) if data.lon[i] >= lonin[0] or data.lon[i] < lonin[1]]
    
    psi = mass_streamfunction(data, a=6376.0e3, lons=lons, dp_in=50.)
    psi /= 1.e9

    psi_before = psi[:,bef_aft[0]:bef_aft[0]+4,::-1].mean('xofyear').transpose()
    psi_after = psi[:,bef_aft[1]:bef_aft[1]+4,::-1].mean('xofyear').transpose()
    
    uv_conv_before, u_ztav_before = uv_partitioning(data, bef_aft[0], lons)
    uv_conv_after, u_ztav_after  = uv_partitioning(data, bef_aft[1], lons)
    
    ds = xr.Dataset({'psi_before': (['pfull', 'lat'], psi_before),
                     'psi_after':  (['pfull', 'lat'], psi_after),
                     'uv_conv_before':  (['pfull', 'lat'], uv_conv_before),
                     'uv_conv_after':  (['pfull', 'lat'], uv_conv_after),
                     'u_ztav_before':  (['pfull', 'lat'], u_ztav_before),
                     'u_ztav_after':   (['pfull', 'lat'], u_ztav_after)},
                     coords={'pfull': ('pfull', data.pfull),
                               'lat': ('lat', data.lat)})
    
    return ds


data_ap2 = u_psi('ap_2', [30,39])

v_era = xr.open_dataset('/scratch/rg419/obs_and_reanalysis/era_v_alllevs.nc')

# Take pentad means
v_era.coords['xofyear'] = v_era.day_of_yr //5 + 1.  
v_era = v_era.groupby('xofyear').mean(('day_of_yr'))
    
lons = [v_era.lon[i] for i in range(len(v_era.lon)) if v_era.lon[i] >= 60. and v_era.lon[i] < 150.]
psi = mass_streamfunction(v_era, a=6376.0e3, lons=lons, dp_in=50.)
psi /= 1.e9
bef_aft=[18,39]
era_psi_before = psi[:,bef_aft[0]:bef_aft[0]+4,::-1].mean('xofyear').transpose()
era_psi_after = psi[:,bef_aft[1]:bef_aft[1]+4,::-1].mean('xofyear').transpose()


lwid=2


# Four subplots
f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
plt.set_cmap('RdBu_r')
#First plot
f1 = ax1.contourf(data_ap2.lat, data_ap2.pfull, data_ap2.uv_conv_before, extend = 'both', levels = np.arange(-10.,10.1,1.))
ax1.contour(data_ap2.lat, data_ap2.pfull, data_ap2.u_ztav_before, colors='0.7', levels=np.arange(-60.,61.,10.), linewidths=lwid)
ax1.contour(data_ap2.lat, data_ap2.pfull, data_ap2.psi_before, colors='k', levels=np.arange(-300.,301.,60.), linewidths=lwid)
ax1.invert_yaxis()
ax1.set_title('$ap2$, pre-onset', fontsize=17)
ax1.set_ylabel('Pressure, hPa')
ax1.set_xlim(-60,60)
ax1.grid(True,linestyle=':')
ax1.text(-80, 0, 'a)')

#Second plot
f2 = ax2.contourf(data_ap2.lat, data_ap2.pfull, data_ap2.uv_conv_after, extend = 'both', levels = np.arange(-10.,10.1,1.))
ax2.contour(data_ap2.lat, data_ap2.pfull, data_ap2.u_ztav_after, colors='0.7', levels=np.arange(-60.,61.,10.), linewidths=lwid)
ax2.contour(data_ap2.lat, data_ap2.pfull, data_ap2.psi_after, colors='k', levels=np.arange(-300.,301.,60.), linewidths=lwid)
ax2.set_xlim(-60,60)
ax2.set_title('$ap2$, post-onset', fontsize=17)
ax2.grid(True,linestyle=':')
ax2.text(-70, 0, 'b)')

#Third plot
f3 = ax3.contour(v_era.lat, v_era.pfull, era_psi_before, colors='k', levels=np.arange(-300.,301.,60.), linewidths=lwid)
ax3.grid(True,linestyle=':')
ax3.invert_yaxis()
ax3.set_title('$ERA$, pre-onset', fontsize=17)
ax3.set_ylabel('Pressure, hPa')
ax3.set_xlabel('Latitude')
ax3.text(-80, 0, 'c)') 

#Fourth plot
f4 = ax4.contour(v_era.lat, v_era.pfull, era_psi_after, colors='k', levels=np.arange(-300.,301.,60.), linewidths=lwid)
ax4.set_xlim(-60,60)
ax4.set_title('$ERA$, post-onset', fontsize=17)
ax4.grid(True,linestyle=':')
ax4.set_xlabel('Latitude')
ax4.text(-70, 0, 'd)')

    
#plt.subplots_adjust(right=0.95, top=0.95, bottom=0., hspace=0.1)
plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0., hspace=0.2)
#Colorbar
cb1=f.colorbar(f2, ax=[ax1,ax2,ax3,ax4], use_gridspec=True, orientation = 'horizontal',fraction=0.15, pad=0.12, aspect=30, shrink=0.5)

plt.savefig(plot_dir+'psi_u_era.pdf', format='pdf')
plt.close()
