#!/bin/csh -f

# ======================= BCONv5.3 Run Script ======================== 
# Usage: run.bcon.csh >&! bcon_v53.log &                                
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
# pushd  ${CMAQ_HOME}/../CMAQ_Project
 setenv CMAQ_HOME $PWD
 source /opt/CMAQ_Project/config_cmaq.csh $compiler
 
# popd

#> Check that CMAQ_DATA is set:
 if ( ! -e $CMAQ_DATA ) then
    echo "   $CMAQ_DATA path does not exist"
    exit 1
 endif
 echo " "; echo " Input data path, CMAQ_DATA set to $CMAQ_DATA"; echo " "

#> Set General Parameters for Configuring the Simulation
set APPL_YR    = `echo $CMAQ_HOME|cut -d'/' -f4|cut -c3-4`
set MO         = $argv[1]
set RUN        = $argv[2]
set DM         = $argv[3]
set APYM       = ${APPL_YR}${MO}
set CAS        = 11 #teds11

 set VRSN     = v53                     #> Code Version
 set APPL       = ${APYM}_run${RUN}
#> Horizontal grid definition
if ( $DM == 'd01' ) then
  setenv GRID_NAM0  sChina_81k      # 16-character maximum
  setenv GRID_NAME  EAsia_81K       # 16-character maximum
  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
else if ( $DM == 'd02' ) then
  setenv GRID_NAM0  EAsia_81K         # 16-character maximum
  setenv GRID_NAME  sChina_27k        # 16-character maximum
# set BCTYPE   = profile                 #> Initial conditions type [profile|regrid]
  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
else if( $DM == 'd04' ) then
  setenv GRID_NAM0  sChina_27k      # 16-character maximum
  setenv GRID_NAME  TWN_3X3         # 16-character maximum
  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
else
  echo "Error input d02/d04"
  exit 1
endif
set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]



#> Set the build directory:
 set BLD      = /opt/CMAQ_Project/PREP/bcon/scripts/BLD_BCON_${VRSN}_${compilerString}
 set EXEC     = BCON_${VRSN}.exe  
 set EXEC_ID  = bcon
 cat $BLD/BCON_${VRSN}.cfg; echo " "; set echo

#> Horizontal grid definition 
 setenv GRIDDESC $CMAQ_DATA/mcip/$APPL/$GRID_NAME/GRIDDESC #> grid description file 
 setenv IOAPI_ISPH 20                     #> GCTP spheroid, use 20 for WRF-based modeling

#> I/O Controls
 setenv IOAPI_LOG_WRITE F     #> turn on excess WRITE3 logging [ options: T | F ]
 setenv IOAPI_OFFSET_64 YES   #> support large timestep records (>2GB/timestep record) [ options: YES | NO ]
 setenv EXECUTION_ID $EXEC    #> define the model execution id

# =====================================================================
#> BCON Configuration Options
#
# BCON can be run in one of two modes:                                     
#     1) regrids CMAQ CTM concentration files (BC type = regrid)     
#     2) use default profile inputs (BC type = profile)
# =====================================================================

 setenv BCON_TYPE ` echo $BCTYPE | tr "[A-Z]" "[a-z]" `

# =====================================================================
#> Input/Output Directories
# =====================================================================

 setenv OUTDIR  $CMAQ_HOME/data/bcon       #> output file directory

# =====================================================================
#> Input Files
#  
#  Regrid mode (BC = regrid) (includes nested domains, windowed domains,
#                             or general regridded domains)
#     CTM_CONC_1 = the CTM concentration file for the coarse domain          
#     MET_CRO_3D_CRS = the MET_CRO_3D met file for the coarse domain
#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target nested domain
#                                                                            
#  Profile mode (BC type = profile)
#     BC_PROFILE = static/default BC profiles 
#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target domain 
#
# NOTE: SDATE (yyyyddd), STIME (hhmmss) and RUNLEN (hhmmss) are only 
#       relevant to the regrid mode and if they are not set,  
#       these variables will be set from the input MET_BDY_3D_FIN file
# =====================================================================
#> Output File
#     BNDY_CONC_1 = gridded BC file for target domain
# =====================================================================
set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
  @ A = $RUN - 1; @ DD = $A * 4 
  @ B = $RUN + 1; @ DB = $RUN * 4 
