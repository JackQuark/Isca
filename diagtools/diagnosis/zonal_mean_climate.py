import xarray as xr
import numpy as np

from ..shared import constants as cs

class zonal_mean_climate(object):
  
  def __init__(
      self,
      ds:xr.Dataset=None,  # dataset (xrdataset, in)
  ):

    self.nlat=ds.lat.size
    self.nlev=ds.pfull.size
    
    self.dlatb=xr.DataArray(data=np.diff(ds.latb),
             dims=["lat"],coords=dict(lat=ds.lat.values))

    self.dsigma=xr.DataArray(data=np.diff(ds.phalf*100)/cs.pref,
             dims=["pfull"],coords=dict(pfull=ds.pfull.values))
    
    self.zonal_int=2*np.pi*cs.a*np.cos(ds.lat/180*np.pi)
    
    self.ds=ds

  def atmospheric_energy_input(self):
        
    AEI=(self.ds.toa_sw-self.ds.olr)-(self.ds.flux_sw+self.ds.flux_lw-cs.Stefan*self.ds.t_surf**4-self.ds.flux_t-self.ds.flux_lhe)
        
    return (AEI.mean(dim='lon').mean(dim='time')*self.zonal_int).rename('AEI')
    
        
  def meridional_energy_transport_from_AEI(self):
    
    AEI=self.atmospheric_energy_input()

    MET = np.zeros([self.nlat+1])
    for i in np.arange(0,self.nlat+1): # integrate from 90S
        MET[i] = np.sum(AEI.isel(lat=slice(None, i, 1))*self.dlatb/180*np.pi*cs.a,axis=0)

    return xr.DataArray(data=MET,
             dims=["latb"],coords=dict(latb=self.ds.latb.values)).rename('MET_AEI')


  def precip_minus_evap(self):
        
    PME=self.ds.precipitation-self.ds.flux_lhe/cs.Lv
        
    return (PME.mean(dim='lon').mean(dim='time')*self.zonal_int).rename('PME')
    
        
  def meridional_energy_transport_from_PME(self):
    
    PME=self.precip_minus_evap()*cs.Lv

    MLET = np.zeros([self.nlat+1])
    for i in np.arange(0,self.nlat+1): # integrate from 90S
        MLET[i] = np.sum(-PME.isel(lat=slice(None, i, 1))*self.dlatb/180*np.pi*cs.a,axis=0)

    return xr.DataArray(data=MLET,
             dims=["latb"],coords=dict(latb=self.ds.latb.values)).rename('MLET_PME')


  def moist_static_energy(self):
    
    return cs.cp*self.ds.temp+cs.g*self.ds.height+cs.Lv*self.ds.sphum
    
  def kinetic_energy(self):
    
    return 0.5*(self.ds.ucomp**2+self.ds.vcomp**2)

  def meridional_energy_transport(self,tracer):
        
    if tracer=='e':
        C=self.moist_static_energy()+self.kinetic_energy()
    elif tracer=='mse':       
        C=self.moist_static_energy()
    elif tracer=='dse':
        C=cs.cp*self.ds.temp+cs.g*self.ds.height
    elif tracer=='le':
        C=cs.Lv*self.ds.sphum
        
    v=self.ds.vcomp
    dp=(self.dsigma*self.ds.ps).transpose('time','pfull','lat','lon')
        
    Cvdp=(C*v*dp).mean(dim='lon').mean(dim='time')
    
    C_vdp = C.mean(dim='lon').mean(dim='time') \
       *(v*dp).mean(dim='lon').mean(dim='time') 
    
#    Cv_dp = (C*v).mean(dim='lon').mean(dim='time') \
#       *(dp).mean(dim='lon').mean(dim='time') 
    
