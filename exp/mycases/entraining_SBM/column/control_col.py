

import os, sh

import numpy as np

from isca import ColumnCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

NCORES = 1

tau_bm = float(os.environ.get("tau_bm", 7200.0*1))
entpar = float(os.environ.get("entpar", 0.25))
SST    = float(os.environ.get("SST",    300.))
_tau_bm = int(tau_bm/3600)
_ep = int(entpar*100)
expname = f"col_{_tau_bm:02d}hr_ep{_ep:02d}"

# compile code 
cb = ColumnCodeBase.from_directory(GFDL_BASE)
cb.compile()  # compile the source code to working directory $GFDL_WORK/codebase
cb.compile(mycode='./mycodes')

# create an Experiment object to handle the configuration of model parameters
# and output diagnostics
exp = Experiment(expname, codebase=cb)
msgs = (
    "=== Running column Isca with parameters ===", 
    f"tau_bm = {tau_bm}", 
    f"entpar = {entpar}",
    f"SST = {SST}",
); list(map(exp.log.info, msgs))

#exp.inputfiles = [os.path.join(GFDL_BASE,'input/rrtm_input_files/ozone_1990.nc')]

#Empty the run directory ready to run
exp.clear_rundir()

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'constants_nml': {
        'omega': 0.0
    },
    
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
        'idealized_moist_model': True              #Use False for Held-Suarez
    },


    'mixed_layer_nml': {
        'depth': 0.1,  
        'albedo_value': 0.22,
        'tconst' : 285.,
        'prescribe_initial_dist':True,
        'evaporation':True,
        # 'do_read_sst':True,
        # 'sst_file':'t_surf',
        'do_uniform_sst':True,
        'uniform_sst_value':SST,
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
        'tcmin_simple':-250          #I changed that so thar C-K computations works in very cold climates
    },

    'astronomy_nml': {
        'obliq': 0.0
    },

    'rrtm_radiation_nml': {
        'solr_cnst': 1365,  
        'dt_rad': 7200,
        'do_read_ozone':False,
        'co2ppmv':300
 #       'ozone_file':'ozone_1990'
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

    'column_nml': {
        'lon_max': 1, # number of columns in longitude, default begins at lon=0.0
        'lat_max': 1, # number of columns in latitude, precise 
                      # latitude can be set in column_grid_nml if only 1 lat used. 
        'reference_sea_level_press':1.0e5,
        'num_levels':30,
        'valid_range_t':[50.,800.],
        'initial_sphum':[2.e-6],
        'vert_coord_option':'uneven_sigma',
        'surf_res':0.1,
        'scale_heights' : 5.0,
        'exponent':3.0,
        'robert_coeff':0.03
    },

    'column_grid_nml': { 
        'lat_value': 0., # set latitude to equator
    },

    # set initial condition, NOTE: currently there is not an option to read in initial condition from a file (aside from a restart file). 
    'column_init_cond_nml': {
        'initial_temperature': 264., # initial atmospheric temperature 
        'surf_geopotential': 0.0, # applied to all columns 
    },
    
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
diag_extra.add_field('column', 'pk', time_avg=True, files=['daily_avg'])
diag_extra.add_field('column', 'bk', time_avg=True, files=['daily_avg'])
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
diag_extra.add_field('column', 'ps', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('column', 'ucomp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('column', 'vcomp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('column', 'temp', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('column', 'sphum', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('column', 'height', time_avg=False, files=['4xdaily_inst'])
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
diag_extra.add_field('atmosphere', 'dt_qg_condensation', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_tg_condensation', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_qg_convection', time_avg=False, files=['4xdaily_inst'])
diag_extra.add_field('atmosphere', 'dt_tg_convection', time_avg=False, files=['4xdaily_inst'])

#Lets do a run!
if __name__=="__main__":
    exp.diag_table = diag
    exp.run(1, use_restart=False, num_cores=NCORES)

    exp.diag_table = diag_extra
    exp.run(2, num_cores=NCORES)
