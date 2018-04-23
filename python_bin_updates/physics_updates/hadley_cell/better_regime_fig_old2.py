"""
3/11/2017
Plot max overturning at 500 hPa for cross-equatorial cell vs the latitude of max near surface mse, or vs precip centroid, or vs lat at which cell drops below some threshold
Generally the same as the previous iteration of better_regime_fig (now better_regime_fig_old) but with the option to plot mse or precip centroid as x axis
6/11/2017
Updated to take in a DataArray rather than run name to some functions (cf psi_edge_loc)
23/11/2017
Trying to use it to analyse Alex's dry runs. For the axisymmetric case need to reset bounds to look for i within in plot_regime.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
import xarray as xr
from climatology import peak_mse, precip_centroid
from pylab import rcParams
from hadley_cell import get_edge_psi
import statsmodels.api as sm


lev = 500. 
    
rcParams['figure.figsize'] = 10, 7
rcParams['font.size'] = 20
rcParams['text.usetex'] = True


def fit_power_law(edge_loc, psi_max, maxmin, show_coeff=False):
    # edge_loc - latitude of the ITCZ
    # psi_max - max overturning strength
    # maxmin - range of latitudes to use
    # show_coeff - option to print fitting coeffs to screen
    
    # Get latitudes where edge_loc is in the desired range
    lat = (edge_loc <= maxmin[1]) & (edge_loc > maxmin[0])
    edge = np.log( edge_loc[lat] )
    psi_max = np.log( psi_max[lat] )
    
    A = np.array([ edge, np.ones(edge.shape) ])
    
    # Regress psi max as edge_loc + const
    model = sm.OLS(psi_max.values, A.T)
    result=model.fit()
    consts = result.params
    std_err = result.bse
    
    #print result.summary()
    
    if show_coeff:
        # Print the coefficients and standard errors for the fit
        print('=== Coeffs ===')
        print((np.exp(consts[1]), consts[0]))
        print('=== Std Errs ===')
        print((2*std_err[1]*np.exp(consts[1]), 2*std_err[0]))
    
    # Use constants to get the line to plot, return line and constants
    line = np.exp(consts[1]) * np.arange(maxmin[0],maxmin[1]+1)**(consts[0])
    
    return line, consts
    
    
    

def plot_regime(vars_in, varcolor='k', symbol='x', guide=10, do_linefit_l=False, do_linefit_h=False, include_withdrawal=False, show_coeff=False):
    # varcolor and symbol specify color and symbol for plotting
    # guide helps in locaton of outward and return branch, selected for shem=True
    # do_linefit_l and h, if True fit a power law to the low or high latitude part of the data
    # include_withdrawal, if True plot the whole time series including withdrawal phase
    
    psi_max = vars_in[1]
    edge_loc = vars_in[0]
    
    # Find the time when the cell edge is furthest south to use as start of time period to plot
    try:
        #i = int(edge_loc[0:50].argmin('xofyear'))
        i = int(edge_loc[0:35].argmin('xofyear'))
    except:
        i = 0
    # Find when the cell extent is largest and when the cell strength is largest
    # Use the minimum time as a later bound for plotting
    j1 = int(edge_loc[guide:].argmax('xofyear'))+guide
    j2 = int(psi_max[guide:].argmax('xofyear'))+guide
    j = min([j1,j2])
    print((i,j))
    
    # Plot ITCZ lat on x axis, cell strength on y over this time period
    plt.plot(edge_loc[i:j], psi_max[i:j], symbol, color=varcolor, ms=10, mew=2)
    if include_withdrawal:
        plt.plot(edge_loc[j:], psi_max[j:], symbol, color=varcolor, ms=8, mew=2, alpha=0.5)
        plt.plot(edge_loc[:i], psi_max[:i], symbol, color=varcolor, ms=8, mew=2, alpha=0.5)
    
    # Fit a power law to a given latitude range of the data, and add the line to the plot
    if do_linefit_l:
        line, consts = fit_power_law(edge_loc[i:j], psi_max[i:j], maxmin=[0.5,7.], show_coeff=show_coeff)
        line = np.exp(consts[1]) * np.arange(0.5,7.5,0.5)**(consts[0])
        plt.plot(np.arange(0.5,7.5,0.5), line, varcolor+':', linewidth=2)
    if do_linefit_h:
        line, consts = fit_power_law(edge_loc[i:j], psi_max[i:j], maxmin=[7.,30.], show_coeff=show_coeff)
        plt.plot(np.arange(7.,31.), line, varcolor+':', linewidth=2)



def plot_multiple(vars_in, plotname, logplot=True, g=None, s=None, vc=None, ll=None, lh=None, iw=None, latmax=None, psimin=None, psimax=None, show_coeff=False):
    # Overplot regime figs for multiple datasets
    
    # If plotting options aren't specified, set to default for all plots
    if g==None:
        g = [10]*len(vars_in)
    if s==None:
        s = ['x']*len(vars_in)
    if vc == None:
        vc = ['k']*len(vars_in)
    if ll == None:
        ll = [False]*len(vars_in)
    if lh == None:
        lh = [False]*len(vars_in)
    if iw == None:
        iw = [False]*len(vars_in)
    
    
    # Get boundaries for plot axes
    if latmax==None:
        latmax = [np.max(vars_in[i][0]).values for i in range(len(vars_in))]
        latmax = max(latmax)
    
    if psimin==None:
        # For min of y plotting range, look for the y coordinate corresponding to the smallest mag ITCZ lat
        psimin = [vars_in[i][1].values[np.argmin(np.abs(vars_in[i][0]-0.5)).values] for i in range(len(vars_in))]
        psimin = min(psimin)
    
    if psimax==None:
        psimax = [np.max(vars_in[i][1]).values for i in range(len(vars_in))]
        psimax = max(psimax)
    
    #print latmax, psimin, psimax
    
    for i in range(len(vars_in)):
        plot_regime(vars_in[i], varcolor=vc[i], symbol=s[i], guide=g[i], do_linefit_l=ll[i], do_linefit_h=lh[i], include_withdrawal=iw[i], show_coeff=show_coeff)
        
    
    
    plt.xlabel('Cell edge')
    plt.ylabel('Max 500 hPa Mass Streamfunction')
    plt.grid(True,linestyle=':')
    if logplot:
        plt.xscale('log')
        plt.yscale('log')
        plt.minorticks_off()
        plt.xlim(0.5,int(latmax)+5)
        plt.ylim(int(psimin),int(psimax)+50)
        xticklist = [i for i in [1,2,5,10,20,30,40,50] if i < latmax]
        plt.xticks(xticklist)
        plt.yticks(list(range(int(round(psimin/50)*50), int(round(psimax/50)*50), 100)))
        ax=plt.gca()
        ax.get_xaxis().set_major_formatter(tk.ScalarFormatter())
        ax.get_yaxis().set_major_formatter(tk.ScalarFormatter())
        plt.tight_layout()
    else:
        plt.ylim([0,int(latmax)+5])
        plt.xlim([0,int(psimax)+50])
    plt.savefig('/scratch/rg419/plots/regime_fig/' + plotname +'.pdf', format='pdf')
    plt.close()



if __name__ == "__main__":
    
    lonin = [-1.,361.]
    
    def set_vars(data, type=None, lonin=[-1.,361.], thresh=0.):
        
        edge_loc, psi_max, psi_max_loc = get_edge_psi(data, thresh=thresh, lev=lev, lonin=lonin)
        
        if type == 'mse':
            data_mse = peak_mse(data, lonin=lonin)
            vars_out = (data_mse.mse_max_loc, psi_max)
            
        elif type == 'pcent':
            data = precip_centroid(data,lonin=lonin)
            vars_out = (data.p_cent, psi_max)

        elif type == None:
            vars_out = (edge_loc, psi_max)
        
        return vars_out
    
    data_ap2 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/ap_2.nc')
    data_ap10 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/sn_1.000.nc')
    data_ap20 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/ap_20.nc')
    data_full = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/full_qflux.nc')

    data_zs = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/zs_sst.nc')
    data_sine = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/sine_sst_10m.nc')

    data_dry_ep = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/dry_ep.nc')
    data_dry_zs = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/dry_zs.nc')
    
    data_sn05 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/sn_0.500.nc')
    data_sn20 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/sn_2.000.nc')
    data_sn80 = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/sn_8.000.nc')
    
    
    vars_full = set_vars(data_full, lonin=[60.,150.], thresh=0.4)
    vars_ap2 = set_vars(data_ap2, thresh=0.3)
    vars_ap10 = set_vars(data_ap10, thresh=0.)
    vars_ap20 = set_vars(data_ap20, thresh=0.3)
    
    vars_sn05 = set_vars(data_sn05, thresh=0.)
    vars_sn20 = set_vars(data_sn20, thresh=0.)
    vars_sn80 = set_vars(data_sn80, thresh=0.)
    
    vars_zs = set_vars(data_zs)
    vars_sine = set_vars(data_sine)
    vars_dep = set_vars(data_dry_ep, thresh=0.1)
    vars_dzs = set_vars(data_dry_zs, thresh=0.1)
    
    #vars_full = get_edge_psi('full_qflux', thresh=thresh, lonin=[60.,150.], lev=lev)
    
    #vars_in = [vars_ap10, vars_zs, vars_sine]
    #plot_multiple(vars_in, 'ep_zs', s=['x','o','+'], psimin=150., psimax=600, latmax=40)#, iw=[True, True, True])
    
    #vars_in = [vars_dep, vars_dzs]
    #plot_multiple(vars_in, 'dry', s=['x','o'], psimin=30., psimax=250, latmax=60)#, iw=[True,True])
    #plot_multiple(vars_in, 'ap_to_full', g=[10,10,10,30], s=['x','o','+','x'], vc=['k']*3+['r'], ll=[False,True,False,True], lh=[False,True,False,True], show_coeff=True, psimin=150., psimax=500.)
    

    
    vars = [vars_sn05, vars_ap10, vars_sn20, vars_sn80]
    plot_multiple(vars, 'seasons_test', s=['x','o','+','s'], ll=[False,True,False,False], lh=[False,True,False,False], psimin=200, psimax=470, latmax=25, show_coeff=True)
    #plot_multiple(vars, 'seasons_pcent', s=['x','o','+'], psimin=200, psimax=470, latmax=25)

    #vars = [vars_rt05, vars_ap10, vars_rt20]
    #plot_multiple(vars, 'rotation_pcent', s=['x','o','+'], psimin=100, psimax=600, latmax=25)
    
    #vars = [vars_ap2, vars_ap10, vars_ap20]
    #plot_multiple(vars, 'mlds_pcent', s=['x','o','+'], psimin=150, psimax=470, latmax=25)
    
    
    #vars = [vars_ap2, vars_ap10, vars_ap20, vars_full]
    #plot_multiple(vars, 'mld_full_pcent', s=['x','o','+','rx'], vc=['k','k','k','r'], psimin=200, psimax=470, latmax=25)
    
    #vars = [vars_ap10, vars_co2, vars_qflux]
    #plot_multiple(vars, 'ap10_co2_qflux_pcent', s=['x','o','+'], psimin=100, psimax=600, latmax=25)

    
    




