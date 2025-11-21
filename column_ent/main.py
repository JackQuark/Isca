# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import xarray    as xr
import matplotlib.pyplot  as plt

sys.path.append("/home/cyinchang/cyinchang03/workspace/")
from diagtools import *
# ==================================================
P = os.path.join

def plot_coszen(d: xr.Dataset, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(np.arange(d.time.size), d.coszen.values)
    return ax

def main(ds: Isca_Dataset):    
    with ds.open(5) as d:
        d = d.squeeze()
        zslice = slice(500, 850)
        d = d.sel(pfull=zslice)
        # print(d)
        # plot_coszen(d)

        if hasattr(d, "surf_lwuflx"):
            ds.log.info("Use surface LW uflux directly")
            d['surfE'] = d.flux_t + d.flux_lhe - d.flux_sw - d.flux_lw + d.surf_lwuflx
        else:
            ds.log.info("Use Stefan-Boltzmann law to calculate surface LW uflux")
            d['surfE'] = d.flux_t + d.flux_lhe - d.flux_sw - d.flux_lw + 5.6704e-8 * d.t_surf**4
        d['toaE'] = d.toa_sw - d.olr

    def CC_eq(Temp):
        """C-C equation, [K] => [Pa]"""
        es = 611.2 * np.exp( cnst.Lv/cnst.Rv * ( 1./273.15 - 1./Temp )) # Pa
        return es
    ε = cnst.Rd / cnst.Rv
    def e_2_qv(e, p):
        """vapor pressure [Pa], pressure [Pa] => specific humidity [kg/kg]"""
        qv = e * ε / ( p - ( 1 - ε ) * e )
        return qv

    d['qsat'] = e_2_qv(CC_eq(d.temp), d.pfull*100)
    d['MSEsat'] = cnst.cp * d.temp + cnst.Lv * d.qsat + cnst.g * d.height

    fig, ax = plt.subplots(figsize=(6, 6))
    X = ((cnst.Lv * (d.qsat - d.sphum)).mean(dim='pfull')) / 1000
    Y = (d.MSEsat[:, -1] - d.MSEsat[:, 0]) / 1000
    X = X.values
    Y = Y.values
      
    ax.scatter(X, Y, s=5, alpha=0.5)
    ax.set_xlabel(r"$Lv * (q^* - q)$")
    ax.set_ylabel(r"$MSE^*_{850} - MSE^*_{500}$")    
    ax.set_xlim(0, 12)
    ax.set_ylim(-12, 0)
    # plot_energy_budget(d)

def plot_energy_budget(ds: xr.Dataset, axs=None):
    if axs is None:
        fig, axs = plt.subplots(2, 1, figsize=(6, 6))        
        
    axs[0].plot(np.arange(1, ds.time.size+1), ds.surfE, lw=1.)
    axs[0].set_title("Surf. budget", loc='left')
    axs[1].plot(np.arange(1, ds.time.size+1), ds.toaE, lw=1.)
    axs[1].set_title("TOA budget", loc='left')

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()

    tau_bms = [7200, 14400, 28800, 57600, 115200] # 1x, 2x, 4x, 8x
    tau_bm  = tau_bms[3]
    BaseDIR = f"/home/cyinchang/archive/cyinchang03/Isca/column_ent_{tau_bm:d}"

    main(Isca_Dataset(BaseDIR))
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