set DATE  = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`
set NDAYS = 6
 
    set YYYYJJJ  = `date -ud "${DATE}" +%Y%j`   #> Convert YYYY-MM-DD to YYYYJJJ
    set YYYYMMDD = `date -ud "${DATE}" +%Y%m%d` #> Convert YYYY-MM-DD to YYYYMMDD
    set YYMMDD   = `date -ud "${DATE}" +%y%m%d` #> Convert YYYY-MM-DD to YYMMDD

#   setenv SDATE           ${YYYYJJJ}
#   setenv STIME           000000
#   setenv RUNLEN          240000

 if ( $BCON_TYPE == regrid ) then 
    setenv MET_CRO_3D_CRS $CMAQ_DATA/mcip/$APPL/${GRID_NAM0}/METCRO3D_$APPL.nc
    if ( $DM == 'd01' ) then
      setenv CTM_CONC_1 $CMAQ_DATA/bcon/ICON_d1_20${APYM}_run${RUN}.nc
    else #if( $DM == 'd02'|| $DM == 'd04' ) then
      setenv CTM_CONC_1 $CMAQ_DATA/bcon/ACONC_d2_20${APYM}.nc  
#link last run/last day as previous day
#     if ( ( $RUN == 5 ) ||  ( ! -e ${CTM_CONC_1} )) then
        set YYYYMMDDb = `date -ud "${DATE} -1 day" +%Y%m%d`

        foreach it ( `seq 0 ${NDAYS}` )
          set YMD = `date -ud "${YYYYMMDDb} +$it day" +%Y%m%d`  
          set out_ym = /nas1/cmaqruns/2019base/data/output_CCTM_v53_gcc_${APYM}
          set src=`ls $out_ym/CCTM_ACONC*${YMD}_${GRID_NAM0}_${CAS}.nc |head -n1`
          if  ( ! -e $src && $RUN == 12 ) then
            set T=CCTM_ACONC_v53_gcc_ 
            set next=$(date -ud "${YMD} + 1day" +%Y%m%d)
            set nxym=$(date -ud "2019${MO}01 + 1month" +%y%m)
            set outNym = /nas1/cmaqruns/2019base/data/output_CCTM_v53_gcc_${nxym}
            set nxt=${outNym}_run5/${T}${ym}_run5_${next}_${GRID_NAM0}_${CAS}.nc
            if ( -e $nxt ) then ln -s $nxt $src;endif
          endif
          ln -sf $src $out_ym/${YMD}.tmp
        end 
      #if ( ! -e ${CTM_CONC_1} ) then
        /usr/bin/ncrcat -O $out_ym/20??????.tmp ${CTM_CONC_1} #this will take large of time
        rm $out_ym/20??????.tmp
#     endif
    endif
    setenv MET_BDY_3D_FIN $CMAQ_DATA/mcip/$APPL/$GRID_NAME/METBDY3D_$APPL.nc
 else if ( $BCON_TYPE == profile ) then
    setenv BC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv
    setenv MET_BDY_3D_FIN $CMAQ_DATA/mcip/$APPL/$GRID_NAME/METBDY3D_$APPL.nc
 endif
 setenv BNDY_CONC_1    "$OUTDIR/BCON_${VRSN}_${APPL}_${BCON_TYPE}_${YYYYMMDD}_${GRID_NAME} -v"

# =====================================================================
#> Output File
# =====================================================================
 
#>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

 if ( ! -d "$OUTDIR" ) mkdir -p $OUTDIR

 ls -l $BLD/$EXEC; size $BLD/$EXEC
 #unlimit
 #limit

#> Executable call:
 time $BLD/$EXEC

 exit() 
