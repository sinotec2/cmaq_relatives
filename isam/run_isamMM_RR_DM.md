# 執行**CMAQ-ISAM**

## 背景
- 與CAMx-OSAT/PSAT類似，**Integrated Source Apportionment Method (ISAM)**是**CMAQ**內設之污染來源分配模式，可以針對模擬範圍內的污染區域、類別進行追蹤計算，分別輸出該分區(分類)之污染濃度，以進行來源追蹤，以便完成：
1. 敏感性分析
1. 排放量設定方式修正、校正
1. 地形遮蔽、滯留現象之探討研究
1. 污染防制、減量、空氣品質管理
相關研究發表不少，詳見下列參考文獻。使用範例、手冊等請參考[官網](https://www.epa.gov/cmaq/integrated-source-apportionment-method-cmaq-isam)。

- 執行**CMAQ-ISAM**的腳本與執行`CCTM`是同一個。然實際全年、全月的模擬還有許多設定需要修改。
- **CMAQ-ISAM**不必特別處理排放量，EPA設計讓所有的排放開關控制對照，都些在`EmissCtrl`檔案內，藉該檔案來控制特定地區污染排放的開啟或關閉。


## `EmissCtrl`檔案之地區控制(`RegionsRegistry`)
- 這個namelist的目的原本是給程式控制排放量的。為了分區進行管制，因此會需要設定(**CMAQ**程式內應用)分區的名稱、[網格遮罩]()`gridmask`檔案與該檔案內定義的名稱之對照關係。各變數說明如下：
  - `ISAM_REGIONS`：檔案標籤，就是在`csh`中所指定的[gridmask遮罩檔案]()。
  - `Region Label`：在nml檔案內應用的分區名稱
  - `Variable on File`：在gridmask檔案內的分區名稱。
- 中國大陸的[空氣質量預報](http://big5.mee.gov.cn/gate/big5/www.mee.gov.cn/hjzl/dqhj/kqzlyb/)分區為例  

```python
!------------------------------------------------------------------------------!
&RegionsRegistry
!| Region Label   | File_Label  | Variable on File
 RGN_NML  =
  'AQFZ0', 'ISAM_REGIONS','AQFZ0',
  'AQFZ1', 'ISAM_REGIONS','AQFZ1',
  'AQFZ2', 'ISAM_REGIONS','AQFZ2',
  'AQFZ3', 'ISAM_REGIONS','AQFZ3',
  'AQFZ4', 'ISAM_REGIONS','AQFZ4',
  'AQFZ5', 'ISAM_REGIONS','AQFZ5',
  'AQFZ6', 'ISAM_REGIONS','AQFZ6',
  'AQFZ7', 'ISAM_REGIONS','AQFZ7',
  'ALL',   'ISAM_REGIONS','ALL',
  'EVERYWHERE'  ,'N/A'        ,'N/A',
/
```
- 臺灣地區縣市代碼為例

```python
!------------------------------------------------------------------------------!
&RegionsRegistry
!| Region Label   | File_Label  | Variable on File
 RGN_NML  =
  'CNTY_01', 'ISAM_REGIONS','CNTY_01',
  'CNTY_02', 'ISAM_REGIONS','CNTY_02',
  'CNTY_11', 'ISAM_REGIONS','CNTY_11',
  'CNTY_12', 'ISAM_REGIONS','CNTY_12',
  'CNTY_17', 'ISAM_REGIONS','CNTY_17',
  'CNTY_21', 'ISAM_REGIONS','CNTY_21',
  'CNTY_22', 'ISAM_REGIONS','CNTY_22',
  'CNTY_31', 'ISAM_REGIONS','CNTY_31',
  'CNTY_32', 'ISAM_REGIONS','CNTY_32',
  'CNTY_33', 'ISAM_REGIONS','CNTY_33',
  'CNTY_34', 'ISAM_REGIONS','CNTY_34',
  'CNTY_35', 'ISAM_REGIONS','CNTY_35',
  'CNTY_36', 'ISAM_REGIONS','CNTY_36',
  'CNTY_37', 'ISAM_REGIONS','CNTY_37',
  'CNTY_38', 'ISAM_REGIONS','CNTY_38',
  'CNTY_39', 'ISAM_REGIONS','CNTY_39',
  'CNTY_40', 'ISAM_REGIONS','CNTY_40',
  'CNTY_41', 'ISAM_REGIONS','CNTY_41',
  'CNTY_42', 'ISAM_REGIONS','CNTY_42',
  'CNTY_43', 'ISAM_REGIONS','CNTY_43',
  'CNTY_44', 'ISAM_REGIONS','CNTY_44',
  'CNTY_45', 'ISAM_REGIONS','CNTY_45',
  'CNTY_46', 'ISAM_REGIONS','CNTY_46',
  'WATER',   'ISAM_REGIONS','CNTY_53',
  'ALL',   'ISAM_REGIONS','ALL',
  'EVERYWHERE'  ,'N/A'        ,'N/A',
/
```

## isam_control.txt ($SA_IOLIST)
- 此檔案是**CMAQ-ISAM**執行過程中，指定排放**類別**及**地區**整合控制的檔案。詳細說明可以參考[ISAM Tutorial](https://github.com/USEPA/CMAQ/blob/main/DOCS/Users_Guide/Tutorials/CMAQ_UG_tutorial_benchmark.md)
- **地區**控制(`RegionsRegistry`)詳見前述
- `isam_control.txt`檔案範例如下
  * 驚嘆號`!`後為註解
  * `TAG CLASSES`：欲追蹤的空品項目。選項有**9項**。不是所有的物質都納入**CMAQ_ISAM**計算。(**PM10**似乎就不在其列)
  * `TAG NAME`：排放標籤，在`CCTM_SA_*`檔案中的變數名稱中會出現，詳[ISAM結果檔案之讀取(PM10)](https://sinotec2.github.io/Focus-on-Air-Quality/GridModels/ISAM/SA_PM10)背景說明。
  * `REGION(S)`：可以是一**地區**(前述`Region Label`的值)、地區的**序列**(以`,`隔開)、或**所有**地區(`EVERYWHERE`，詳前述`RGN_NML`最末行)
  * `EMIS STREAM(S)`：即為[run_cctm.csh]()檔案中的`GR_EMIS_LAB_001`、`STK_EMIS_LAB_001`等等
  * `ENDLIST eof`： **E**nd **O**f **F**ile

```bash
[kuang@DEVP 2018base]$ cat isam_controlFWS.txt
cat isam_controlFWS.txt
!!! CMAQ-ISAM tag definition control file
!!!   (lines begining with !!! - three exclamaition marks - are ignored by the text parser)
!!!
!!!   Example file provided with CMAQ v5.3 release
!!!   05 June 2019: Sergey L. Napelenok
!!!
!!!
!!! The following line defines the tag classes to track for the simulation. Species in NITRATE and VOC classes depend on the
!!! the chemical mechanism used. The below definitions apply for the cb6r3_ae7_aq mechanism.
!!!   Choose any/all from the list of nine:  SULFATE, NITRATE, AMMONIUM, EC, OC, VOC, PM25_IONS, CO, OZONE
!!!   SULFATE   - ASO4J, ASO4I, SO2, SULF, SULRXN
!!!   NITRATE   - ANO3J, ANO3I, HNO3, ANO3J, ANO3I, HNO3, NO, NO2, NO3, HONO, N2O5, PNA, PAN, PANX, NTR1, NTR2, INTR, CLNO2, CLNO3
!!!   AMMONIUM  - ANH4J, ANH4I, NH3
!!!   EC        - AECJ, AECI
!!!   OC        - APOCI, APOCJ, APNCOMI, APNCOMJ
!!!   VOC       - 22 species, check CCTM/src/isam/SA_DEFN.F for species names
!!!   PM25_IONS - ACLI/J,ANAI/J,AMGJ,AKJ,ACAJ,AFEJ,AALJ,ASIJ,ATIJ,AMNJ,AOTHRI/J
!!!   CO        - CO
!!!   OZONE     - all NITRATE species + all VOC species

TAG CLASSES     |SULFATE, NITRATE, AMMONIUM, EC, OC, VOC, PM25_IONS, CO, OZONE

!!! The following are source definition text blocks in the format:
!!!   TAG NAME        |Three character text string
!!!   REGION(S)       |Keyword EVERYWHERE or variable names from the region file (multiple regions need to be comma delimited)
!!!   FILENAME(S)     |Emissions labels (multiple labels need to be comma delimited)


TAG NAME        |GR13
REGION(S)       |AQFZ2
EMIS STREAM(S)  |GRIDDED_INDS,GRIDDED_AREA
TAG NAME        |GR24
REGION(S)       |AQFZ2
EMIS STREAM(S)  |GRIDDED_LINE,GRIDDED_AVIN
TAG NAME        |PTA
REGION(S)       |AQFZ2
EMIS STREAM(S)  |POINT_ALL

ENDLIST eof
```
## CMAQ-ISAM選項範例

**ISAM相關變數與範例**

|**Variable** | **Settings** | **Description**|**Value and Why**|
|-------|----------|------------|----|
|CTM_ISAM|Y/N|Set this to Y to enable ISAM|`Y`(如選Y，$BLD及$EXEC等須確實有打開編譯選項)|
|SA_IOLIST|path/filename|Provide the location of the ISAM control file (discussed below)|`${WORKDIR}/isam_control${BSN}.txt`(直接指向不同**地區**的設定檔，須預先產生)|
|ISAM_BLEV_ELEV|" MINVALUE MAX VALUE "|LAYER range for the instantaneous ISAM output concentrations|`" 1 1"`(只輸出地面)|
|AISAM_BLEV_ELEV|" MINVALUE MAX VALUE "|LAYER range for the average ISAM output concentrations|`" 1 1"`(只輸出地面)|
|ISAM_NEW_START|Y/N|set Y for a new simulation and N for continuing from a previous day's outputs|run5為`Y`，其餘為`N`|
|ISAM_PREVDAY|path/filename|Provide the location of the previous day's ISAM restart file|`"$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc"`(將前一批次最末天結果連結過來)|
|SA_ACONC_1|path/filename|ISAM output for average apportioned concentrations|`"$OUTDIR/CCTM_SA_ACONC_${CTM_APPL}_${BSN}.nc -v"`|
|SA_CONC_1|path/filename|ISAM output for instanteneous apportioned concentrations|`"$OUTDIR/CCTM_SA_CONC_${CTM_APPL}_${BSN}.nc -v"`|
|SA_DD_1|path/filename|ISAM output for apportioned dry deposition|`"$OUTDIR/CCTM_SA_DRYDEP_${CTM_APPL}_${BSN}.nc -v"`|
|SA_WD_1|path/filename|ISAM output for apportioned wet deposition|`"$OUTDIR/CCTM_SA_WETDEP_${CTM_APPL}_${BSN}.nc -v"`|
|SA_CGRID_1|path/filename|ISAM output for a restart file to continue the simulation further in time|`"$OUTDIR/CCTM_SA_CGRID_${CTM_APPL}_${BSN}.nc -v"`|
|ISAM_REGIONS|path/filename|optional ISAM regions files|`/nas1/cmaqruns/2018base/data/land/gridmask/AQFZones_EAsia_81K.nc`|

## 其他設定
- 官方教學或示範都是以個案方式，實務上有批次間相連的困難。此處以官網最新腳本範例(`v533`)比較說明
- **ISAM**也有其初始狀態(`$ISAM_NEW_START`)。此處以每月第1批次(`run5`)為初始。其他批次、或同一批次其他天則為接序執行。

```bash
(base)
kuang@114-32-164-198 /Users/cmaqruns/2018base
$ diff run_isamMM_RR_DM.csh2 ../2016base/old_scripts/run_cctm_Bench_2016_12SE1.csh
525,528c458,459
<          if ($RUN == 5 ) then
<            setenv ISAM_NEW_START Y
<            setenv ISAM_PREVDAY
<          endif
---
>           setenv ISAM_NEW_START Y
>           setenv ISAM_PREVDAY
```
  - 此段專為特定月份、特定批次編號執行**ISAM**之方便門

```python
530,561c461,462
<          echo 'kuang' #in case of another run or another days
<          setenv ISAM_NEW_START N
<          if ( $MO == '04' && $RUN == 5 && $TODAYJ == $START_DAY ) then
<            setenv ISAM_NEW_START Y
<            setenv ISAM_PREVDAY
<          endif
```
- 如非啟始，則需要給定前一天最末小時的執行結果`ISAM_PREVDAY`
  - 檔名設定有地區代碼`${BSN}`，如果是全區`AL`則無
  - 此處為同一批次、隔日之後的狀況。將前日最末小時之`CCTM_SA_CGRID`檔案設定為初始值。

```python
<          if ( $BSN == 'AL' )then
<            setenv ISAM_PREVDAY "$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}.nc"
<          else
<            if ( -e  "$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc" )then
<              setenv ISAM_PREVDAY "$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc"
<            else
<              setenv ISAM_PREVDAY "$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc"
<            endif
<          endif
```
- 測試是否存在`ISAM_PREVDAY`檔案，如果不存在，表示是跨批次執行，要把前1批次最末小時結果連結到本批次目錄。
  - 如果真的也沒有分地區之執行結果，至少把全區結果連過來。如果連全區也沒有，腳本就會中斷，必須先產生一個`CCTM_SA_CGRID`檔案出來。

```python
<          if (! (-e $ISAM_PREVDAY )) then
<            @ PRUN = $RUN - 1
<            set PRUNID = ${VRSN}_${compilerString}_${APYM}_run${PRUN}
<            set POUTDIR = ${OUTDIR}/../output_CCTM_${PRUNID}
<            if ( $BSN == 'AL' )then
<              ln -sf ${POUTDIR}/CCTM_SA_CGRID_${PRUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}.nc \
<                   $OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}.nc
<            else
<              if ( -e ${POUTDIR}/CCTM_SA_CGRID_${PRUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc ) then
<                ln -sf ${POUTDIR}/CCTM_SA_CGRID_${PRUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc \
<                   $OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc
<              else
<                ln -sf ${POUTDIR}/CCTM_SA_CGRID_${PRUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}.nc \
<                   $OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}_${GRID_NAME}_${STKCASEE}_${BSN}.nc
<              endif
<            endif
<          endif
---
>           setenv ISAM_NEW_START N
>           setenv ISAM_PREVDAY "$OUTDIR/CCTM_SA_CGRID_${RUNID}_${YESTERDAY}.nc"

```

## Reference
- USEPA, **Integrated Source Apportionment Method (CMAQ-ISAM)**, CMAQ User's Guide (c) 2021, [github](https://github.com/USEPA/CMAQ/blob/main/DOCS/Users_Guide/CMAQ_UG_ch11_ISAM.md), Latest commit  on 18 Aug, 2021
- USEAP, **CMAQ Installation & Benchmarking Tutorial**, [github](https://github.com/USEPA/CMAQ/blob/main/DOCS/Users_Guide/Tutorials/CMAQ_UG_tutorial_benchmark.md), Latest commit on 18 Aug, 2021