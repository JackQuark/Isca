

import os, sh

import numpy as np

from isca import IscaCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

NCORES = 32

tau_bm = float(os.environ.get("tau_bm", 7200.0))
entpar = float(os.environ.get("entpar", 0.25))
_tau_bm = int(tau_bm/3600)
_ep = int(entpar*100)
expname = f"T42_ape_{_tau_bm:02d}hr_ep{_ep:02d}_test"

# a CodeBase can be a directory on the computer,
# useful for iterative development
cb = IscaCodeBase.from_directory(GFDL_BASE)

# or it can point to a specific git repo and commit id.
# This method should ensure future, independent, reproducibility of results.
# cb = DryCodeBase.from_repo(repo='https://github.com/isca/isca', commit='isca1.1')

# compilation depends on computer specific settings.  The $GFDL_ENV
# environment variable is used to determine which `$GFDL_BASE/src/extra/env` file
# is used to load the correct compilers.  The env file is always loaded from
# $GFDL_BASE and not the checked out git repo.

cb.compile()  # compile the source code to working directory $GFDL_WORK/codebase
cb.compile(mycode='./mycodes')  # compile the source code to working directory $GFDL_WORK/codebase

# create an Experiment object to handle the configuration of model parameters
# and output diagnostics
exp = Experiment(expname, codebase=cb)
msgs = (
    "=== Running isca with parameters ===", 
    f"tau_bm = {tau_bm}", 
    f"entpar = {entpar}",
); list(map(exp.log.info, msgs))

#exp.inputfiles = [os.path.join(GFDL_BASE,'input/rrtm_input_files/ozone_1990.nc')]

#Empty the run directory ready to run
exp.clear_rundir()

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'main_nml': {
        'days'   : 360,
        'hours'  : 0,
        'minutes': 0,
        'seconds': 0,
        'dt_atmos':300,
        'current_date' : [1,1,1,0,0,0],
        'calendar' : 'thirty_day'
    },

    'idealized_moist_phys_nml': {
        'two_stream_gray': False,
        'do_rrtm_radiation': True,    #Use RRTM radiation, not grey
        'convection_scheme': 'ENTRAINING_QE',     #Use the entrainment SBM convection scheme
        'do_damping': True,
        'turb':True,
        'mixed_layer_bc':True,
        'do_virtual' :False,
        'do_simple': True,
        'roughness_mom':3.21e-05,
        'roughness_heat':3.21e-05,
        'roughness_moist':3.21e-05,
    },

    'vert_turb_driver_nml': {
        'do_mellor_yamada': False,     # default: True
        'do_diffusivity': True,        # default: False
        'do_simple': True,             # default: False
        'constant_gust': 0.0,          # default: 1.0
        'use_tau': False
    },
    
    'diffusivity_nml': {
        'do_entrain':False,
        'do_simple': True,        #Affects computation of PBL depth on the unstable side
    },

    'surface_flux_nml': {
        'use_virtual_temp': False,
        'do_simple': True,
        'old_dtaudv': True    
    },

    'atmosphere_nml': {
        'idealized_moist_model': True
    },

    'mixed_layer_nml': {
        'depth': 0.1,
        'albedo_value': 0.22,
        'tconst' : 285.,
        'prescribe_initial_dist':True,
        'evaporation':True,
        'do_ape_sst':True, # Use Neale and Hoskins (2001) APE's Control SST
    },

    'entraining_qe_moist_convection_nml': {
        'tau_bm': tau_bm, # default: 7200.
        'entpar': entpar, # default: 0.0 (equals to original SBM)
        'rhbm':0.7,
        'Tmin':160.,
        'Tmax':350.
    },
    
    'lscale_cond_nml': {
        'do_simple':True,
        'do_evap':False              #Reevaporation of rain
    },
    
    'sat_vapor_pres_nml': {
        'do_simple':True,
        'tcmin_simple':-250
    },
    
    'damping_driver_nml': {
        'do_rayleigh': True,
        'trayfric': -0.5,              # neg. value: time in *days*
        'sponge_pbottom':  50.,
        'do_conserve_energy': True,         
    },

    'astronomy_nml': {
        'obliq': 0.0
    },

    'rrtm_radiation_nml': {
        'solr_cnst': 1365,  
        'dt_rad': 7200,
        'do_read_ozone':False,
        'co2ppmv':300
        # 'ozone_file':'ozone_1990'
    },



    # FMS Framework configuration
    'diag_manager_nml': {
        'mix_snapshot_average_fields': False  # time avg fields are labelled with time in middle of window
    },

    'fms_nml': {
        'stack_size': 6000000,                               # default: 0
        'domains_stack_size': 6000000                        # default: 0
    },

    'fms_io_nml': {
        'threading_write': 'single',                         # default: multi
        'fileset_write': 'single',                           # default: multi
    },

    'spectral_dynamics_nml': {
        'damping_order': 4,             
        'water_correction_limit': 200.e2,
        'reference_sea_level_press':1.0e5,
        'num_levels':30,
        'valid_range_t':[50.,800.],
        'initial_sphum':[2.e-6],
        'vert_coord_option':'uneven_sigma',
        'surf_res':0.1,
        'scale_heights' : 5.0,
        'exponent':3.0,
        'robert_coeff':0.03
    }
    
})

