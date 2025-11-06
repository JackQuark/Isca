# Dataset for Isca output
# author: Quark
# ==================================================
import os
import xarray    as xr

from .logger import Logger
# ==================================================
P = os.path.join

class Isca_Dataset(Logger):
    def __init__(self, BaseDIR):
        self.BaseDIR = BaseDIR
        self.run_dirs = sorted(os.listdir(self.BaseDIR)); self.run_dirs.pop(0) # pop restart/
        self.run_dirs = [P(self.BaseDIR, d) for d in self.run_dirs]
        self.nc_files = [[f for f in os.listdir(d) if f.endswith(".nc")][0] for d in self.run_dirs]
        self.nc_files = [P(d, f) for d, f in zip(self.run_dirs, self.nc_files)]
        
        self.nml_file = P(self.run_dirs[0], "input.nml")

    def show_nml(self, name_nml: str | None = None):
        with open(self.nml_file, 'r') as f:
            if name_nml is None: # show all
                print(f.read())
            else:
                for line in f:
                    if not line.startswith("&"):
                        continue
                    elif name_nml in line:
                        print(line.strip())
                        while True:
                            print(line := f.readline(), end='')
                            if line.startswith("/"):
                                break
                        break
        
    def open(self, run_N: int, **kwargs):
        """**kwargs: keyword arguments for xr.open_dataset()"""
        ds = xr.open_dataset(self.nc_files[run_N-1], use_cftime=True, **kwargs)
        self.log.info(f"Opening {self.run_dirs[run_N-1]}")
        return ds

    def __getitem__(self, key):
        pass
