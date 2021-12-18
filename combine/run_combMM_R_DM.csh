#! /bin/csh -f

# ====================== COMBINE_v5.3 Run Script ======================== 
# Usage: run.combine.uncoupled.csh >&! combine_v53_uncoupled.log &                                
#
# To report problems or request help with this script/program:     
#             http://www.epa.gov/cmaq    (EPA CMAQ Website)
#             http://www.cmascenter.org  (CMAS Website)
# ===================================================================  

# ==================================================================
#> Runtime Environment Options
# ==================================================================

#> Choose compiler and set up CMAQ environment with correct
#> libraries using config.cmaq. Options: intel | gcc | pgi
 setenv compiler gcc

#> Set location of CMAQ repo.  This will be used to point to the correct species definition files.
 setenv REPO_HOME  ../CMAQ_Project
 #> Source the config.cmaq file to set the build environment
 source $REPO_HOME/config_cmaq.csh gcc
 setenv CMAQ_HOME $PWD
 setenv CMAQ_DATA  /nas1/cmaqruns/2018base/data

set MO         = $argv[1]
set RUN        = $argv[2]
set DM         = $argv[3]

       
#> Set General Parameters for Configuring the Simulation
 set VRSN      = v53               #> Code Version
 set PROC      = mpi               #> serial or mpi
 set MECH      = cb6r3_ae7_aq      #> Mechanism ID
 set APPL      = 18${MO}              #> Application Name (e.g. Gridname)
 set STKCASEE  = 11   
                                                      
#> Define RUNID as any combination of parameters above or others. By default,
#> this information will be collected into this one string, $RUNID, for easy
#> referencing in output binaries and log files as well as in other scripts.
 setenv RUNID  ${VRSN}_${compilerString}_${APPL}

#> Set the build directory if this was not set above 
#> (this is where the CMAQ executable is located by default).
#if ( ! $?BINDIR ) then
  setenv BINDIR $REPO_HOME/POST/combine/scripts/BLD_combine_${VRSN}_${compilerString}
#endif

#> Set the name of the executable.
 setenv EXEC combine_${VRSN}.exe


#> Set working, input and output directories
if ( $DM == 'd01' ) then
  setenv GRID_NAME  EAsia_81K        
else if ( $DM == 'd02' ) then
  setenv GRID_NAME  sChina_27k        
else if( $DM == 'd04' ) then
  setenv GRID_NAME  TWN_3X3           
else
  echo "Error input d02/d04"
  exit 1
endif

# setenv GRID_NAME TWN_3X3                 #> check GRIDDESC file for GRID_NAME options
 setenv CCTMOUTDIR ${CMAQ_DATA}/output_CCTM_${RUNID}      #> CCTM Output Directory
 setenv POSTDIR    ${CCTMOUTDIR}/POST                     #> Location where combine file will be written

  if ( ! -e $POSTDIR ) then
	  mkdir $POSTDIR
  endif



# =====================================================================
#> COMBINE Configuration Options
# =====================================================================

#> Set Start and End Days for looping
 set BEG_DATE = `date -ud "2018-${MO}-15 -1 month" +%Y-%m-%d `
 set END_DATE = `date -ud "2018-${MO}-01 +1 month" +%Y-%m-%d `
#  echo ${APPL}|cut -d'n' -f2
# set MRUN = `echo ${APPL}|cut -d'n' -f2`
 set MRUN = 4 
  @ NDYS = $MRUN * 4
 set START_DATE = `date -ud "${BEG_DATE} +${NDYS}days" +%Y-%m-%d `
 set END_DATE = `date -ud "${START_DATE} +32days" +%Y-%m-%d`
 
#> Set location of species definition files for concentration and deposition species.
 setenv SPEC_CONC $REPO_HOME/POST/combine/scripts/spec_def_files/SpecDef_${MECH}.txt
 setenv SPEC_DEP  $REPO_HOME/POST/combine/scripts/spec_def_files/SpecDef_Dep_${MECH}.txt

#> Use GENSPEC switch to generate a new specdef file (does not generate output file).
 setenv GENSPEC N


# =====================================================================
#> Begin Loop Through Simulation Days to Create ACONC File
# =====================================================================

#> Set the species definition file for concentration species.
 setenv SPECIES_DEF $SPEC_CONC
 
