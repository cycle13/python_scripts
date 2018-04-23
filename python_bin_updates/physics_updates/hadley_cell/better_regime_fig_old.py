"""
Plot overturning at 500 hPa at the Equator vs the latitude at which overturning goes below a certain threshold
Uses get_edge_psi_nh, so only considers SH cell
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import numpy as np
import xarray as xr
from hadley_cell import get_edge_psi
from pylab import rcParams
import statsmodels.api as sm


thresh = 0.   
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
    
    
    

def plot_regime(vars, varcolor='k', symbol='x', guide=10, do_linefit_l=False, do_linefit_h=False, include_withdrawal=False, show_coeff=False):
    # varcolor and symbol specify color and symbol for plotting
    # guide helps in locaton of outward and return branch, selected for shem=True
    # do_linefit_l and h, if True fit a power law to the low or high latitude part of the data
    # include_withdrawal, if True plot the whole time series including withdrawal phase
    
    psi_max = vars[1]
    edge_loc = vars[0]
    
    # Find the time when the cell edge is furthest south to use as start of time period to plot
    try:
        i = int(edge_loc[0:50].argmin('xofyear'))
    except:
        i = 0
    # Find when the cell extent is largest and when the cell strength is largest
    # Use the minimum time as a later bound for plotting
    j1 = int(edge_loc[guide:].argmax('xofyear'))+guide
    j2 = int(psi_max[guide:].argmax('xofyear'))+guide
    j = min([j1,j2])
    #print i, j
    
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



def plot_multiple(vars, plotname, logplot=True, g=None, s=None, vc=None, ll=None, lh=None, iw=None, latmax=None, psimin=None, psimax=None, show_coeff=False):
    # Overplot regime figs for multiple datasets
    
    # If plotting options aren't specified, set to default for all plots
    if g==None:
        g = [10]*len(vars)
    if s==None:
        s = ['x']*len(vars)
    if vc == None:
        vc = ['k']*len(vars)
    if ll == None:
        ll = [False]*len(vars)
    if lh == None:
        lh = [False]*len(vars)
    if iw == None:
        iw = [False]*len(vars)
    
    
    # Get boundaries for plot axes
    if latmax==None:
        latmax = [np.max(vars[i][0]).values for i in range(len(vars))]
        latmax = max(latmax)
    
    if psimin==None:
        # For min of y plotting range, look for the y coordinate corresponding to the smallest mag ITCZ lat
        psimin = [vars[i][1].values[np.argmin(np.abs(vars[i][0]-0.5)).values] for i in range(len(vars))]
        psimin = min(psimin)
    
    if psimax==None:
        psimax = [np.max(vars[i][1]).values for i in range(len(vars))]
        psimax = max(psimax)
    
    #print latmax, psimin, psimax
    
    for i in range(len(vars)):
        plot_regime(vars[i], varcolor=vc[i], symbol=s[i], guide=g[i], do_linefit_l=ll[i], do_linefit_h=lh[i], include_withdrawal=iw[i], show_coeff=show_coeff)
        
    
    
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


#vars_zs = get_edge_psi('zs_sst', thresh=thresh, lev=lev, sanity_check=True)
#vars_co2 = get_edge_psi('ap10_co2', thresh=thresh, lev=lev, sanity_check=True)
#vars_qflux = get_edge_psi('ap10_qflux', thresh=thresh, lev=lev, sanity_check=True)

#vars_ap2 = get_edge_psi('ap_2', thresh=thresh, lev=lev)
    vars_ap10 = get_edge_psi('sn_1.000', thresh=thresh, lev=lev)
#vars_ap20 = get_edge_psi('ap_20', thresh=thresh, lev=lev)
#vars_full = get_edge_psi('full_qflux', thresh=thresh, lonin=[60.,150.], lev=lev)
    vars_sn05 = get_edge_psi('sn_0.500', thresh=thresh, lev=lev)
    vars_sn20 = get_edge_psi('sn_2.000', thresh=thresh, lev=lev)
#vars_rt05 = get_edge_psi('rt_0.500', thresh=0., lev=lev)
#vars_rt10 = get_edge_psi('sn_1.000', thresh=0., lev=lev)
#vars_rt20 = get_edge_psi('rt_2.000', thresh=0., lev=lev)

#vars = [vars_ap10]
#plot_multiple(vars, 'mlds_10', s=['o'], psimin=200, psimax=470, latmax=25)

#vars = [vars_ap10]
#plot_multiple(vars, 'mlds_10_line', s=['o'], ll=[True], lh=[True], psimin=200, psimax=470, latmax=25)

#vars = [vars_ap10, vars_co2, vars_qflux]
#plot_multiple(vars, 'ap10_co2_qflux', s=['x','o','+'])#, psimin=200, psimax=470, latmax=25)

#vars = [vars_ap2, vars_ap10, vars_ap20]
#plot_multiple(vars, 'mlds', s=['x','o','+'], ll=[False,True,False], lh=[False,True,False], psimin=200, psimax=470, latmax=25)

#vars = [vars_ap2, vars_ap10, vars_ap20]
#plot_multiple(vars, 'mlds_iw', s=['x','o','+'], psimin=200, psimax=470, latmax=25, iw=[True,True,True])

#vars = [vars_ap2, vars_ap10, vars_ap20, vars_full]
#plot_multiple(vars, 'mld_full', s=['x','o','+','x'], vc=['k','k','k','r'], ll=[False,True,False,True], lh=[False,True,False,True], psimin=150, psimax=470, latmax=25)

#vars = [vars_sn05, vars_ap10, vars_sn20]
#plot_multiple(vars, 'seasons', s=['x','o','+'], ll=[False,True,False], lh=[False,True,False], psimin=200, psimax=470, latmax=25, show_coeff=True)

#vars = [vars_sn05, vars_ap10, vars_sn20]
#plot_multiple(vars, 'seasons_iw', s=['x','o','+'], psimin=200, psimax=470, latmax=25, iw=[True,True,True])

#vars = [vars_rt05, vars_rt10, vars_rt20]
#plot_multiple(vars, 'rotation', s=['x','o','+'])

#vars = [vars_rt05, vars_rt10, vars_rt20]
#plot_multiple(vars, 'rotation_iw', s=['x','o','+'], iw=[True,True,True])


