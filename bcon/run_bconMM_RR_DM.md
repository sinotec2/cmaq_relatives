# **CMAQ**邊界條件輸入檔案之產生

## 背景

## 腳本程式說明
### 程式名稱
- [run_bconMM_RR_DM.csh]()
- 修改自[USEAP_CMAQ](https://github.com/USEPA/CMAQ)之[run_bcon.csh](https://github.com/USEPA/CMAQ/blob/main/PREP/bcon/scripts/run_bcon.csh)

### 分段說明

```bash
kuang@114-32-164-198 ~/GitHub/cmaq_relatives/bcon
$ cat -n run_bconMM_RR_DM.csh
     1	#!/bin/csh -f
     2	
     3	# ======================= BCONv5.3 Run Script ======================== 
     4	# Usage: run.bcon.csh >&! bcon_v53.log &                                
     5	#
     6	# To report problems or request help with this script/program:        
     7	#             http://www.cmascenter.org
     8	# ==================================================================== 
     9	
    10	# ==================================================================
    11	#> Runtime Environment Options
    12	# ==================================================================
    13	
    14	#> Choose compiler and set up CMAQ environment with correct 
    15	#> libraries using config.cmaq. Options: intel | gcc | pgi
    16	 setenv compiler gcc 
    17	
    18	#> Source the config_cmaq file to set the run environment
    19	# pushd  ${CMAQ_HOME}/../CMAQ_Project
```
- 工作目錄及編譯環境

```bash    
    20	 setenv CMAQ_HOME $PWD
    21	 source /opt/CMAQ_Project/config_cmaq.csh $compiler
    22	 
    23	# popd
    24	
    25	#> Check that CMAQ_DATA is set:
    26	 if ( ! -e $CMAQ_DATA ) then
    27	    echo "   $CMAQ_DATA path does not exist"
    28	    exit 1
    29	 endif
    30	 echo " "; echo " Input data path, CMAQ_DATA set to $CMAQ_DATA"; echo " "
    31	
```
- 讀取引數：2碼月份、批次序(\~12)、範圍序(`d01`/`d02`/`d04`、無`d03`)
  - `CAS`設定為**TEDS**編號，與年代有關，2019附近使用TEDS**11**

```python
    32	#> Set General Parameters for Configuring the Simulation
    33	set APPL_YR    = `echo $CMAQ_HOME|cut -d'/' -f4|cut -c3-4`
    34	set MO         = $argv[1]
    35	set RUN        = $argv[2]
    36	set DM         = $argv[3]
    37	set APYM       = ${APPL_YR}${MO}
    38	set CAS        = 11 #teds11
    39	
```
- 模式版本與應用個案(`APPL`)，設定為**年月**_run**批序**

```python
    40	 set VRSN     = v53                     #> Code Version
    41	 set APPL       = ${APYM}_run${RUN}
```
- 水平網格的設定：詳[mcip]()的設定

```python
    42	#> Horizontal grid definition
    43	if ( $DM == 'd01' ) then
    44	  setenv GRID_NAM0  sChina_81k      # 16-character maximum
    45	  setenv GRID_NAME  EAsia_81K       # 16-character maximum
    46	  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
    47	else if ( $DM == 'd02' ) then
    48	  setenv GRID_NAM0  EAsia_81K         # 16-character maximum
    49	  setenv GRID_NAME  sChina_27k        # 16-character maximum
    50	# set BCTYPE   = profile                 #> Initial conditions type [profile|regrid]
    51	  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
    52	else if( $DM == 'd04' ) then
    53	  setenv GRID_NAM0  sChina_27k      # 16-character maximum
    54	  setenv GRID_NAME  TWN_3X3         # 16-character maximum
    55	  set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
    56	else
    57	  echo "Error input d02/d04"
    58	  exit 1
    59	endif
    60	set BCTYPE   = regrid             #> Initial conditions type [profile|regrid]
    61	
    62	
    63	
```
- 執行檔路徑與名稱

```python
    64	#> Set the build directory:
    65	 set BLD      = /opt/CMAQ_Project/PREP/bcon/scripts/BLD_BCON_${VRSN}_${compilerString}
    66	 set EXEC     = BCON_${VRSN}.exe  
    67	 set EXEC_ID  = bcon
    68	 cat $BLD/BCON_${VRSN}.cfg; echo " "; set echo
    69	
    70	#> Horizontal grid definition 
```
- 網格設定檔案

```python
    71	 setenv GRIDDESC $CMAQ_DATA/mcip/$APPL/$GRID_NAME/GRIDDESC #> grid description file 
```
- `bcon`IO設定

```python
    72	 setenv IOAPI_ISPH 20                     #> GCTP spheroid, use 20 for WRF-based modeling
    73	
    74	#> I/O Controls
    75	 setenv IOAPI_LOG_WRITE F     #> turn on excess WRITE3 logging [ options: T | F ]
    76	 setenv IOAPI_OFFSET_64 YES   #> support large timestep records (>2GB/timestep record) [ options: YES | NO ]
    77	 setenv EXECUTION_ID $EXEC    #> define the model execution id
    78	
    79	# =====================================================================
    80	#> BCON Configuration Options
    81	#
    82	# BCON can be run in one of two modes:                                     
    83	#     1) regrids CMAQ CTM concentration files (BC type = regrid)     
    84	#     2) use default profile inputs (BC type = profile)
    85	# =====================================================================
    86	
    87	 setenv BCON_TYPE ` echo $BCTYPE | tr "[A-Z]" "[a-z]" `
    88	
    89	# =====================================================================
    90	#> Input/Output Directories
    91	# =====================================================================
    92	
```
- `bcon`輸出檔案的路徑

```python
    93	 setenv OUTDIR  $CMAQ_HOME/data/bcon       #> output file directory
```
- 原腳本說明段

```python
    94	
    95	# =====================================================================
    96	#> Input Files
    97	#  
    98	#  Regrid mode (BC = regrid) (includes nested domains, windowed domains,
    99	#                             or general regridded domains)
   100	#     CTM_CONC_1 = the CTM concentration file for the coarse domain          
   101	#     MET_CRO_3D_CRS = the MET_CRO_3D met file for the coarse domain
   102	#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target nested domain
   103	#                                                                            
   104	#  Profile mode (BC type = profile)
   105	#     BC_PROFILE = static/default BC profiles 
   106	#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target domain 
   107	#
   108	# NOTE: SDATE (yyyyddd), STIME (hhmmss) and RUNLEN (hhmmss) are only 
   109	#       relevant to the regrid mode and if they are not set,  
   110	#       these variables will be set from the input MET_BDY_3D_FIN file
   111	# =====================================================================
   112	#> Output File
   113	#     BNDY_CONC_1 = gridded BC file for target domain
   114	# =====================================================================
```
- 批次起始時間的計算
  - 批次時間為**5天**+**1小時**

```python
   115	set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
   116	  @ A = $RUN - 1; @ DD = $A * 4 
   117	  @ B = $RUN + 1; @ DB = $RUN * 4 
   118	set DATE  = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`
   119	set NDAYS = 6
   120	 
```
- 日期的格式轉換

```python
   121	    set YYYYJJJ  = `date -ud "${DATE}" +%Y%j`   #> Convert YYYY-MM-DD to YYYYJJJ
   122	    set YYYYMMDD = `date -ud "${DATE}" +%Y%m%d` #> Convert YYYY-MM-DD to YYYYMMDD
   123	    set YYMMDD   = `date -ud "${DATE}" +%y%m%d` #> Convert YYYY-MM-DD to YYMMDD
   124	
   125	#   setenv SDATE           ${YYYYJJJ}
   126	#   setenv STIME           000000
   127	#   setenv RUNLEN          240000
   128	
```
- `METCRO3D`檔案路徑之設定

```python
   129	 if ( $BCON_TYPE == regrid ) then 
   130	    setenv MET_CRO_3D_CRS $CMAQ_DATA/mcip/$APPL/${GRID_NAM0}/METCRO3D_$APPL.nc
   131	    if ( $DM == 'd01' ) then
```
- `d01`情況：直接使用全球模式模擬結果(見[moz2cmaqH]())

```python
   132	      setenv CTM_CONC_1 $CMAQ_DATA/bcon/ICON_d1_20${APYM}_run${RUN}.nc
   133	    else #if( $DM == 'd02'|| $DM == 'd04' ) then
```
- 其他層級的模擬範圍：使用上層`CCTM_ACONC`模擬結果
  - 但因為`CCTM_ACONC`是逐日儲存的，需要先整合成一個檔案

```python
   134	      setenv CTM_CONC_1 $CMAQ_DATA/bcon/ACONC_d2_20${APYM}.nc  
   135	#link last run/last day as previous day
   136	#     if ( ( $RUN == 5 ) ||  ( ! -e ${CTM_CONC_1} )) then
   137	        set YYYYMMDDb = `date -ud "${DATE} -1 day" +%Y%m%d`
   138	
```
- 會需要比正常天數多一個小時，所以天數要多一天。
  - 可以用[pr_tflag.py]()`確認`nc`檔案的`TFLAG`內容。

```python
   139	        foreach it ( `seq 0 ${NDAYS}` )
   140	          set YMD = `date -ud "${YYYYMMDDb} +$it day" +%Y%m%d`  
   141	          set out_ym = /nas1/cmaqruns/2019base/data/output_CCTM_v53_gcc_${APYM}
   142	          set src=`ls $out_ym/CCTM_ACONC*${YMD}_${GRID_NAM0}_${CAS}.nc |head -n1`
   143	          if  ( ! -e $src && $RUN == 12 ) then
   144	            set T=CCTM_ACONC_v53_gcc_ 
   145	            set next=$(date -ud "${YMD} + 1day" +%Y%m%d)
   146	            set nxym=$(date -ud "2019${MO}01 + 1month" +%y%m)
   147	            set outNym = /nas1/cmaqruns/2019base/data/output_CCTM_v53_gcc_${nxym}
   148	            set nxt=${outNym}_run5/${T}${ym}_run5_${next}_${GRID_NAM0}_${CAS}.nc
   149	            if ( -e $nxt ) then ln -s $nxt $src;endif
   150	          endif
   151	          ln -sf $src $out_ym/${YMD}.tmp
   152	        end 
   153	      #if ( ! -e ${CTM_CONC_1} ) then
```
- 用`ncrcat`將上層濃度檔序列，整合(append along time axis)成一個大檔案

```python
   154	        /usr/bin/ncrcat -O $out_ym/20??????.tmp ${CTM_CONC_1} #this will take large of time
   155	        rm $out_ym/20??????.tmp
   156	#     endif
   157	    endif
```
- `mcip`邊界檔案結果的檔名與路徑

```python
   158	    setenv MET_BDY_3D_FIN $CMAQ_DATA/mcip/$APPL/$GRID_NAME/METBDY3D_$APPL.nc
```
- `profile`的設定方式(沒有用到)

```python
   159	 else if ( $BCON_TYPE == profile ) then
   160	    setenv BC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv
   161	    setenv MET_BDY_3D_FIN $CMAQ_DATA/mcip/$APPL/$GRID_NAME/METBDY3D_$APPL.nc
   162	 endif
```
- `bcon`結果檔名的設定

```python
   163	 setenv BNDY_CONC_1    "$OUTDIR/BCON_${VRSN}_${APPL}_${BCON_TYPE}_${YYYYMMDD}_${GRID_NAME} -v"
```
- 執行程式

```python
   164	
   165	# =====================================================================
   166	#> Output File
   167	# =====================================================================
   168	 
   169	#>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   170	
   171	 if ( ! -d "$OUTDIR" ) mkdir -p $OUTDIR
   172	
   173	 ls -l $BLD/$EXEC; size $BLD/$EXEC
   174	 #unlimit
   175	 #limit
   176	
   177	#> Executable call:
   178	 time $BLD/$EXEC
   179	
   180	 exit() 
```

## 腳本檔案下載
- [github]()

## 參考
