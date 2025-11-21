# _summary_
# author: Quark
# ==================================================
import sys, os
import numpy     as np
import xarray    as xr
import matplotlib.pyplot  as plt

sys.path.append("/home/cyinchang/cyinchang03/workspace")
from diagtools import *
# ==================================================

def initFig_global(ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.get_figure()

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_aspect('equal')
    return fig, ax

def check_energy_budget(ids, ds):
    ids.log.info("Check surface budget")
    ds = ds.squeeze()
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
    
    fig, axs = plt.subplots(3, 1, figsize=(6, 6), sharex=True)
    L0, = axs[0].plot(np.arange(1, ds.time.size+1), surfE_wmean, lw=1.)
    axs[0].set_title("Surf. budget", loc='left')
    L1, = axs[1].plot(np.arange(1, ds.time.size+1), toaE_wmean, lw=1.)
    axs[1].set_title("TOA budget", loc='left')
    axs[2].plot(np.arange(1, ds.time.size+1), L0.get_ydata() + L1.get_ydata(), lw=1.)
    axs[2].set_title("Net budget (Atmos.)", loc='left')
    
    fig, axs = plt.subplots(3, 1, figsize=(6, 6), sharex=True)
    fig.subplots_adjust(hspace=0.3)
    axs[0].set_title("Surf. budget", loc='left')
    axs[1].set_title("TOA budget", loc='left')
    axs[2].set_title("Precipitaion", loc='left')
    _sel  = ds.surfE.mean(dim=('time'))
    # _sel  = ds.surfE.isel(time=-1)
    _max  = np.ceil(np.max(np.abs(_sel.values)))
    # cf0   = axs[0].contourf(ds.lon, ds.lat, _sel, levels=np.linspace(-_max, _max, 19), cmap='coolwarm')
    cf0   = axs[0].contourf(ds.lon, ds.lat, _sel, levels=None, cmap='Blues_r')
    cbar0 = plt.colorbar(cf0, ax=axs[0], shrink=0.75)
    _sel  = ds.toaE.mean(dim=('time'))
    # _sel  = ds.toaE.isel(time=-1)
    _max  = np.ceil(np.max(np.abs(_sel.values)))
    # cf1   = axs[1].contourf(ds.lon, ds.lat, _sel, levels=np.linspace(-_max, _max, 19), cmap='coolwarm')
    cf1   = axs[1].contourf(ds.lon, ds.lat, _sel, levels=None, cmap='Oranges')
    cbar1 = plt.colorbar(cf1, ax=axs[1], shrink=0.75)

    _sel  = ds.precipitation.mean(dim=('time'))
    cf2   = axs[2].contourf(ds.lon, ds.lat, _sel, levels=None, cmap='jet')
    cbar2 = plt.colorbar(cf2, ax=axs[2], shrink=0.75)
    axs[2].set_xlabel('Longitude')

def main(ids: Isca_Dataset):
    with ids.open(11, decode_timedelta=False) as ds:
        check_energy_budget(ids, ds)
        return 
        d = ds.squeeze()
        yslice = slice(-20, 20)
        zslice = slice(500, 850)
        d = d.sel(pfull=zslice, lat=yslice)
 
    # def CC_eq(Temp):
    #     """C-C equation, [K] => [Pa]"""
    #     es = 611.2 * np.exp( cnst.Lv/cnst.Rv * ( 1./273.15 - 1./Temp )) # Pa
    #     return es
    # ε = cnst.Rd / cnst.Rv
    # def e_2_qv(e, p):
    #     """vapor pressure [Pa], pressure [Pa] => specific humidity [kg/kg]"""
    #     qv = e * ε / ( p - ( 1 - ε ) * e )
    #     return qv

    # d['qsat'] = e_2_qv(CC_eq(d.temp), d.pfull*100)
    # d['MSEsat'] = cnst.cp * d.temp + cnst.Lv * d.qsat + cnst.g * d.height

    # fig, ax = plt.subplots(figsize=(6, 6))
    # X = ((cnst.Lv * (d.qsat - d.sphum)).mean(dim='pfull')) / 1000
    # Y = (d.MSEsat[:, -1] - d.MSEsat[:, 0]) / 1000
    # X = np.reshape(X.values, (2, 360, -1)).mean(axis=0)
    # Y = np.reshape(Y.values, (2, 360, -1)).mean(axis=0)
    
    # from scipy.stats import linregress
    # slope, intercept, r_value, p_value, std_err = linregress(X.reshape(-1), Y.reshape(-1))
    # x_fit = np.linspace(X.min(), X.max(), 100)
    # y_fit = slope * x_fit + intercept
    
    # ax.text(0.01, 0.99, f'ε: {-slope:.5f}' + r' $km^{-1}$', fontsize=12, va='top', ha='left', transform=ax.transAxes)
    # ax.plot(x_fit, y_fit, color='red', label=f'Fit: y={slope:.2f}x+{intercept:.2f}')
  
    # ax.scatter(X, Y, s=5, alpha=0.5)
    # ax.set_xlabel(r"$Lv * (q^* - q)$")
    # ax.set_ylabel(r"$MSE^*_{850} - MSE^*_{500}$")    

# ==================================================
from time import perf_counter
if __name__ == '__main__':
    start_time = perf_counter()
    
    ctrlT42 = "/home/cyinchang/archive/cyinchang03/Isca/T42_kangm20_slab1m_SBM"
    uniT42 = "/home/cyinchang/archive/cyinchang03/Isca/T42_kangm20_slab1m_test"
    uniT42_nonrot = "/home/cyinchang/archive/cyinchang03/Isca/uniformT42_nonrot"
    uniT42_nonrot_entqe = "/home/cyinchang/archive/cyinchang03/Isca/uniformT42_nonrot_entqe"
    # ids = Isca_Dataset(uniT42)    
    ids = Isca_Dataset(uniT42_nonrot)    
    # ids = Isca_Dataset(uniT42_nonrot_entqe)
    main(ids)
    
    end_time = perf_counter()
    print('\ntime :%.3f ms' %((end_time - start_time)*1000))
