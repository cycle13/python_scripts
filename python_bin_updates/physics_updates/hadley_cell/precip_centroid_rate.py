"""
Calculate rate of movement of precipitation centroid. 
Last edit 22/11/2017

"""

import xarray as xr
import sh
import numpy as np
import matplotlib.pyplot as plt
from climatology import precip_centroid
from physics import gradients as gr
from pylab import rcParams


   
def precip_centroid_rate(run, ax_in, ylim_in=1.):
    
    data = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/' + run + '.nc')
    
    precip_centroid(data)
    
    dpcentdt = gr.ddt(data.p_cent) * 86400.
    
    dpcentdt_ppos = dpcentdt.where(data.p_cent>=0.)
    dpcentdt_max = dpcentdt_ppos.where(dpcentdt_ppos==dpcentdt_ppos.max(),drop=True)
    pcent_dtmax = data.p_cent.sel(xofyear=dpcentdt_max.xofyear)
    print((dpcentdt_max.values, pcent_dtmax.values))   
    
    ax_twin = ax_in.twinx()
    
    data.p_cent.plot(ax=ax_twin, color='b')
    dpcentdt.plot(ax=ax_in, color='k')
        
    ax_in.set_xlabel('')
    ax_in.set_ylabel('')
    ax_twin.set_ylabel('')
    ax_twin.set_ylim([-30,30])
    ax_in.set_ylim([-1.*ylim_in, ylim_in])
    ax_in.set_title(run, fontsize=14)
    #ax_in.set_yticks([-8.,-4.,0.,4.,8.])
    ax_twin.spines['right'].set_color('blue')
    plt.tight_layout()
    
    return ax_twin



def pcent_grad_scatter(run, ax_in, ylim_in=1.):
    
    data = xr.open_dataset('/scratch/rg419/Data_moist/climatologies/' + run + '.nc')
    
    precip_centroid(data)
    dpcentdt = gr.ddt(data.p_cent) * 86400.
    
    ax_in.plot(data.p_cent, dpcentdt, 'xk')
        
    ax_in.set_xlabel('')
    ax_in.set_ylabel('')
    ax_in.set_xlim([-30,30])
    ax_in.set_ylim([-1.*ylim_in, ylim_in])
    ax_in.set_title(run, fontsize=14)
    
    

if __name__ == "__main__":
    
    plot_dir = '/scratch/rg419/plots/subcloud_entropy/'
    mkdir = sh.mkdir.bake('-p')
    mkdir(plot_dir)

    rcParams['figure.figsize'] = 10, 12
    rcParams['font.size'] = 14
    
    
    f, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8), (ax9, ax10)) = plt.subplots(5, 2)
    axes = [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8, ax9, ax10]
    runs = ['sn_1.000', 'zs_sst',
            'ap_2', 'ap_20',
            'rt_0.500', 'rt_2.000',
            'sn_0.500', 'sn_2.000',
            'sn_8.000', 'sine_sst_10m' ]
    ylim_in = [0.5, 2., 1., 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 1.]
    
    axes_twin=[]
    for i in range(10):
        ax_twin = precip_centroid_rate(runs[i], axes[i], ylim_in=ylim_in[i])
        axes_twin.append(ax_twin)
        
    for i in range(6):
        axes[i].set_xlim([0,72])
    
    for i in range(0,9,2):
        axes_twin[i].set_yticklabels('')
    
    axes[6].set_xlim([0,36])
    axes[7].set_xlim([0,144])
    axes[8].set_xlim([0,576])
    axes[9].set_xlim([0,72])
    for i in range(0,10,2):
        axes[i].set_ylabel('P. cent. lat')
    
    ax9.set_xlabel('Pentad')
    ax10.set_xlabel('Pentad')
    
    plt.subplots_adjust(right=0.9, left=0.1, top=0.95, bottom=0.05, hspace=0.4, wspace=0.2)
    
    plt.savefig(plot_dir + 'precip_centroid_rate.pdf', format='pdf')
    plt.close()
    
    
    
    f2, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8), (ax9, ax10)) = plt.subplots(5, 2)
    axes = [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8,ax9,ax10]
    runs = ['sn_1.000', 'zs_sst',
            'ap_2', 'ap_20',
            'rt_0.500', 'rt_2.000',
            'sn_0.500', 'sn_2.000',
            'sn_8.000', 'sine_sst_10m' ]
    
    axes_twin=[]
    for i in range(10):
        ax_twin = pcent_grad_scatter(runs[i], axes[i], ylim_in[i])
    
    ax9.set_xlabel('Precip centroid lat')
    ax10.set_xlabel('Precip centroid lat')
    for i in range(0,10,2):
        axes[i].set_ylabel('P. cent. rate')
        
    plt.subplots_adjust(right=0.97, left=0.1, top=0.95, bottom=0.05, hspace=0.4, wspace=0.2)
    
    plt.savefig(plot_dir + 'pcent_grad_scatter.pdf', format='pdf')
    plt.close()
    
