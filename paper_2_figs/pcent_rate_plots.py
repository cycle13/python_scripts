"""
Calculate rate of movement of precipitation centroid for different seasons 02/02/2018

"""

import xarray as xr
import sh
import numpy as np
import matplotlib.pyplot as plt
from climatology import precip_centroid
from data_handling_updates import gradients as gr
from pylab import rcParams
from pcent_rate_max import p_cent_rate_max

    
# Set plotting directory
plot_dir = '/scratch/rg419/plots/paper_2_figs/'
mkdir = sh.mkdir.bake('-p')
mkdir(plot_dir)

# Set figure parameters
rcParams['figure.figsize'] = 12, 6
rcParams['font.size'] = 16

runs_sn = ['sn_0.250', 'sn_0.500', 'sn_1.000', 'sn_2.000', 'sn_4.000']
days = [True, False, False, False, False]
max_rate_sn, max_rate_lat_sn = p_cent_rate_max(runs_sn, days)

runs_mld = ['mld_2.5', 'mld_5', 'sn_1.000', 'mld_15', 'mld_20']
max_rate_mld, max_rate_lat_mld = p_cent_rate_max(runs_mld)

runs_rot = ['rt_0.500', 'rt_0.750', 'sn_1.000', 'rt_1.250', 'rt_1.500', 'rt_1.750', 'rt_2.000']
max_rate_rot, max_rate_lat_rot = p_cent_rate_max(runs_rot)

period_fac = [0.25, 0.5, 1., 2., 4.]
mld = [2.5, 5., 10., 15., 20.]
rot = [0.5, 0.75, 1., 1.25, 1.5, 1.75, 2.]

# Start figure with 4 subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(period_fac, max_rate_sn, 'xk', mew=2, ms=10)
ax1.set_ylabel('Max rate')
#ax1.set_xscale('log')
#ax1.set_yscale('log')
ax1.set_xlabel('P/P$_{E}$')
ax1.set_ylim([0,1.1])
ax1.set_yticks([0,0.25,0.5,0.75,1.])

ax2.plot(period_fac, max_rate_sn*period_fac, 'xk', mew=2, ms=10)
ax2.set_ylabel('Max rate (scaled)')
#ax2.set_xscale('log')
#ax2.set_yscale('log')
ax2.set_xlabel('P/P$_{E}$')
ax2.set_ylim([0,1.1])
ax2.set_yticks([0,0.25,0.5,0.75,1.])

ax3.plot(mld, max_rate_mld, 'xk', mew=2, ms=10)
ax3.set_ylabel('Max rate')
#ax3.set_xscale('log')
#ax3.set_yscale('log')
ax3.set_xlabel('MLD (m)')
ax3.set_ylim([0,1.1])
ax3.set_yticks([0,0.25,0.5,0.75,1.])

ax4.plot(rot, max_rate_rot, 'xk', mew=2, ms=10)
ax4.set_ylabel('Max rate')
#ax4.set_xscale('log')
#ax4.set_yscale('log')
ax4.set_xlabel('$\Omega$/$\Omega_{E}$')
ax4.set_ylim([0,1.1])
ax4.set_yticks([0,0.25,0.5,0.75,1.])

plt.subplots_adjust(right=0.95, left=0.1, top=0.95, bottom=0.1, hspace=0.3, wspace=0.4)
plt.savefig(plot_dir + 'ratemax_all.pdf', format='pdf')
plt.close()
    
    
    
    
    