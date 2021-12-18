# **CMAQ**綜合空品項目之計算(combine)

## 背景

## 腳本程式說明
### 程式名稱
- [run_bconMM_RR_DM.csh](https://github.com/sinotec2/cmaq_relatives/blob/master/bcon/run_bconMM_RR_DM.csh)
- 修改自[USEAP_CMAQ](https://github.com/USEPA/CMAQ)之[run_combine.csh](https://github.com/USEPA/CMAQ/blob/main/POST/combine/scripts/run_combine.csh)

### 分段說明
- 原腳本說明段

```python
$ cat -n ~/GitHub/cmaq_relatives/combine/run_combMM_R_DM.csh
     1	#! /bin/csh -f
     2	
     3	# ====================== COMBINE_v5.3 Run Script ======================== 
     4	# Usage: run.combine.uncoupled.csh >&! combine_v53_uncoupled.log &                                
     5	#
     6	# To report problems or request help with this script/program:     
     7	#             http://www.epa.gov/cmaq    (EPA CMAQ Website)
     8	#             http://www.cmascenter.org  (CMAS Website)
     9	# ===================================================================  
    10	
    11	# ==================================================================
    12	#> Runtime Environment Options
    13	# ==================================================================
    14	
    15	#> Choose compiler and set up CMAQ environment with correct
    16	#> libraries using config.cmaq. Options: intel | gcc | pgi
    17	 setenv compiler gcc
    18	
    19	#> Set location of CMAQ repo.  This will be used to point to the correct species definition files.
    20	 setenv REPO_HOME  ../CMAQ_Project
    21	 #> Source the config.cmaq file to set the build environment
    22	 source $REPO_HOME/config_cmaq.csh gcc
    23	 setenv CMAQ_HOME $PWD
    24	 setenv CMAQ_DATA  /nas1/cmaqruns/2018base/data
    25	
    26	set MO         = $argv[1]
    27	set RUN        = $argv[2]
    28	set DM         = $argv[3]
    29	
    30	       
    31	#> Set General Parameters for Configuring the Simulation
    32	 set VRSN      = v53               #> Code Version
    33	 set PROC      = mpi               #> serial or mpi
    34	 set MECH      = cb6r3_ae7_aq      #> Mechanism ID
    35	 set APPL      = 18${MO}              #> Application Name (e.g. Gridname)
    36	 set STKCASEE  = 11   
    37	                                                      
    38	#> Define RUNID as any combination of parameters above or others. By default,
    39	#> this information will be collected into this one string, $RUNID, for easy
    40	#> referencing in output binaries and log files as well as in other scripts.
    41	 setenv RUNID  ${VRSN}_${compilerString}_${APPL}
    42	
    43	#> Set the build directory if this was not set above 
    44	#> (this is where the CMAQ executable is located by default).
    45	#if ( ! $?BINDIR ) then
    46	  setenv BINDIR $REPO_HOME/POST/combine/scripts/BLD_combine_${VRSN}_${compilerString}
    47	#endif
    48	
    49	#> Set the name of the executable.
    50	 setenv EXEC combine_${VRSN}.exe
    51	
    52	
    53	#> Set working, input and output directories
    54	if ( $DM == 'd01' ) then
    55	  setenv GRID_NAME  EAsia_81K        
    56	else if ( $DM == 'd02' ) then
    57	  setenv GRID_NAME  sChina_27k        
    58	else if( $DM == 'd04' ) then
    59	  setenv GRID_NAME  TWN_3X3           
    60	else
    61	  echo "Error input d02/d04"
    62	  exit 1
    63	endif
    64	
    65	# setenv GRID_NAME TWN_3X3                 #> check GRIDDESC file for GRID_NAME options
    66	 setenv CCTMOUTDIR ${CMAQ_DATA}/output_CCTM_${RUNID}      #> CCTM Output Directory
    67	 setenv POSTDIR    ${CCTMOUTDIR}/POST                     #> Location where combine file will be written
    68	
    69	  if ( ! -e $POSTDIR ) then
    70		  mkdir $POSTDIR
    71	  endif
    72	
    73	
    74	
    75	# =====================================================================
    76	#> COMBINE Configuration Options
    77	# =====================================================================
    78	
    79	#> Set Start and End Days for looping
    80	 set BEG_DATE = `date -ud "2018-${MO}-15 -1 month" +%Y-%m-%d `
    81	 set END_DATE = `date -ud "2018-${MO}-01 +1 month" +%Y-%m-%d `
    82	#  echo ${APPL}|cut -d'n' -f2
    83	# set MRUN = `echo ${APPL}|cut -d'n' -f2`
    84	 set MRUN = 4 
    85	  @ NDYS = $MRUN * 4
    86	 set START_DATE = `date -ud "${BEG_DATE} +${NDYS}days" +%Y-%m-%d `
    87	 set END_DATE = `date -ud "${START_DATE} +32days" +%Y-%m-%d`
    88	 
    89	#> Set location of species definition files for concentration and deposition species.
    90	 setenv SPEC_CONC $REPO_HOME/POST/combine/scripts/spec_def_files/SpecDef_${MECH}.txt
    91	 setenv SPEC_DEP  $REPO_HOME/POST/combine/scripts/spec_def_files/SpecDef_Dep_${MECH}.txt
    92	
    93	#> Use GENSPEC switch to generate a new specdef file (does not generate output file).
    94	 setenv GENSPEC N
    95	
    96	
    97	# =====================================================================
    98	#> Begin Loop Through Simulation Days to Create ACONC File
    99	# =====================================================================
   100	
   101	#> Set the species definition file for concentration species.
   102	 setenv SPECIES_DEF $SPEC_CONC
   103	 
   104	#> Loop through all days between START_DAY and END_DAY
   105	 set TODAYG = ${START_DATE}
   106	 set TODAYJ = `date -ud "${START_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   107	 set STOP_DAY = `date -ud "${END_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   108	 set I = 0
   109	 while ($TODAYJ <= $STOP_DAY )  #>Compare dates in terms of YYYYJJJ
   110	   @ R = 6 # $I / 4 + 5
   111	   echo 'kuang' $I run$R
   112	   if ( $R > 12 ) exit 0
   113	  #> Retrieve Calendar day Information
   114	   set YYYY = `date -ud "${TODAYG}" +%Y`
   115	   set YY = `date -ud "${TODAYG}" +%y`
   116	   set MM = `date -ud "${TODAYG}" +%m`
   117	   set DD = `date -ud "${TODAYG}" +%d`
   118	   if ( "${STKCASEE}" != "" ) then
   119	     setenv CTM_APPL ${RUNID}_run${R}_$YYYY$MM${DD}_${GRID_NAME}_${STKCASEE}
   120	  else
   121	     setenv CTM_APPL ${RUNID}_$YYYY$MM${DD}_${GRID_NAME}
   122	  endif
   123	  #> for files that are indexed with Julian day:
   124	   #  set YYYYJJJ = `date -ud "${TODAYG}" +%Y%j` 
   125	
   126	  #> Define name of combine output file to save hourly average concentration.
   127	  #> A new file will be created for each month/year.
   128	   setenv OUTFILE ${POSTDIR}/COMBINE_ACONC_${CTM_APPL}.nc
   129	
   130	  #> Define name of input files needed for combine program.
   131	  #> File [1]: CMAQ conc/aconc file
   132	  #> File [2]: MCIP METCRO3D file
   133	  #> File [3]: CMAQ APMDIAG file
   134	  #> File [4]: MCIP METCRO2D file
   135	 setenv METDIR    ${CMAQ_DATA}/mcip/${APPL}_run${R}/${GRID_NAME}            #> Met Output Directory
   136	   setenv INFILE1 $CCTMOUTDIR/CCTM_ACONC_${CTM_APPL}.nc
   137	   setenv INFILE2 $METDIR/METCRO3D_${APPL}_run${R}.nc
   138	   setenv INFILE3 $CCTMOUTDIR/CCTM_APMDIAG_${CTM_APPL}.nc
   139	   setenv INFILE4 $METDIR/METCRO2D_${APPL}_run${R}.nc
   140	
   141	  #> Executable call:
   142	 if ( $RUN == $R) then
   143	   ${BINDIR}/${EXEC}
   144	 endif
   145	
   146	  #> Increment both Gregorian and Julian Days
   147	   set TODAYG = `date -ud "${TODAYG}+1days" +%Y-%m-%d` #> Add a day for tomorrow
   148	   set TODAYJ = `date -ud "${TODAYG}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   149	   @ I = $I + 1 
   150	 end #Loop to the next Simulation Day
   151	
   152	
   153	# =====================================================================
   154	#> Begin Loop Through Simulation Days to Create DEP File
   155	# =====================================================================
   156	
   157	#> Set the species definition file for concentration species.
   158	 setenv SPECIES_DEF $SPEC_DEP
   159	 
   160	#> Loop through all days between START_DAY and END_DAY
   161	 set TODAYG = ${START_DATE}
   162	 set TODAYJ = `date -ud "${START_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   163	 set STOP_DAY = `date -ud "${END_DATE}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   164	 set I = 0
   165	 while ($TODAYJ <= $STOP_DAY )  #>Compare dates in terms of YYYYJJJ
   166	   @ R = 6 #$I / 4 + 5
   167	   echo 'kuang' $I run$R
   168	   if ( $R > 12 ) exit 0
   169	  #> Retrieve Calendar day Information
   170	   set YYYY = `date -ud "${TODAYG}" +%Y`
   171	   set YY = `date -ud "${TODAYG}" +%y`
   172	   set MM = `date -ud "${TODAYG}" +%m`
   173	   set DD = `date -ud "${TODAYG}" +%d`
   174	   if ( "${STKCASEE}" != "" ) then
   175	     setenv CTM_APPL ${RUNID}_run${R}_$YYYY$MM${DD}_${GRID_NAME}_${STKCASEE}
   176	     setenv CTM_APPD ${RUNID}_run${R}_$YYYY${MM}_${GRID_NAME}_${STKCASEE}
   177	  else
   178	     setenv CTM_APPL ${RUNID}_$YYYY$MM$DD
   179	     setenv CTM_APPD ${RUNID}_$YYYY$MM
   180	  endif
   181	  #> for files that are indexed with Julian day:
   182	   #  set YYYYJJJ = `date -ud "${TODAYG}" +%Y%j` 
   183	
   184	  #> Define name of combine output file to save hourly total deposition.
   185	  #> A new file will be created for each month/year.
   186	   setenv OUTFILE ${POSTDIR}/COMBINE_DEP_${CTM_APPD}
   187	  #> Define name of input files needed for combine program.
   188	  #> File [1]: CMAQ DRYDEP file
   189	  #> File [2]: CMAQ WETDEP file
   190	  #> File [3]: MCIP METCRO2D
   191	  #> File [4]: {empty}
   192	   setenv METDIR    ${CMAQ_DATA}/mcip/${APPL}_run${R}/${GRID_NAME}            #> Met Output Directory
   193	   setenv INFILE1 $CCTMOUTDIR/CCTM_DRYDEP_${CTM_APPL}.nc
   194	   setenv INFILE2 $CCTMOUTDIR/CCTM_WETDEP1_${CTM_APPL}.nc
   195	   setenv INFILE3 $METDIR/METCRO2D_${APPL}_run${R}.nc
   196	   setenv INFILE4
   197	
   198	  #> Executable call:
   199	 if ( $RUN == $R) then
   200	   mpirun -np 10 ${BINDIR}/${EXEC}
   201	 endif
   202	
   203	  #> Increment both Gregorian and Julian Days
   204	   set TODAYG = `date -ud "${TODAYG}+1days" +%Y-%m-%d` #> Add a day for tomorrow
   205	   set TODAYJ = `date -ud "${TODAYG}" +%Y%j` #> Convert YYYY-MM-DD to YYYYJJJ
   206	   @ I = $I + 1 
   207	 end #Loop to the next Simulation Day
   208	
   209	 
   210	 exit()
```