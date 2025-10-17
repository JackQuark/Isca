import sys, os

import numpy as np

from isca import ColumnCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

if len(sys.argv) > 1:
    # read tau_bm value
    tau_bm = float(sys.argv[1])
else:
    tau_bm = 7200.
print("Using tau_bm =", tau_bm)

# column model only uses 1 core
NCORES = 1

# compile code 
cb = ColumnCodeBase.from_directory(GFDL_BASE)
cb.compile()
cb.compile(mycode='./mycodes')

# create an Experiment object to handle the configuration of model parameters
# exp = Experiment(f'column_ent_{tau_bm:.0f}', codebase=cb)
exp = Experiment(f'column_ent_test', codebase=cb)

#Tell model how to write diagnostics
diag = DiagTable()
diag.add_file('atmos_monthly', 30, 'days', time_units='days')

#Tell model which diagnostics to write
diag.add_field('column', 'ps', time_avg=True)
diag.add_field('column', 'bk')
diag.add_field('column', 'pk')
diag.add_field('atmosphere', 'precipitation', time_avg=True)
diag.add_field('mixed_layer', 't_surf', time_avg=True)
diag.add_field('mixed_layer', 'flux_t', time_avg=True)
diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True)
diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True)
diag.add_field('rrtm_radiation', 'surf_lwuflx', time_avg=True)
diag.add_field('rrtm_radiation', 'toa_sw', time_avg=True)
diag.add_field('rrtm_radiation', 'olr', time_avg=True)
diag.add_field('rrtm_radiation', 'coszen', time_avg=True)
exp.diag_table = diag

#Empty the run directory ready to run
exp.clear_rundir()

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'main_nml':{
     'days'   : 360,
     'hours'  : 0,
     'minutes': 0,
     'seconds': 0,
     'dt_atmos':600,
     'current_date' : [1,1,1,0,0,0],
     'calendar' : 'thirty_day'
    },
    
    'atmosphere_nml': {
        'idealized_moist_model': True
    },

    'column_nml': {
        'lon_max': 1, # number of columns in longitude, default begins at lon=0.0
        'lat_max': 1, # number of columns in latitude, precise 
                      # latitude can be set in column_grid_nml if only 1 lat used. 
        'num_levels': 50,  # number of levels 
        'initial_sphum': 1e-3, 
        'vert_coord_option': 'even_sigma',
        'q_decrease_only':True # constrain q in stratosphere
    },

    'column_grid_nml': { 
        'lat_value': 0. # set latitude to equator
        # 'global_average': True # don't use this option at the moment
    },

    # set initial condition, NOTE: currently there is not an option to read in initial condition from a file (aside from a restart file). 
    'column_init_cond_nml': {
        'initial_temperature': 264., # initial atmospheric temperature 
        'surf_geopotential': 0.0, # applied to all columns 
    },

    'idealized_moist_phys_nml': {
        'two_stream_gray': False,
        'do_rrtm_radiation': True,    #Use RRTM radiation, not grey
        'convection_scheme': 'SIMPLE_BETTS_MILLER',     #Use the simple Betts Miller convection scheme
        'do_damping': True,
        'turb':True,
        'mixed_layer_bc':True,
        'do_virtual' :False,
        'do_simple': True,
        'roughness_mom':3.21e-05,
        'roughness_heat':3.21e-05,
        'roughness_moist':3.21e-05,                
    },

    'rrtm_radiation_nml': {
        'solr_cnst': 1365,  #s set solar constant to 1360, rather than default of 1368.22
        'dt_rad': 7200, #Use long RRTM timestep
        'do_read_ozone':False,
        'co2ppmv':300,
    },

    'qe_moist_convection_nml': {
        'rhbm':0.7,  # rh criterion for convection 
        'Tmin':160., # min temperature for convection scheme look up tables 
        'Tmax':350., # max temperature for convection scheme look up tables 
        'tau_bm':tau_bm # default: 7200.
    },
    
    'lscale_cond_nml': {
        'do_simple':True, # only rain 
        'do_evap':False,  # no re-evaporation of falling precipitation 
    },

    'surface_flux_nml': {
        'use_virtual_temp': False,
        'do_simple': True,
        'old_dtaudv': True    
    },

    'vert_turb_driver_nml': {
        'do_mellor_yamada': False,     # default: True
        'do_diffusivity': True,        # default: False
        'do_simple': True,             # default: False
        'constant_gust': 0.0,          # default: 1.0
        'use_tau': False
    },

    #Use a large mixed-layer depth, and the Albedo of the CTRL case in Jucker & Gerber, 2017
    'mixed_layer_nml': {
        'depth': 1,
        'albedo_value': 0.22,
        'tconst' : 285.,
        'prescribe_initial_dist':True,
        'evaporation':True,
        'do_qflux':True,
#        'do_qflux':False
        'do_uniform_sst': True,
        'uniform_sst_value': 303.78,
    },
    
    'sat_vapor_pres_nml': {
        'do_simple':True, 
        'tcmin_simple':-250 
    },

    # FMS Framework configuration
    'diag_manager_nml': {
        'mix_snapshot_average_fields': False  # time avg fields are labelled with time in middle of window
    },
    'fms_nml': {
        'stack_size': 6000000,                        # default: 0
        'domains_stack_size': 6000000                        # default: 0
    },
    'fms_io_nml': {
        'threading_write': 'single',                         # default: multi
        'fileset_write': 'single',                           # default: multi
    },

    'astronomy_nml': { 
            'obliq' : 0.0, 
            }, 
})

#Lets do a run!
if __name__=="__main__":
    exp.run(1, use_restart=False, num_cores=NCORES)
    for i in range(2,10):
        exp.run(i, num_cores=NCORES)
        
    diag = DiagTable()
    diag.add_file('atmos_daily', 1, 'days', time_units='days')
    
    diag.add_field('column', 'ps', time_avg=True)
    diag.add_field('column', 'bk')
    diag.add_field('column', 'pk')
    diag.add_field('atmosphere', 'precipitation', time_avg=True)
    diag.add_field('mixed_layer', 't_surf', time_avg=True)
    diag.add_field('mixed_layer', 'flux_t', time_avg=True)
    diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
    diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True)
    diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True)
    diag.add_field('rrtm_radiation', 'surf_lwuflx', time_avg=True)
    diag.add_field('rrtm_radiation', 'toa_sw', time_avg=True)
    diag.add_field('rrtm_radiation', 'olr', time_avg=True)
    diag.add_field('rrtm_radiation', 'coszen', time_avg=True)
    diag.add_field('atmosphere', 'rh', time_avg=True)
    diag.add_field('column', 'sphum', time_avg=True)
    diag.add_field('column', 'ucomp', time_avg=True)
    diag.add_field('column', 'vcomp', time_avg=True)
    diag.add_field('column', 'temp', time_avg=True)
    diag.add_field('column', 'vor', time_avg=True)
    diag.add_field('column', 'div', time_avg=True)
    diag.add_field('column', 'height', time_avg=True)
    diag.add_field('column', 'omega', time_avg=True)
    exp.diag_table = diag
    
    exp.run(10, num_cores=NCORES)