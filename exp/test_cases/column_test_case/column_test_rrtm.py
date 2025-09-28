import os

import numpy as np

from isca import ColumnCodeBase, DiagTable, Experiment, Namelist, GFDL_BASE

### to create ozone file:
from scm_interp_routine import scm_interp, global_average_lat_lon

# column model only uses 1 core
NCORES = 1

# compile code 
base_dir = os.path.dirname(os.path.realpath(__file__))
cb = ColumnCodeBase.from_directory(GFDL_BASE)
cb.compile() 

# create an Experiment object to handle the configuration of model parameters
exp = Experiment('column_test', codebase=cb)


#Tell model how to write diagnostics
diag = DiagTable()
diag.add_file('atmos_daily', 1, 'days', time_units='days')

#Tell model which diagnostics to write
diag.add_field('column', 'ps', time_avg=True)
diag.add_field('column', 'bk')
diag.add_field('column', 'pk')
diag.add_field('atmosphere', 'precipitation', time_avg=True)
diag.add_field('mixed_layer', 't_surf', time_avg=True)
diag.add_field('mixed_layer', 'flux_lhe', time_avg=True)
diag.add_field('column', 'sphum', time_avg=True)
diag.add_field('column', 'ucomp', time_avg=True)
diag.add_field('column', 'vcomp', time_avg=True)
diag.add_field('column', 'temp', time_avg=True)
diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True) # W2-B
diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True) # W2-B
diag.add_field('rrtm_radiation', 'toa_sw', time_avg=True)
diag.add_field('rrtm_radiation', 'olr', time_avg=True)
diag.add_field('rrtm_radiation', 'coszen', time_avg=True)
# diag.add_field('atmosphere', 'dt_ug_diffusion', time_avg=True)
# diag.add_field('atmosphere', 'dt_vg_diffusion', time_avg=True)
exp.diag_table = diag

#Empty the run directory ready to run
exp.clear_rundir()

#Define values for the 'core' namelist
exp.namelist = namelist = Namelist({
    'main_nml':{
     'days'   : 10,
     'hours'  : 0,
     'minutes': 0,
     'seconds': 0,
     'dt_atmos':3600,
     'current_date' : [2025,3,21,0,0,0],
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
        'lat_value': 30.0 # set latitude to that which causes insolation in frierson p2 radiation to be insolation / 4. 
        # 'global_average': True # don't use this option at the moment
    },

    # set initial condition, NOTE: currently there is not an option to read in initial condition from a file (aside from a restart file). 
    'column_init_cond_nml': {
        'initial_temperature': 264., # initial atmospheric temperature 
        'surf_geopotential': 0.0, # applied to all columns 
        'surface_wind': 5. # as described above 
    },

    'idealized_moist_phys_nml': {
        'do_damping': False, # no damping in column model, surface wind prescribed 
        'turb':True,
        'mixed_layer_bc':True,
        'do_simple': True, # simple RH calculation 
        'roughness_mom': 3.21e-05,
        'roughness_heat':3.21e-05,
        'roughness_moist':3.21e-05,
        'two_stream_gray': False,     #Use grey radiation
        'do_rrtm_radiation': True,
        # 'convection_scheme': 'NONE'
        'convection_scheme': 'SIMPLE_BETTS_MILLER', #Use the simple Betts Miller convection scheme 
        'do_lcl_diffusivity_depth':True, # use convection scheme LCL height to set PBL depth 
    },

    'rrtm_radiation_nml': {
        'solr_cnst': 1360,  #s set solar constant to 1360, rather than default of 1368.22
        'dt_rad': 3600, #Use long RRTM timestep
        'dt_rad_avg':86400, 
        # 'co2ppmv':400.,
        'lat_cnst': 30.0, # [deg]
    },

    # 'qe_moist_convection_nml': {
    #     'rhbm':0.7, # rh criterion for convection 
    #     'Tmin':160., # min temperature for convection scheme look up tables 
    #     'Tmax':350.  # max temperature for convection scheme look up tables 
    # },
    
    'lscale_cond_nml': {
        'do_simple':True, # only rain 
        'do_evap':False,  # no re-evaporation of falling precipitation 
    },

    'surface_flux_nml': {
        'use_virtual_temp': True, # use virtual temperature for BL stability 
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
        'tconst' : 285.,
        'prescribe_initial_dist':False,
        'evaporation':True,   
        'depth': 2.5,                          #Depth of mixed layer used
        'albedo_value': 0.0,                  #Albedo value used             
    },
    
    'sat_vapor_pres_nml': {
        'do_simple':True, 
    },

    # FMS Framework configuration
    'diag_manager_nml': {
        'mix_snapshot_average_fields': False  # time avg fields are labelled with time in middle of window
    },
    'fms_nml': {
        'domains_stack_size': 600000                        # default: 0
    },
    'fms_io_nml': {
        'threading_write': 'single',                         # default: multi
        'fileset_write': 'single',                           # default: multi
    },


    'astronomy_nml': { 
            'ecc' : 0.0, 
            'obliq' : 0.0, 
            'per' : 0.0
            }, 

})

#Lets do a run!
if __name__=="__main__":

    exp.run(1, use_restart=False, num_cores=NCORES, mpirun_opts='--bind-to socket')
    # for i in range(2,13):
    #     exp.run(i, num_cores=NCORES, mpirun_opts='--bind-to socket')