#    C_v_dp = C.mean(dim='lon').mean(dim='time') \
#       *v.mean(dim='lon').mean(dim='time') \
#       *dp.mean(dim='lon').mean(dim='time')
        
    total=xr.DataArray(data=Cvdp/cs.g*self.zonal_int,
             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('MET_total')
    
    MMC=xr.DataArray(data=C_vdp/cs.g*self.zonal_int,
             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('MET_MMC')
    
#    total_cps=xr.DataArray(data=Cv_dp/cs.g*self.zonal_int,
#             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('MET_total_cps')
#    
#    MMC_cps=xr.DataArray(data=C_v_dp/cs.g*self.zonal_int,
#             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('MET_MMC_cps')
 
#    return xr.merge([total,MMC,total_cps,MMC_cps])
    return xr.merge([total,MMC])

  def meridional_flux_divergence(self,tracer):

    if tracer=='e':
        C=self.moist_static_energy()+self.kinetic_energy()
    elif tracer=='mse':
        C=self.moist_static_energy()
    elif tracer=='dse':
        C=cs.cp*self.ds.temp+cs.g*self.ds.height
    elif tracer=='le':
        C=cs.Lv*self.ds.sphum
    elif tracer=='angular_momentum':
        C=self.ds.ucomp*cs.a*np.cos(self.ds.lat/180.*np.pi)

    v=self.ds.vcomp
    dp=(self.dsigma*self.ds.ps).transpose('time','pfull','lat','lon')

    Cvdp=(C*v*dp).mean(dim='lon').mean(dim='time')

    C_vdp = C.mean(dim='lon').mean(dim='time') \
       *(v*dp).mean(dim='lon').mean(dim='time')

    vpCp = (Cvdp.values - C_vdp.values)/dp.mean(dim='time').mean(dim='lon').values
    del Cvdp, C_vdp, dp, v, C

    vpCp_b = np.zeros([self.nlev, self.nlat+1])
    dvpCpdy = np.zeros([self.nlev, self.nlat])

    for i in np.arange(0, self.nlev):
        vpCp_b[i,1:-1] = np.interp(self.ds.latb.values[1:-1],self.ds.lat.values,vpCp[i,:])
        dvpCpdy[i,:] = np.diff(vpCp_b[i,:]*np.cos(self.ds.latb.values/180.*np.pi),axis=-1)/np.diff(self.ds.latb.values)/np.cos(self.ds.lat.values/180.*np.pi)

    dvpCpdy = dvpCpdy/cs.a/np.pi*180.

    return xr.DataArray(data=dvpCpdy,
             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('dvpCpdy')

  def vertical_flux_divergence(self,tracer):

    if tracer=='e':
        C=self.moist_static_energy()+self.kinetic_energy()
    elif tracer=='mse':
        C=self.moist_static_energy()
    elif tracer=='dse':
        C=cs.cp*self.ds.temp+cs.g*self.ds.height
    elif tracer=='le':
        C=cs.Lv*self.ds.sphum

    wC = (C * self.ds.omega).mean(dim='time').mean(dim='lon').values
    wpCp = wC-self.ds.omega.mean(dim='time').mean(dim='lon').values*C.mean(dim='time').mean(dim='lon').values
    del wC, C

    wpCp_b = np.zeros([self.nlev+1, self.nlat])
    dwpCpdp = np.zeros([self.nlev, self.nlat])

    ps = self.ds.ps.mean(dim='time').mean(dim='lon').values
    for j in np.arange(0, self.nlat):
        wpCp_b[1:-1,j]=np.interp(self.ds.phalf.values[1:-1],self.ds.pfull.values,wpCp[:,j])
        dwpCpdp[:,j]=np.diff(wpCp_b[:,j], axis=0)/np.diff(self.ds.phalf.values)/100*cs.pref/ps[j]
    del ps, wpCp, wpCp_b

    return xr.DataArray(data=dwpCpdp,
             dims=["pfull","lat"],coords=dict(pfull=self.ds.pfull.values,lat=self.ds.lat.values)).rename('dwpCpdp')

  def mass_streamfunction(self):
    
    v=self.ds.vcomp
    dp=(self.dsigma*self.ds.ps).transpose('time','pfull','lat','lon')
        
    MMT=(v*dp).mean(dim='lon').mean(dim='time')/cs.g*self.zonal_int
    
#    MMT_cps= v.mean(dim='lon').mean(dim='time') \
#       *dp.mean(dim='lon').mean(dim='time')/cs.g*self.zonal_int 
    
    psi = np.zeros([self.nlev+1,self.nlat])
#    psi_cps = np.zeros([self.nlev+1,self.nlat])
    for i in np.arange(0,self.nlev+1): # integrate from sigma=0
        psi[i,:] = np.sum(MMT.isel(pfull=slice(None, i, 1)).values,axis=0)
#        psi_cps[i,:] = np.sum(MMT_cps.isel(pfull=slice(None, i, 1)).values,axis=0)

    Psi = xr.DataArray(data=psi,
             dims=["phalf","lat"],coords=dict(phalf=self.ds.phalf.values,lat=self.ds.lat.values)).rename('psi')
    
#    Psi_cps = xr.DataArray(data=psi_cps,
#             dims=["phalf","lat"],coords=dict(phalf=self.ds.phalf.values,lat=self.ds.lat.values)).rename('psi_cps')

#    return xr.merge([Psi,Psi_cps])
    return Psi

  def mass_streamfunction_max(self):
    
    psi=self.mass_streamfunction()

    index_array = np.argmax(np.abs(psi.values), axis=0)
    mpsi=np.take_along_axis(psi.values, np.expand_dims(index_array, axis=0), axis=0)
    
    return xr.DataArray(data=np.squeeze(mpsi),
             dims=["lat"],coords=dict(lat=self.ds.lat.values)).rename('psi_max')

