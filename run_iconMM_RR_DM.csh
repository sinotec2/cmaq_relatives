#!/bin/csh -f

# ======================= ICONv5.3 Run Script ========================
# Usage: run.icon.csh >&! icon_v53.log &                                   
#
# To report problems or request help with this script/program:         
#             http://www.cmascenter.org
# ==================================================================== 

# ==================================================================
#> Runtime Environment Options
# ==================================================================

#> Choose compiler and set up CMAQ environment with correct 
#> libraries using config.cmaq. Options: intel | gcc | pgi
 setenv compiler gcc 

#> Source the config_cmaq file to set the run environment
# pushd  /nas1/cmaqruns/CMAQ_Project
# source ../CMAQ_Project/config_cmaq.csh $compiler
# popd

#> Check that CMAQ_DATA is set:
 if ( ! -e $CMAQ_DATA ) then
    echo "   $CMAQ_DATA path does not exist"
    exit 1
 endif
 echo " "; echo " Input data path, CMAQ_DATA set to $CMAQ_DATA"; echo " "
#argv[1]: month in 2 digit, 01~12
#argv[2]: run 1~12
#argv[3]:domain: d2 or d4
source $CMAQ_HOME/../CMAQ_Project/config_cmaq.csh gcc
set APPL_YR    = `echo $CMAQ_HOME|cut -d'/' -f4|cut -c3-4`
set MO         = $argv[1]
set RUN        = $argv[2]
set DM         = $argv[3]
set APYM       = ${APPL_YR}${MO}
#> Set General Parameters for Configuring the Simulation
 set VRSN     = v53                     #> Code Version
 set APPL       = $APPL_YR${argv[1]}_run${argv[2]}
#> Horizontal grid definition 
if ( $DM == 'd02' ) then
  setenv GRID_NAME  sChina_27k        # 16-character maximum
  if ( $MO == '01' ) then
    set ICTYPE   = profile                 #> Initial conditions type [profile|regrid]
  else
    set ICTYPE   = regrid             #> Initial conditions type [profile|regrid]
  endif
else if( $DM == 'd04' ) then
  setenv GRID_NAME  TWN_3X3           # 16-character maximum
  set ICTYPE   = regrid             #> Initial conditions type [profile|regrid]
else
  echo "Error input d02/d04"
  exit 1
endif

#> Set the working directory:
 set BLD      = /nas1/cmaqruns/CMAQ_Project/PREP/icon/scripts/BLD_ICON_${VRSN}_${compilerString}
 set EXEC     = ICON_${VRSN}.exe  
 set EXEC_ID  = icon
 cat $BLD/ICON_${VRSN}.cfg; echo " "; set echo

 setenv GRIDDESC $CMAQ_DATA/mcip/$APPL/$GRID_NAME/GRIDDESC #> grid description file 
 setenv IOAPI_ISPH 20                     #> GCTP spheroid, use 20 for WRF-based modeling

#> I/O Controls
 setenv IOAPI_LOG_WRITE T     #> turn on excess WRITE3 logging [ options: T | F ]
 setenv IOAPI_OFFSET_64 YES   #> support large timestep records (>2GB/timestep record) [ options: YES | NO ]
 setenv EXECUTION_ID $EXEC    #> define the model execution id

# =====================================================================
#> ICON Configuration Options
#
# ICON can be run in one of two modes:                                     
#     1) regrids CMAQ CTM concentration files (IC type = regrid)     
#     2) use default profile inputs (IC type = profile)
# =====================================================================

 setenv ICON_TYPE ` echo $ICTYPE | tr "[A-Z]" "[a-z]" ` 

# =====================================================================
#> Input/Output Directories
# =====================================================================

 set OUTDIR   = $CMAQ_HOME/data/icon                        #> output file directory

# =====================================================================
#> Input Files
#  
#  Regrid mode (IC = regrid) (includes nested domains, windowed domains,
#                             or general regridded domains)
#     CTM_CONC_1 = the CTM concentration file for the coarse domain          
#     MET_CRO_3D_CRS = the MET_CRO_3D met file for the coarse domain
#     MET_CRO_3D_FIN = the MET_CRO_3D met file for the target nested domain 
#                                                                            
#  Profile Mode (IC = profile)
#     IC_PROFILE = static/default IC profiles 
#     MET_CRO_3D_FIN = the MET_CRO_3D met file for the target domain 
#
# NOTE: SDATE (yyyyddd) and STIME (hhmmss) are only relevant to the
#       regrid mode and if they are not set, these variables will 
#       be set from the input MET_CRO_3D_FIN file
# =====================================================================
#> Output File
#     INIT_CONC_1 = gridded IC file for target domain
# =====================================================================
set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
  @ A = $RUN - 1; @ DD = $A * 4 ; @ ED = $A * 4 + 5
set DATE  = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`

    set YYYYJJJ  = `date -ud "${DATE}" +%Y%j`   #> Convert YYYY-MM-DD to YYYYJJJ
    set YYMMDD   = `date -ud "${DATE}" +%y%m%d` #> Convert YYYY-MM-DD to YYMMDD
    set YYYYMMDD = `date -ud "${DATE}" +%Y%m%d` #> Convert YYYY-MM-DD to YYYYMMDD

    setenv SDATE           ${YYYYJJJ}
    setenv STIME           120000

 if ( $ICON_TYPE == regrid ) then
   if ($DM == 'd02' ) then
     setenv CTM_CONC_1 ${CMAQ_DATA}/bcon/ICON_d1_20${APYM}_run5.nc
     setenv MET_CRO_3D_CRS ${CMAQ_DATA}/mcip/${APPL}/sChina_81k/METCRO3D_${APPL}.nc
   endif
   if ($DM == 'd04' ) then
     setenv CTM_CONC_1 ${CMAQ_DATA}/bcon/ACONC_d2_20${APYM}
     setenv MET_CRO_3D_CRS ${CMAQ_DATA}/mcip/${APPL}/sChina_27k/METCRO3D_${APPL}.nc
   endif
   setenv MET_CRO_3D_FIN ${CMAQ_DATA}/mcip/${APPL}/${GRID_NAME}/METCRO3D_${APPL}.nc
   setenv INIT_CONC_1    "$OUTDIR/ICON_${VRSN}_${APPL}_${GRID_NAME}_${ICON_TYPE}_${YYYYMMDD} -v"
 endif

 if ( $ICON_TYPE == profile ) then
    setenv IC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv
    setenv MET_CRO_3D_FIN ${CMAQ_DATA}/mcip/${APPL}/${GRID_NAME}/METCRO3D_${APPL}.nc
    setenv INIT_CONC_1    "$OUTDIR/ICON_${VRSN}_${APPL}_${GRID_NAME}_${ICON_TYPE}_${YYYYMMDD} -v"
 endif
 
#>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

 if ( ! -d "$OUTDIR" ) mkdir -p $OUTDIR

 ls -l $BLD/$EXEC; size $BLD/$EXEC
# unlimit
# limit

#> Executable call:
 time $BLD/$EXEC

 exit() 
