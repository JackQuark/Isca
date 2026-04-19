
module qflux_mod

  use constants_mod, only : pi
  use       fms_mod, only : file_exist, open_namelist_file, check_nml_error, &
                            error_mesg, FATAL, close_file, stdlog, &
                            mpp_pe, mpp_root_pe
  
implicit none

real ::    qflux_amp      = 30.,  &
           qflux_width    = 16.,  &
           warmpool_amp   =  5.,  &
           warmpool_width = 20., &
           warmpool_zwid  = 30., &
           kang_qflux_amp = 0.
  
integer :: warmpool_k     = 1   !Use 0 for a Gaussian with width warpool_zwid


logical :: qflux_initialized = .false.


namelist /qflux_nml/ qflux_amp,qflux_width,&
     warmpool_amp,warmpool_width,warmpool_k,warmpool_zwid,&
     kang_qflux_amp

private 

public :: qflux_init,qflux,warmpool

contains

!########################################################
  subroutine qflux_init
    implicit none
    integer :: unit, ierr, io

    if ( file_exist('input.nml') )then
       unit = open_namelist_file()
       ierr=1; 
       do while (ierr /= 0)
          read( unit, nml=qflux_nml, iostat=io, end=10 )
          ierr = check_nml_error(io,'qflux_nml')
       enddo
10     call close_file(unit)
    endif

    if ( mpp_pe() == mpp_root_pe() ) write (stdlog(), nml=qflux_nml)
    
    qflux_initialized = .true.
    
  end subroutine qflux_init
!########################################################

  subroutine qflux(latb, flux)
! compute Q-flux as in Merlis et al (2013) [Part II]
    implicit none
    real,dimension(:)  ,intent(in)    :: latb   !latitude boundary
    real,dimension(:,:),intent(inout) :: flux   !total ocean heat flux
!
    integer j
    real lat,coslat

    if( .not. qflux_initialized ) then
       call error_mesg('qflux','qflux module not initialized',FATAL)
    endif
    
    do j=1, size(latb)-1
       lat = 0.5*(latb(j+1) + latb(j))
       coslat = cos(lat)
       lat = lat*180./pi
       flux(:,j) = flux(:,j) - qflux_amp*(1-2.*lat**2/qflux_width**2) * &
            exp(- ((lat)**2/(qflux_width)**2))/coslat
    enddo

    ! Kang et al 2008 style with sign convention is reversed:
    ! kang_qflux_amp>0 -> warm NH extratrop
    do j=1, size(latb)-1
       lat = 0.5*(latb(j+1) + latb(j))
       lat = lat*180./pi
       if (lat < -40.) then
          flux(:,j) = flux(:,j) + kang_qflux_amp*sin(pi*(lat+40.)/50.)
       elseif (lat > 40.) then
          flux(:,j) = flux(:,j) + kang_qflux_amp*sin(pi*(lat-40.)/50.)
       endif
    enddo

  end subroutine qflux

!########################################################

  subroutine warmpool(lonb, latb, flux)
    implicit none
    real,dimension(:)  ,intent(in)   :: lonb,latb  !lon and lat boundaries
    real,dimension(:,:),intent(inout):: flux       !total ocean heat flux
!
    integer i,j
    real lon,lat,qval,zmq

    do j=1,size(latb)-1
       lat = 0.5*(latb(j+1) + latb(j))*180./pi
       lat = lat/warmpool_width
       if( abs(lat) .le. 1.0 ) then
          if(warmpool_k .gt.0) then
             do i=1,size(lonb)-1
                lon = 0.5*(lonb(i+1) + lonb(i))
                flux(i,j) = flux(i,j) &
                    &+ (1.-lat**2.)*warmpool_amp*cos(warmpool_k*lon)
             enddo
          else
             zmq=0
             do i=1,size(lonb)-1
                lon = 0.5*(lonb(i+1) + lonb(i))*180./pi
                qval=(1.-lat**2.)*warmpool_amp*exp(-((lon-180)/warmpool_zwid)**2.)
                flux(i,j) = flux(i,j) + qval
                zmq=zmq+qval
             enddo
             flux(:,j)=flux(:,j)-zmq/size(flux,1)
          endif
       endif
    enddo

  end subroutine warmpool

!########################################################

end module qflux_mod
