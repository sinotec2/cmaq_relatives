# **mcip**程式執行腳本

## 背景
- **mcip**程式是**WRF**與**CMAQ**程式之間的橋樑，**mcip**程式結果也是許多程式包括`bcon`、`combine`等都會讀取的重要檔案，建構**CMAQ**模式模擬應優先進行**mcip**程式。
- **CMAQ**整體的時間、空間架構、範圍等等，都是在**mcip**腳本中決定，因此如果後續執行模擬發現必須更動模擬的時空範圍，必須回到此處重新設定。
  - 時間範圍：主要發生在雨量等等相關變數的累積特性。建議將**WRF**和**mcip**、**CMAQ**等等的執行批次設定成完全一樣，可以避免很多錯誤。**WRF**或**mcip**程式的結束時間可以更長，但起始時間必須一致。
  - 空間範圍：因為濃度邊界需要一定寬度，因此**mcip**的範圍會比**WRF**略小一些。
- 版本的相依性：**mcip**程式對**WRF**程式的版本有相依性。**CMAQ**對**mcip**程式版本也有相依性。這些程式必須同時更新。


## 腳本程式說明

### 執行方式
- 以`csh`環境執行腳本，呼叫[run_mcipMM_RR_DM.csh](https://github.com/sinotec2/cmaq_relatives/blob/master/mcip/run_mcipMM_RR_DM.csh)

```bash
foreach M (`seq 1 12`)
   set mon=`printf '%02d' $M`
   foreach DM ( 'd01' 'd02' 'd04')
      foreach RUN (`seq 5 12`)
         cd /data/cmaqruns/2019base
         source run_mcipMM_RR_DM.csh $mon $RUN $DM # ${JOB}_$mon$RUN$DM 1>&2 
      end
   end
end
```

### 分段差異說明
- 引數、網格系統、資料與家目錄
   - 為了讓同一個腳本應用在不同月份、不同**批序**(批次序號)、不同模擬範圍，讓腳本可以更換執行的條件。
   - `APPL`個案應用標籤：加上**批序**會更方便與[WRF](https://sinotec2.github.io/Focus-on-Air-Quality/wind_models/OBSGRID/obsYYMM_run.sh/#%E6%89%B9%E6%AC%A1%E7%9A%84%E5%AE%9A%E7%BE%A9)對照。
   - 此處沒有`d03`的選項，因為`d02`已經足夠產生`d04`的邊界條件。

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
- IO目錄之設定

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
```
- `wrfout`之連結引用
   - 此處沒有使用`wrfout`的全名，而是在`bash`腳本中執行連結(see [ln_YYMM.cs])，因為全月的**WRF**模擬主要是以`bash`腳本控制，有較多的範本可以引用。
   - 使用連結還有一個好處，可以對日期較為自由(事實上`bcon`會比WRF批次多要求**向後**1個小時、`mcip`則會要求**向前**1個小時。)。

```python
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
```
- 是否提供`geo_em`檔案

```python
184,185c161,162
< set IfGeo      = "T"
< set InGeoFile  = $InGeoDir/geo_em.${DM}.nc
---
> set IfGeo      = "F"
> set InGeoFile  = $InGeoDir/geo_em_d01.nc
```
- 是否輸出垂直速度。`CCTM_ACONC`也會輸出一份，其實沒有必要在這個階段輸出。

```python
202c179
< set LWOUT   = 1
---
> set LWOUT   = 0
```
- 起始日期的計算，參考[批次的定義](批次的定義)

```python
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
```
- 手動個別設定邊界內縮網格數，不需要另外再設定`BTRIM`

```python
243c216
< set BTRIM = -1
---
> set BTRIM = 0
```
- 各層網格系統的起始位置、網格數

```python
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
```
- 蘭伯特投影參考緯度：照個案實際值代入

```python
300c256
< set WRF_LC_REF_LAT = 23.61
---
> set WRF_LC_REF_LAT = 40.0
```
- 這段是為避免執行過程的警訊，不影響結果。

```python
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
```
- 執行方式：與編譯方式有關。

```python
514c464
< mpirun -np 1 $ProgDir/${PROG}.exe
---
> $ProgDir/${PROG}.exe
```

### ***Mac***版本日期設定與計算方式之差異 
- ***Mac*** (<)與一般的UNIX(>)有很大的[差異](https://www.cnblogs.com/qwj-sysu/p/5396372.html)，輸入格式`-f`在引數之前設定，日期的加減也是在引數之前。一般(如***centos***)是在引數之後。
- run**批序**之起始日：前月15日

```bash
kuang@114-32-164-198 /Users/cmaqruns/2016base
$ diff mac_mcipMM_RR_DM.csh run_mcipMM_RR_DM.csh
212c212
< set BEGD = `date -v-1m -j -f "%Y-%m-%d" "20${APPL_YR}-${MO}-15" +%Y-%m-%d`
---
> set BEGD = `date -ud "20${APPL_YR}-${MO}-15 +-1months" +%Y-%m-%d`
```
- `BEGD`後的`DD`日與`ED`日

```python
214,215c214,215
< set START = `date -v+${DD}d -j -f "%Y-%m-%d" "${BEGD}" +%Y-%m-%d` #> Convert YYYY-MM-DD to YYYYMMDD
< set ENDDT = `date -v+${ED}d -j -f "%Y-%m-%d" "${BEGD}" +%Y-%m-%d` #> Convert YYYY-MM-DD to YYYYMMDD
---
> set START = `date -ud "$BEGD +${DD}days" +%Y-%m-%d`
> set ENDDT = `date -ud "$BEGD +${ED}days" +%Y-%m-%d`
```

### mcip轉檔結果的確認
- `mcip`的結果都是`m3.nc`格式檔案，可以用[VERDI](ttps://github.com/CEMPD/VERDI/blob/master/doc/User_Manual/VERDI_ch01.md)或[MeteoInfo]((http://meteothink.org/))開啟
- 使用[pr_tflag.py](https://sinotec2.github.io/Focus-on-Air-Quality/utilities/netCDF/pr_tflag/)亦能快速檢查結果檔案的時間標籤

## 腳本下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/mcip/run_mcipMM_RR_DM.csh)

## Reference
- USEPA, **run_mcip.csh**, [github](https://github.com/USEPA/CMAQ/blob/main/PREP/mcip/scripts/run_mcip.csh)
- lizadams, **Visualization Environment for Rich Data Interpretation (VERDI): User’s Manual**, [github](https://github.com/CEMPD/VERDI/blob/master/doc/User_Manual/VERDI_ch01.md), August 03, 2021
