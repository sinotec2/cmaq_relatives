# **mcip**程式執行腳本

## 背景
- **mcip**程式是**WRF**與**CMAQ**程式之間的橋樑，**mcip**程式結果也是許多程式包括`bcon`、`combine`等都會讀取的重要檔案，建構**CMAQ**模式模擬應優先進行**mcip**程式。
- **CMAQ**整體的時間、空間架構、範圍等等，都是在**mcip**腳本中決定，因此如果後續執行模擬發現必須更動模擬的時空範圍，必須回到此處重新設定。
  - 時間範圍：主要發生在雨量等等相關變數的累積特性。建議將**WRF**和**mcip**、**CMAQ**等等的執行批次設定成完全一樣，可以避免很多錯誤。**WRF**或**mcip**程式的結束時間可以更長，但起始時間必須一致。
  - 空間範圍：因為濃度邊界需要一定寬度，因此**mcip**的範圍會比**WRF**略小一些。
- 版本的相依性：**mcip**程式對**WRF**程式的版本有相依性。**CMAQ**對**mcip**程式版本也有相依性。這些程式必須同時更新。


## 腳本程式說明

### 執行方式

### 分段說明
- 原腳本說明段(無更動)

```python
     1	#!/bin/csh -f 
     2	
     3	#------------------------------------------------------------------------------#
     4	#  The Community Multiscale Air Quality (CMAQ) system software is in           #
     5	#  continuous development by various groups and is based on information        #
...
   121	#-----------------------------------------------------------------------
```
- 

```python
   122	#argv[1]: month in 2 digit, 01~12
   123	#argv[2]: run 1~12
   124	#argv[3]:domain: d2 or d4
   125	source $CMAQ_HOME/../CMAQ_Project/config_cmaq.csh gcc
   126	set APPL_YR    = `echo $CMAQ_HOME|cut -d'/' -f4|cut -c3-4`
   127	set MO         = $argv[1]
   128	set RUN        = $argv[2]
   129	set DM         = $argv[3]
   130	set APPL       = $APPL_YR${argv[1]}_run${argv[2]}
   131	set CoordName  = TWN_PULI          # 16-character maximum
   132	if ( $DM == 'd00' ) then
   133	  set GridName   = sChina_81k        # 16-character maximum
   134	else if ( $DM == 'd01' ) then
   135	  set GridName   = sChina_81ki       # 16-character maximum
   136	else if ( $DM == 'd02' ) then
   137	  set GridName   = sChina_27k        # 16-character maximum
   138	else if( $DM == 'd04' ) then
   139	  set GridName   = TWN_3X3           # 16-character maximum
   140	else
   141	  echo "Error input d01~d04"
   142	  exit 1
   143	endif
   144	set CMAQ_DATA  = $CMAQ_HOME/data
   145	set DataPath   = $CMAQ_DATA
   146	echo $APPL
   147	set ApplRun    = `echo ${APPL} | sed -e 's/_/\//g'` #replace _ with /
   148	echo $ApplRun
   149	set InMetDir   = $DataPath/wrfout/$ApplRun
   150	set InGeoDir   = $DataPath/wrfout
   151	set OutDir     = $DataPath/mcip/$APPL/$GridName
   152	set ProgDir    = $CMAQ_HOME/../CMAQ_Project/PREP/mcip/src
   153	set WorkDir    = $OutDir
   154	echo 'DataPath='$CMAQ_DATA
   155	echo 'InMetDir='$InMetDir
   156	
```
- 

