"""
Load in the vorticity budget terms and produce a lat-time plot at 150 hPa

"""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from data_handling import time_means, month_dic
import sh
from physics import gradients as gr
from pylab import rcParams

def vort_eq_hm(run, lev=150, rotfac=1.0, period_fac=1.):
    
    rcParams['figure.figsize'] = 10, 7.5
    rcParams['font.size'] = 18
    rcParams['text.usetex'] = True
    
    plot_dir = '/scratch/rg419/plots/crit_lat_test/'
    mkdir = sh.mkdir.bake('-p')
    mkdir(plot_dir)
    
    #Load in vorticity budget term means
    data = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/vort_eq_'+run+'.nc')    
    print 'vorticity budget data loaded'
    
    # Calculate vertical component of absolute vorticity = f + dv/dx - du/dy
    omega = 7.2921150e-5 * rotfac
    f = 2 * omega * np.sin(data.lat *np.pi/180)
    v_dx = gr.ddx(data.vcomp)  # dvdx
    u_dy = gr.ddy(data.ucomp)  # dudy
    vor = v_dx - u_dy + f
    
    abs_vort = vor.mean('lon')*86400.
    
    dvordx = gr.ddx(vor)
    dvordy = gr.ddy(vor, vector=False)
    
    horiz_md_mean = -86400.**2. * (data.ucomp * dvordx + data.vcomp * dvordy)
    
    div = gr.ddx(data.ucomp) + gr.ddy(data.vcomp)
    stretching_mean = -86400.**2. * vor * div
    
    transient = 86400.**2.*data.horiz_md + 86400.**2.*data.stretching - horiz_md_mean - stretching_mean
    
    data['transient'] = (('pentad','pfull','lat','lon'), transient.values )	
    
    horiz_md_hm = horiz_md_mean.mean('lon')
    stretching_hm = stretching_mean.mean('lon')
    transient_hm = data.transient.mean('lon')
    total_hm = data.total.sel(pfull=lev).mean('lon')
    
    mn_dic = month_dic(1)
    tickspace = range(13,72,18)
    labels = [mn_dic[(k+5)/6 ] for k in tickspace]
    levels = np.arange(-1.5,1.6,0.25)
    
    print 'starting plotting'

    # Four subplots
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
    plt.set_cmap('RdBu_r')
    #First plot
    f2=horiz_md_hm.sel(pfull=lev).plot.contourf(x='pentad', y='lat', levels=levels, ax=ax1, extend = 'both', add_labels=False, add_colorbar=False)
    ax1.contour(data.pentad, data.lat, abs_vort.sel(pfull=lev).T, levels=np.arange(-12.,13.,2.), colors='k', linewidths=2, alpha=0.25)
    ax1.set_ylabel('Latitude')
    ax1.set_ylim(-60,60)
    ax1.set_yticks(np.arange(-60,61,30))
    ax1.grid(True,linestyle=':')
    ax1.text(-10, 60, 'a)')

    #Second plot
    stretching_hm.sel(pfull=lev).plot.contourf(x='pentad', y='lat', levels=levels, ax=ax2, extend = 'both', add_labels=False, add_colorbar=False)
    ax2.contour(data.pentad, data.lat, abs_vort.sel(pfull=lev).T, levels=np.arange(-12.,13.,2.), colors='k', linewidths=2, alpha=0.25)
    ax2.set_ylim(-60,60)
    ax2.set_yticks(np.arange(-60,61,30))
    ax2.grid(True,linestyle=':')
    ax2.text(-5, 60, 'b)')
    
    
    #Third plot
    transient_hm.sel(pfull=lev).plot.contourf(x='pentad', y='lat', levels=levels, ax=ax3, extend = 'both', add_labels=False, add_colorbar=False)
    ax3.contour(data.pentad, data.lat, abs_vort.sel(pfull=lev).T, levels=np.arange(-12.,13.,2.), colors='k', linewidths=2, alpha=0.25)
    ax3.set_ylabel('Latitude')
    ax3.set_ylim(-60,60)
    ax3.set_yticks(np.arange(-60,61,30))
    ax3.set_xticks(tickspace)
    ax3.set_xticklabels(labels,rotation=25)
    ax3.grid(True,linestyle=':')
    ax3.text(-10, 60, 'c)')
    
    #Fourth plot
    (horiz_md_hm + stretching_hm).sel(pfull=lev).plot.contourf(x='pentad', y='lat', levels=levels, ax=ax4, extend = 'both', add_labels=False, add_colorbar=False)
    ax4.contour(data.pentad, data.lat, abs_vort.sel(pfull=lev).T, levels=np.arange(-12.,13.,2.), colors='k', linewidths=2, alpha=0.25)
    ax4.set_ylim(-60,60)
    ax4.set_yticks(np.arange(-60,61,30))
    ax4.set_xticks(tickspace)
    ax4.set_xticklabels(labels,rotation=25)
    ax4.grid(True,linestyle=':')
    ax4.text(-5, 60, 'd)')
    
    
    plt.subplots_adjust(right=0.97, left=0.1, top=0.95, bottom=0., hspace=0.2, wspace=0.1)
    #Colorbar
    cb1=f.colorbar(f2, ax=[ax1,ax2,ax3,ax4], use_gridspec=True, orientation = 'horizontal',fraction=0.15, pad=0.1, aspect=30, shrink=0.5)
    cb1.set_label('Vorticity tendency, day$^{-2}$')
    
    
    figname = 'vort_budg_hm_balance' + run + '.pdf'
    plt.savefig(plot_dir + figname, format='pdf')
    plt.close()
    
      
vort_eq_hm('sn_1.000')
vort_eq_hm('sn_2.000', period_fac=2.)
vort_eq_hm('sn_0.500', period_fac=0.5)
vort_eq_hm('rt_2.000', rotfac=2.)
vort_eq_hm('rt_0.500', rotfac=0.5)


