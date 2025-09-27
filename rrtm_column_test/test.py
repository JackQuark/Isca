# _summary_
# author: Quark
# ==================================================
import sys
import os
import numpy     as np
import xarray    as xr
import matplotlib.pyplot  as plt
# ==================================================
P = os.path.join

base1 = "/home/cyinchang/archive/cyinchang03/Isca/column_test_rrtm"
base2 = "/home/cyinchang/archive/cyinchang03/Isca/column_test_zen30"
basedir = "/home/cyinchang/archive/cyinchang03/Isca/column_test"


class Dataset(object):
    def __init__(self, basedir):
        self.basedir = basedir
        self.rundirs = sorted(os.listdir(self.basedir)); self.rundirs.pop(0)
        self.rundirs = [P(self.basedir, rundir) for rundir in self.rundirs]
        self.ncfiles = [P(self.basedir, rundir, "atmos_daily.nc") for rundir in self.rundirs]
    
    def open(self, f, ftype='nc'):
        if ftype == 'nc':
            pass
        
    def __getitem__(self, key):
        pass
    
def main():
    ds = Dataset(basedir)
    # ds1 = Dataset(base1)
    # ds2 = Dataset(base2)
     
    with xr.open_dataset(ds.ncfiles[0], decode_timedelta=False) as d:
        d = d.isel(lat=0, lon=0)
        ofname = "col_rrtm.lat0.test1.txt"
        if os.path.exists(ofname):
            raise ValueError(f"{ofname} already exists")
        
        with open(ofname, 'w') as f:
            f.write("time\tcoszen\ttoa_sw\tcoszen*S_0\n")
            for i in range(10):
                f.write(f"{d.time[i].values}\t{d.coszen[i].values:.5f}\t{d.toa_sw[i].values:.5f}\t{d.coszen[i].values * 1360:.5f}\n")
            f.write("\n")
            with open("/home/cyinchang/archive/cyinchang03/Isca/column_test/run0001/input.nml", 'r') as nml:
                while True:
                    line = nml.readline()
                    if not line: break
                    f.write(line)
        
        print(d.toa_sw.values)
        print(d.coszen.values)
        print(d.coszen.values * 1360)
    
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