```python
   157	#-----------------------------------------------------------------------
   158	# Set name(s) of input meteorology file(s)
   159	#
   160	#   File name(s) must be set inside parentheses since "InMetFiles" is
   161	#   a C-shell script array.  Multiple file names should be space-
   162	#   delimited.  Additional lines can be used when separated by a
   163	#   back-slash (\) continuation marker.  The file names can be as
   164	#   they appear on your system; MCIP will link the files in by a
   165	#   Fortran unit number and the explicit name via a namelist.  The
   166	#   files must be listed in chronological order.  The maximum number
   167	#   of input meteorology files must be less than or equal to the number
   168	#   in MAX_MM in file_mod.F (default is 367).
   169	#
   170	#   Example:
   171	#     set InMetFiles = ( $InMetDir/wrfout_d01_date1 \
   172	#                        $InMetDir/wrfout_d01_date2 )
   173	#
   174	#-----------------------------------------------------------------------
   175	
   176	set InMetFiles = ( \
   177	                   $InMetDir/wrfout_${argv[3]}_1 \
   178	                   $InMetDir/wrfout_${argv[3]}_2 \
   179	                   $InMetDir/wrfout_${argv[3]}_3 \
   180	                   $InMetDir/wrfout_${argv[3]}_4 \
   181	                   $InMetDir/wrfout_${argv[3]}_5 \
   182	                   $InMetDir/wrfout_${argv[3]}_6 )
   183	
   184	set IfGeo      = "T"
   185	set InGeoFile  = $InGeoDir/geo_em.${DM}.nc
   186	
   187	#-----------------------------------------------------------------------
   188	# Set user control options.
   189	#
   190	#   LPV:     0 = Do not compute and output potential vorticity
   191	#            1 = Compute and output potential vorticity
   192	#
   193	#   LWOUT:   0 = Do not output vertical velocity
   194	#            1 = Output vertical velocity
   195	#
   196	#   LUVBOUT: 0 = Do not output u- and v-component winds on B-grid
   197	#            1 = Output u- and v-component winds on B-grid (cell corner)
   198	#                in addition to the C-grid (cell face) output
   199	#-----------------------------------------------------------------------
   200	
   201	set LPV     = 0
   202	set LWOUT   = 1
   203	set LUVBOUT = 1
   204	
   205	#-----------------------------------------------------------------------
   206	# Set run start and end date.  (YYYY-MO-DD-HH:MI:SS.SSSS)
   207	#   MCIP_START:  First date and time to be output [UTC]
   208	#   MCIP_END:    Last date and time to be output  [UTC]
   209	#   INTVL:       Frequency of output [minutes]
   210	#-----------------------------------------------------------------------
   211	
   212	set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
   213	  @ A = $RUN - 1; @ DD = $A * 4 ; @ ED = $A * 4 + 5
   214	set START = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`
   215	set ENDDT = `date -ud "$BEGD +${ED}days" +%Y-%m-%d`
   216	set MCIP_START = ${START}:01:00.0000  # [UTC]
   217	set MCIP_END   = ${ENDDT}:00:00.0000  # [UTC]
   218	
   219	set INTVL      = 60 # [min]
   220	