#> Loop through all days between START_DAY and END_DAY
 set TODAYG = ${START_DATE}
 set TODAYJ = `date -ud "${START_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
 set STOP_DAY = `date -ud "${END_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
 set I = 0
 while ($TODAYJ <= $STOP_DAY )  #>Compare dates in terms of YYYYJJJ
   @ R = 6 # $I / 4 + 5
   echo 'kuang' $I run$R
   if ( $R > 12 ) exit 0
  #> Retrieve Calendar day Information
   set YYYY = `date -ud "${TODAYG}" +%Y`
   set YY = `date -ud "${TODAYG}" +%y`
   set MM = `date -ud "${TODAYG}" +%m`
   set DD = `date -ud "${TODAYG}" +%d`
   if ( "${STKCASEE}" != "" ) then
     setenv CTM_APPL ${RUNID}_run${R}_$YYYY$MM${DD}_${GRID_NAME}_${STKCASEE}
  else
     setenv CTM_APPL ${RUNID}_$YYYY$MM${DD}_${GRID_NAME}
  endif
  #> for files that are indexed with Julian day:
   #  set YYYYJJJ = `date -ud "${TODAYG}" +%Y%j` 

  #> Define name of combine output file to save hourly average concentration.
  #> A new file will be created for each month/year.
   setenv OUTFILE ${POSTDIR}/COMBINE_ACONC_${CTM_APPL}.nc

  #> Define name of input files needed for combine program.
  #> File [1]: CMAQ conc/aconc file
  #> File [2]: MCIP METCRO3D file
  #> File [3]: CMAQ APMDIAG file
  #> File [4]: MCIP METCRO2D file
 setenv METDIR    ${CMAQ_DATA}/mcip/${APPL}_run${R}/${GRID_NAME}            #> Met Output Directory
   setenv INFILE1 $CCTMOUTDIR/CCTM_ACONC_${CTM_APPL}.nc
   setenv INFILE2 $METDIR/METCRO3D_${APPL}_run${R}.nc
   setenv INFILE3 $CCTMOUTDIR/CCTM_APMDIAG_${CTM_APPL}.nc
   setenv INFILE4 $METDIR/METCRO2D_${APPL}_run${R}.nc

  #> Executable call:
 if ( $RUN == $R) then
   ${BINDIR}/${EXEC}
 endif

  #> Increment both Gregorian and Julian Days
   set TODAYG = `date -ud "${TODAYG}+1days" +%Y-%m-%d` #> Add a day for tomorrow
   set TODAYJ = `date -ud "${TODAYG}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   @ I = $I + 1 
 end #Loop to the next Simulation Day


# =====================================================================
#> Begin Loop Through Simulation Days to Create DEP File
# =====================================================================

#> Set the species definition file for concentration species.
 setenv SPECIES_DEF $SPEC_DEP
 
#> Loop through all days between START_DAY and END_DAY
 set TODAYG = ${START_DATE}
 set TODAYJ = `date -ud "${START_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
 set STOP_DAY = `date -ud "${END_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
 set I = 0
 while ($TODAYJ <= $STOP_DAY )  #>Compare dates in terms of YYYYJJJ
   @ R = 6 #$I / 4 + 5
   echo 'kuang' $I run$R
   if ( $R > 12 ) exit 0
  #> Retrieve Calendar day Information
   set YYYY = `date -ud "${TODAYG}" +%Y`
   set YY = `date -ud "${TODAYG}" +%y`
   set MM = `date -ud "${TODAYG}" +%m`
   set DD = `date -ud "${TODAYG}" +%d`
   if ( "${STKCASEE}" != "" ) then
     setenv CTM_APPL ${RUNID}_run${R}_$YYYY$MM${DD}_${GRID_NAME}_${STKCASEE}
     setenv CTM_APPD ${RUNID}_run${R}_$YYYY${MM}_${GRID_NAME}_${STKCASEE}
  else
     setenv CTM_APPL ${RUNID}_$YYYY$MM$DD
     setenv CTM_APPD ${RUNID}_$YYYY$MM
  endif
  #> for files that are indexed with Julian day:
   #  set YYYYJJJ = `date -ud "${TODAYG}" +%Y%j` 

  #> Define name of combine output file to save hourly total deposition.
  #> A new file will be created for each month/year.
   setenv OUTFILE ${POSTDIR}/COMBINE_DEP_${CTM_APPD}
  #> Define name of input files needed for combine program.
  #> File [1]: CMAQ DRYDEP file
  #> File [2]: CMAQ WETDEP file
  #> File [3]: MCIP METCRO2D
  #> File [4]: {empty}
   setenv METDIR    ${CMAQ_DATA}/mcip/${APPL}_run${R}/${GRID_NAME}            #> Met Output Directory
   setenv INFILE1 $CCTMOUTDIR/CCTM_DRYDEP_${CTM_APPL}.nc
   setenv INFILE2 $CCTMOUTDIR/CCTM_WETDEP1_${CTM_APPL}.nc
   setenv INFILE3 $METDIR/METCRO2D_${APPL}_run${R}.nc
   setenv INFILE4

  #> Executable call:
 if ( $RUN == $R) then
   mpirun -np 10 ${BINDIR}/${EXEC}
 endif

  #> Increment both Gregorian and Julian Days
   set TODAYG = `date -ud "${TODAYG}+1days" +%Y-%m-%d` #> Add a day for tomorrow
   set TODAYJ = `date -ud "${TODAYG}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   @ I = $I + 1 
 end #Loop to the next Simulation Day

 
 exit()
