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

ctrlT42 = "/home/cyinchang/archive/cyinchang05/Isca/T42_kangm20_slab1m_SBM"
uniformT42 = "/home/cyinchang/archive/cyinchang03/Isca/T42_kangm20_slab1m_test"
    
def initFig_global(ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.get_figure()

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_aspect('equal')
    return fig, ax

def array_equal(a, b):
    if np.array_equal(a, b):
        return True
    else:
        print("Maximum err:", np.max(np.abs(a-b)))
        return False
    
def check_energy_budget(ids, ds):
    ids.log.info("Check surface budget")
    ds = ds.squeeze()
    # plot_coszen(d)
    if hasattr(ds, "surf_lwuflx"):
        ids.log.info("Use surface LW uflux directly")
        # ds['surfE'] = ds.flux_t + ds.flux_lhe + ds.surf_swuflx - ds.surf_swdflx + ds.surf_lwuflx - ds.surf_lwdflx
        ds['surfE'] = ds.flux_t + ds.flux_lhe - ds.flux_sw - ds.flux_lw + ds.surf_lwuflx
    else:
        ids.log.info("Use Stefan-Boltzmann law to calculate surface LW uflux")
        ds['surfE'] = ds.flux_t + ds.flux_lhe - ds.flux_sw - ds.flux_lw + 5.6704e-8 * ds.t_surf**4
    ds['toaE'] = ds.toa_sw - ds.olr
    
    weights = np.cos(np.deg2rad(ds.lat))
    weights = weights / weights.mean()
    surfE_wmean = ds.surfE.weighted(weights).mean(dim=('lon', 'lat'))
    toaE_wmean  = ds.toaE.weighted(weights).mean(dim=('lon', 'lat'))
    
    fig, axs = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
    axs[0].plot(np.arange(1, ds.time.size+1), surfE_wmean, lw=1.)
    axs[0].set_title("Surf. budget", loc='left')
    axs[1].plot(np.arange(1, ds.time.size+1), toaE_wmean, lw=1.)
    axs[1].set_title("TOA budget", loc='left')
    
    fig, axs = plt.subplots(2, 1, figsize=(6, 5))
    fig.subplots_adjust(hspace=0.3)
    axs[0].set_title("Surf. budget", loc='left')
    axs[1].set_title("TOA budget", loc='left')
    _sel  = ds.surfE.mean(dim=('time'))
    _max  = np.ceil(np.max(np.abs(_sel.values)))
    cf0   = axs[0].contourf(ds.lon, ds.lat, _sel, levels=np.linspace(-_max, _max, 19), cmap='coolwarm')
    cbar0 = plt.colorbar(cf0, ax=axs[0], shrink=0.75)
    _sel  = ds.toaE.mean(dim=('time'))
    _max  = np.ceil(np.max(np.abs(_sel.values)))
    cf1   = axs[1].contourf(ds.lon, ds.lat, _sel, levels=np.linspace(-_max, _max, 19), cmap='coolwarm')
    cbar1 = plt.colorbar(cf1, ax=axs[1], shrink=0.75)

def main():
    ids = Isca_Dataset(uniformT42)
    # ids.show_nml()
    with ids.open(0, decode_timedelta=False) as d:
        # selvar = d.t_surf
        # print(selvar.max(), selvar.min(), sep='\n')
        # fig, ax = initFig_global()
        # c = ax.contourf(d.lon, d.lat, selvar.mean('time').values, levels=16, cmap='coolwarm')
        # cbar = plt.colorbar(c, shrink=0.5)
        # # print(d.surf.max().values)
        # return 
        check_energy_budget(ids, d)
        
    
def zonal_mean_section(ds: xr.Dataset, var='temp'):
    fig, ax = plt.subplots(figsize=(5, 3))
    
    c  = ax.contour(ds.lat, ds.pfull, ds[var].mean(dim=('time','lon')), levels=16, colors='k')
    cl = ax.clabel(c)
    
    ax.invert_yaxis()
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Pressure (hPa)')
    ax.set_title(f'Zonal Mean Section of {var}')

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    main()
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