```
- 

```python
   221	#-----------------------------------------------------------------------
   222	# Choose output format.
   223	#   1 = Models-3 I/O API
   224	#   2 = netCDF
   225	#-----------------------------------------------------------------------
   226	
   227	set IOFORM = 1
   228	
   229	#-----------------------------------------------------------------------
   230	# Set number of meteorology "boundary" points to remove on each of four
   231	# horizontal sides of MCIP domain.  This affects the output MCIP domain
   232	# dimensions by reducing meteorology domain by 2*BTRIM + 2*NTHIK + 1,
   233	# where NTHIK is the lateral boundary thickness (in BDY files), and the
   234	# extra point reflects conversion from grid points (dot points) to grid
   235	# cells (cross points).  Setting BTRIM = 0 will use maximum of input
   236	# meteorology.  To remove MM5 lateral boundaries, set BTRIM = 5.
   237	#
   238	# *** If windowing a specific subset domain of input meteorology, set
   239	#     BTRIM = -1, and BTRIM will be ignored in favor of specific window
   240	#     information in X0, Y0, NCOLS, and NROWS.
   241	#-----------------------------------------------------------------------
   242	
   243	set BTRIM = -1
   244	
   245	#-----------------------------------------------------------------------
   246	# Define MCIP subset domain.  (Only used if BTRIM = -1.  Otherwise,
   247	# the following variables will be set automatically from BTRIM and
   248	# size of input meteorology fields.)
   249	#   X0:     X-coordinate of lower-left corner of full MCIP "X" domain
   250	#           (including MCIP lateral boundary) based on input MM5 domain.
   251	#           X0 refers to the east-west dimension.  Minimum value is 1.
   252	#   Y0:     Y-coordinate of lower-left corner of full MCIP "X" domain
   253	#           (including MCIP lateral boundary) based on input MM5 domain.
   254	#           Y0 refers to the north-south dimension.  Minimum value is 1.
   255	#   NCOLS:  Number of columns in output MCIP domain (excluding MCIP
   256	#           lateral boundaries).
   257	#   NROWS:  Number of rows in output MCIP domain (excluding MCIP
   258	#           lateral boundaries).
   259	#-----------------------------------------------------------------------
   260	if ( $DM == 'd00' ) then
   261	  set X0    =   1
   262	  set Y0    =   1
   263	  set NCOLS =  57
   264	  set NROWS =  57
   265	else if ( $DM == 'd01' ) then
   266	  set X0    =   3
   267	  set Y0    =   3
   268	  set NCOLS =  53
   269	  set NROWS =  53
   270	else if ( $DM == 'd02' ) then
   271	  set X0    =   2
   272	  set Y0    =   2
   273	  set NCOLS =  65
   274	  set NROWS =  65
   275	else if ( $DM == 'd04' ) then
   276	  set X0    =   8
   277	  set Y0    =   8
   278	  set NCOLS =  83
   279	  set NROWS = 137
   280	endif
   281	
   282	
```
- 

```python
   283	#-----------------------------------------------------------------------
   284	# Set coordinates for cell for diagnostic prints on output domain.
   285	# If coordinate is set to 0, domain center cell will be used.
   286	#-----------------------------------------------------------------------
   287	
   288	set LPRT_COL = 0
   289	set LPRT_ROW = 0
   290	
   291	#-----------------------------------------------------------------------
   292	# Optional:  Set WRF Lambert conformal reference latitude.
   293	#            (Handy for matching WRF grids to existing MM5 grids.)
   294	#            If not set, MCIP will use average of two true latitudes.
   295	# To "unset" this variable, set the script variable to "-999.0".
   296	# Alternatively, if the script variable is removed here, remove it
   297	# from the setting of the namelist (toward the end of the script).
   298	#-----------------------------------------------------------------------
   299	
```
- 

```python
   300	set WRF_LC_REF_LAT = 23.61