#Tell model how to write diagnostics
diag = DiagTable()
diag.add_file('daily_avg', 1, 'days', time_units='days')
diag.add_field('atmosphere', 'precipitation', time_avg=True)
diag.add_field('mixed_layer', 't_surf', time_avg=True)
diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
diag.add_field('mixed_layer', 'flux_t', time_avg=True)
diag.add_field('rrtm_radiation', 'toa_sw', time_avg=True)
diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True)
diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True)
diag.add_field('rrtm_radiation', 'surf_lwuflx', time_avg=True)
diag.add_field('rrtm_radiation', 'olr', time_avg=True)

diag_extra = DiagTable()
# daily .nc
diag_extra.add_file('daily_avg', 1, 'days', time_units='days')
diag_extra.add_field('dynamics', 'pk', time_avg=True, files=['daily_avg'])
diag_extra.add_field('dynamics', 'bk', time_avg=True, files=['daily_avg'])
diag_extra.add_field('atmosphere', 'precipitation', time_avg=True, files=['daily_avg'])
diag_extra.add_field('mixed_layer', 't_surf', time_avg=True, files=['daily_avg'])
diag_extra.add_field('mixed_layer', 'flux_lhe', time_avg=True, files=['daily_avg'])
diag_extra.add_field('mixed_layer', 'flux_t', time_avg=True, files=['daily_avg'])
diag_extra.add_field('rrtm_radiation', 'toa_sw', time_avg=True, files=['daily_avg'])
diag_extra.add_field('rrtm_radiation', 'flux_sw', time_avg=True, files=['daily_avg'])
diag_extra.add_field('rrtm_radiation', 'flux_lw', time_avg=True, files=['daily_avg'])
diag_extra.add_field('rrtm_radiation', 'surf_lwuflx', time_avg=True, files=['daily_avg'])
diag_extra.add_field('rrtm_radiation', 'olr', time_avg=True, files=['daily_avg'])
# 4xdaily .nc
diag_extra.add_file('4xdaily_inst', 6, 'hours', time_units='days')
diag_extra.add_field('dynamics', 'ps', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'vor', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'div', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'omega', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'ucomp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'vcomp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'temp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'sphum', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'height', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'precipitation', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'rh', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('mixed_layer', 't_surf', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('mixed_layer', 'flux_t', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('mixed_layer', 'flux_lhe', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('rrtm_radiation', 'toa_sw', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('rrtm_radiation', 'flux_sw', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('rrtm_radiation', 'flux_lw', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('rrtm_radiation', 'surf_lwuflx', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('rrtm_radiation', 'olr', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'ucomp_rot', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'vcomp_rot', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'ucomp_div', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('dynamics', 'vcomp_div', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_qg_condensation', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_tg_condensation', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_qg_convection', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_tg_convection', time_avg=False, files=['4xdaily_inst'])

#Lets do a run!
if __name__=="__main__":
    exp.set_resolution('T42')
    exp.diag_table = diag
    exp.run(1, use_restart=False, num_cores=NCORES) 
    exp.run(2, num_cores=NCORES)
    
    exp.diag_table = diag_extra
    for run in range(3, 6):
        exp.run(run, num_cores=NCORES)