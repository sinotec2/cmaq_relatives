# **mcip**程式執行腳本

## 背景
- **mcip**程式是**WRF**與**CMAQ**程式之間的橋樑，**mcip**程式結果也是許多程式包括`bcon`、`combine`等都會讀取的重要檔案，建構**CMAQ**模式模擬應優先進行**mcip**程式。
- **CMAQ**整體的時間、空間架構、範圍等等，都是在**mcip**腳本中決定，因此如果後續執行模擬發現必須更動模擬的時空範圍，必須回到此處重新設定。
  - 時間範圍：主要發生在雨量等等相關變數的累積特性。建議將**WRF**和**mcip**、**CMAQ**等等的執行批次設定成完全一樣，可以避免很多錯誤。**WRF**或**mcip**程式的結束時間可以更長，但起始時間必須一致。
  - 空間範圍：因為濃度邊界需要一定寬度，因此**mcip**的範圍會比**WRF**略小一些。
- 版本的相依性：**mcip**程式對**WRF**程式的版本有相依性。**CMAQ**對**mcip**程式版本也有相依性。這些程式必須同時更新。


## 腳本程式說明

### 執行方式

### 分段差異說明
- 引數、網格系統、資料與家目錄
   - 為了讓同一個腳本應用在不同月份、不同**批序**(批次序號)、不同模擬範圍，讓腳本可以更換執行的條件。
   - `APPL`個案應用標籤：加上**批序**會更方便與[WRF]()對照。
```python
kuang@114-32-164-198 /Users/cmaqruns/2016base/old_scripts
$ diff ~/GitHub/cmaq_relatives/mcip/run_mcipMM_RR_DM.csh run_mcip.csh
122,144c124,130
< #argv[1]: month in 2 digit, 01~12
< #argv[2]: run 1~12
< #argv[3]:domain: d2 or d4
< source $CMAQ_HOME/../CMAQ_Project/config_cmaq.csh gcc
< set APPL_YR    = `echo $CMAQ_HOME|cut -d'/' -f4|cut -c3-4`
< set MO         = $argv[1]
< set RUN        = $argv[2]
< set DM         = $argv[3]
< set APPL       = $APPL_YR${argv[1]}_run${argv[2]}
< set CoordName  = TWN_PULI          # 16-character maximum
< if ( $DM == 'd00' ) then
<   set GridName   = sChina_81k        # 16-character maximum
< else if ( $DM == 'd01' ) then
<   set GridName   = sChina_81ki       # 16-character maximum
< else if ( $DM == 'd02' ) then
<   set GridName   = sChina_27k        # 16-character maximum
< else if( $DM == 'd04' ) then
<   set GridName   = TWN_3X3           # 16-character maximum
< else
<   echo "Error input d01~d04"
<   exit 1
< endif
< set CMAQ_DATA  = $CMAQ_HOME/data
---
> 
> source $CMAQ_HOME/config_cmaq.csh
> 
> set APPL       = 160702
> set CoordName  = LamCon_40N_97W    # 16-character maximum
> set GridName   = 2016_12SE1        # 16-character maximum
> 
```
-
```python
146,152c132,135
< echo $APPL
< set ApplRun    = `echo ${APPL} | sed -e 's/_/\//g'` #replace _ with /
< echo $ApplRun
< set InMetDir   = $DataPath/wrfout/$ApplRun
< set InGeoDir   = $DataPath/wrfout
< set OutDir     = $DataPath/mcip/$APPL/$GridName
< set ProgDir    = $CMAQ_HOME/../CMAQ_Project/PREP/mcip/src
---
> set InMetDir   = $DataPath/wrf
> set InGeoDir   = $DataPath/wrf
> set OutDir     = $DataPath/mcip/$GridName
> set ProgDir    = $CMAQ_HOME/PREP/mcip/src
154,155d136
< echo 'DataPath='$CMAQ_DATA
< echo 'InMetDir='$InMetDir
176,182c157,159
< set InMetFiles = ( \
<                    $InMetDir/wrfout_${argv[3]}_1 \
<                    $InMetDir/wrfout_${argv[3]}_2 \
<                    $InMetDir/wrfout_${argv[3]}_3 \
<                    $InMetDir/wrfout_${argv[3]}_4 \
<                    $InMetDir/wrfout_${argv[3]}_5 \
<                    $InMetDir/wrfout_${argv[3]}_6 )
---
> set InMetFiles = ( $InMetDir/subset_wrfout_d01_2016-07-01_00:00:00 \
>                    $InMetDir/subset_wrfout_d01_2016-07-02_00:00:00 \
>                    $InMetDir/subset_wrfout_d01_2016-07-03_00:00:00 )
184,185c161,162
< set IfGeo      = "T"
< set InGeoFile  = $InGeoDir/geo_em.${DM}.nc
---
> set IfGeo      = "F"
> set InGeoFile  = $InGeoDir/geo_em_d01.nc
202c179
< set LWOUT   = 1
---
> set LWOUT   = 0
212,217c189,190
< set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
<   @ A = $RUN - 1; @ DD = $A * 4 ; @ ED = $A * 4 + 5
< set START = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`
< set ENDDT = `date -ud "$BEGD +${ED}days" +%Y-%m-%d`
< set MCIP_START = ${START}:01:00.0000  # [UTC]
< set MCIP_END   = ${ENDDT}:00:00.0000  # [UTC]
---
> set MCIP_START = 2016-07-02-00:00:00.0000  # [UTC]
> set MCIP_END   = 2016-07-03-00:00:00.0000  # [UTC]
243c216
< set BTRIM = -1
---
> set BTRIM = 0
260,280d232
< if ( $DM == 'd00' ) then
<   set X0    =   1
<   set Y0    =   1
<   set NCOLS =  57
<   set NROWS =  57
< else if ( $DM == 'd01' ) then
<   set X0    =   3
<   set Y0    =   3
<   set NCOLS =  53
<   set NROWS =  53
< else if ( $DM == 'd02' ) then
<   set X0    =   2
<   set Y0    =   2
<   set NCOLS =  65
<   set NROWS =  65
< else if ( $DM == 'd04' ) then
<   set X0    =   8
<   set Y0    =   8
<   set NCOLS =  83
<   set NROWS = 137
< endif
281a234,237
> set X0    =  13
> set Y0    =  94
> set NCOLS =  89
> set NROWS = 104
300c256
< set WRF_LC_REF_LAT = 23.61
---
> set WRF_LC_REF_LAT = 40.0
475,481d430
< #add by kuang
< setenv IOAPI_CHECK_HEADERS  F
< setenv IOAPI_OFFSET_64      T
< setenv IOAPI_CFMETA YES
< setenv IOAPI_CMAQMETA NONE	
< setenv IOAPI_SMOKEMETA NONE	
< setenv IOAPI_TEXTMETA NONE	
482a432
> setenv IOAPI_CHECK_HEADERS  T
514c464
< mpirun -np 1 $ProgDir/${PROG}.exe
---
> $ProgDir/${PROG}.exe
```

## Reference
- USEPA, **run_mcip.csh**, [github](https://github.com/USEPA/CMAQ/blob/main/PREP/mcip/scripts/run_mcip.csh)