```
- 

```python
   301	
   302	#=======================================================================
   303	#=======================================================================
   304	# Set up and run MCIP.
   305	#   Should not need to change anything below here.
   306	#=======================================================================
   307	#=======================================================================
   308	
   309	set PROG = mcip
   310	
   311	date
   312	
   313	#-----------------------------------------------------------------------
   314	# Make sure directories exist.
   315	#-----------------------------------------------------------------------
   316	
   317	if ( ! -d $InMetDir ) then
   318	  echo "No such input directory $InMetDir"
   319	  exit 1
   320	endif
   321	
   322	if ( ! -d $OutDir ) then
   323	  echo "No such output directory...will try to create one"
   324	  mkdir -p $OutDir
   325	  if ( $status != 0 ) then
   326	    echo "Failed to make output directory, $OutDir"
   327	    exit 1
   328	  endif
   329	endif
   330	
   331	if ( ! -d $ProgDir ) then
   332	  echo "No such program directory $ProgDir"
   333	  exit 1
   334	endif
   335	
   336	#-----------------------------------------------------------------------
   337	# Make sure the input files exist.
   338	#-----------------------------------------------------------------------
   339	
   340	if ( $IfGeo == "T" ) then
   341	  if ( ! -f $InGeoFile ) then
   342	    echo "No such input file $InGeoFile"
   343	    exit 1
   344	  endif
   345	endif
   346	
   347	foreach fil ( $InMetFiles )
   348	  if ( ! -f $fil ) then
   349	    echo "No such input file $fil"
   350	    exit 1
   351	  endif
   352	end
   353	
   354	#-----------------------------------------------------------------------
   355	# Make sure the executable exists.
   356	#-----------------------------------------------------------------------
   357	
   358	if ( ! -f $ProgDir/${PROG}.exe ) then
   359	  echo "Could not find ${PROG}.exe"
   360	  exit 1
   361	endif
   362	
   363	#-----------------------------------------------------------------------
   364	# Create a work directory for this job.
   365	#-----------------------------------------------------------------------
   366	
   367	if ( ! -d $WorkDir ) then
   368	  mkdir -p $WorkDir
   369	  if ( $status != 0 ) then
   370	    echo "Failed to make work directory, $WorkDir"
   371	    exit 1
   372	  endif
   373	endif
   374	
   375	cd $WorkDir
   376	
   377	#-----------------------------------------------------------------------
   378	# Set up script variables for input files.
   379	#-----------------------------------------------------------------------
   380	
   381	if ( $IfGeo == "T" ) then
   382	  if ( -f $InGeoFile ) then
   383	    set InGeo = $InGeoFile
   384	  else
   385	    set InGeo = "no_file"
   386	  endif
   387	else
   388	  set InGeo = "no_file"
   389	endif
   390	
   391	set FILE_GD  = $OutDir/GRIDDESC
   392	
   393	#-----------------------------------------------------------------------
   394	# Create namelist with user definitions.
   395	#-----------------------------------------------------------------------
   396	
   397	set MACHTYPE = `uname`
   398	if ( ( $MACHTYPE == "AIX" ) || ( $MACHTYPE == "Darwin" ) ) then
   399	  set Marker = "/"
   400	else
   401	  set Marker = "&END"
   402	endif
   403	
   404	cat > $WorkDir/namelist.${PROG} << !
   405	
   406	 &FILENAMES
   407	  file_gd    = "$FILE_GD"
   408	  file_mm    = "$InMetFiles[1]",
   409	!
   410	
   411	if ( $#InMetFiles > 1 ) then
   412	  @ nn = 2
   413	  while ( $nn <= $#InMetFiles )
   414	    cat >> $WorkDir/namelist.${PROG} << !
   415	               "$InMetFiles[$nn]",
   416	!
   417	    @ nn ++
   418	  end
   419	endif
   420	
   421	if ( $IfGeo == "T" ) then
   422	cat >> $WorkDir/namelist.${PROG} << !
   423	  file_geo   = "$InGeo"
   424	!
   425	endif
   426	
   427	cat >> $WorkDir/namelist.${PROG} << !
   428	  ioform     =  $IOFORM
   429	 $Marker
   430	
   431	 &USERDEFS
   432	  lpv        =  $LPV
   433	  lwout      =  $LWOUT
   434	  luvbout    =  $LUVBOUT
   435	  mcip_start = "$MCIP_START"
   436	  mcip_end   = "$MCIP_END"
   437	  intvl      =  $INTVL
   438	  coordnam   = "$CoordName"
   439	  grdnam     = "$GridName"
   440	  btrim      =  $BTRIM
   441	  lprt_col   =  $LPRT_COL
   442	  lprt_row   =  $LPRT_ROW
   443	  wrf_lc_ref_lat = $WRF_LC_REF_LAT
   444	 $Marker
   445	
   446	 &WINDOWDEFS
   447	  x0         =  $X0
   448	  y0         =  $Y0
   449	  ncolsin    =  $NCOLS
   450	  nrowsin    =  $NROWS
   451	 $Marker
   452	
   453	!
   454	
   455	#-----------------------------------------------------------------------
   456	# Set links to FORTRAN units.
   457	#-----------------------------------------------------------------------
   458	
   459	rm fort.*
   460	if ( -f $FILE_GD ) rm -f $FILE_GD
   461	
   462	ln -s $FILE_GD                   fort.4
   463	ln -s $WorkDir/namelist.${PROG}  fort.8
   464	
   465	set NUMFIL = 0
   466	foreach fil ( $InMetFiles )
   467	  @ NN = $NUMFIL + 10
   468	  ln -s $fil fort.$NN
   469	  @ NUMFIL ++
   470	end
   471	
   472	#-----------------------------------------------------------------------
   473	# Set output file names and other miscellaneous environment variables.
   474	#-----------------------------------------------------------------------
   475	#add by kuang
   476	setenv IOAPI_CHECK_HEADERS  F
   477	setenv IOAPI_OFFSET_64      T
   478	setenv IOAPI_CFMETA YES
   479	setenv IOAPI_CMAQMETA NONE	
   480	setenv IOAPI_SMOKEMETA NONE	
   481	setenv IOAPI_TEXTMETA NONE	
   482	
   483	setenv EXECUTION_ID         $PROG
   484	
   485	setenv GRID_BDY_2D          $OutDir/GRIDBDY2D_${APPL}.nc
   486	setenv GRID_CRO_2D          $OutDir/GRIDCRO2D_${APPL}.nc
   487	setenv GRID_DOT_2D          $OutDir/GRIDDOT2D_${APPL}.nc
   488	setenv MET_BDY_3D           $OutDir/METBDY3D_${APPL}.nc
   489	setenv MET_CRO_2D           $OutDir/METCRO2D_${APPL}.nc
   490	setenv MET_CRO_3D           $OutDir/METCRO3D_${APPL}.nc
   491	setenv MET_DOT_3D           $OutDir/METDOT3D_${APPL}.nc
   492	setenv LUFRAC_CRO           $OutDir/LUFRAC_CRO_${APPL}.nc
   493	setenv SOI_CRO              $OutDir/SOI_CRO_${APPL}.nc
   494	setenv MOSAIC_CRO           $OutDir/MOSAIC_CRO_${APPL}.nc
   495	
   496	if ( -f $GRID_BDY_2D ) rm -f $GRID_BDY_2D
   497	if ( -f $GRID_CRO_2D ) rm -f $GRID_CRO_2D
   498	if ( -f $GRID_DOT_2D ) rm -f $GRID_DOT_2D
   499	if ( -f $MET_BDY_3D  ) rm -f $MET_BDY_3D
   500	if ( -f $MET_CRO_2D  ) rm -f $MET_CRO_2D
   501	if ( -f $MET_CRO_3D  ) rm -f $MET_CRO_3D
   502	if ( -f $MET_DOT_3D  ) rm -f $MET_DOT_3D
   503	if ( -f $LUFRAC_CRO  ) rm -f $LUFRAC_CRO
   504	if ( -f $SOI_CRO     ) rm -f $SOI_CRO
   505	if ( -f $MOSAIC_CRO  ) rm -f $MOSAIC_CRO
   506	
   507	if ( -f $OutDir/mcip.nc      ) rm -f $OutDir/mcip.nc
   508	if ( -f $OutDir/mcip_bdy.nc  ) rm -f $OutDir/mcip_bdy.nc
   509	
   510	#-----------------------------------------------------------------------
   511	# Execute MCIP.
   512	#-----------------------------------------------------------------------
   513	
   514	mpirun -np 1 $ProgDir/${PROG}.exe
   515	
   516	if ( $status == 0 ) then
   517	  rm fort.*
   518	  exit 0
   519	else
   520	  echo "Error running $PROG"
   521	  exit 1
   522	endif
```

## Reference
- USEPA, **run_mcip.csh**, [github](https://github.com/USEPA/CMAQ/blob/main/PREP/mcip/scripts/run_mcip.csh)
