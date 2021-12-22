
# ISAM結果檔案之讀取(PM10)

## 背景
- 由於**ISAM**並未設計給**PM10**的追蹤使用，因此也找不到類似`combine`的後處理程式，可以整合**CMAQ-ISAM**執行的成果。只能自行撰寫程式整併所有的氣膠成分。
  - CMAQ-ISAM執行的成果`CCTM_SA_ACONC`變數的命名規則：以底線(`_`)區隔之複合變數`spec_group`，其中：
    - `spec`=`CCTM_ACONC`的[污染項目名稱](https://github.com/USEPA/CMAQ/blob/main/CCTM/src/MECHS/mechanism_information/cb6mp_ae6_aq/AE6_species_table.md)
    - `group`=`isam_control.txt`檔案裏定義的`TAG_NAME`，另外還包括`ICON`、`BCON`、`OTHR`等固定內設的標籤。
- 綜合性污染物的定義：可以參考`$REPO_HOME/POST/combine/scripts/spec_def_files/SpecDef_${MECH}.txt`的內容
- **ISAM**可能同時執行多個**分區**之排放分析，因此程式輸出結果須能有所區別
  - 分區的定義在`isam_control.txt`檔案裏的`REGION(S)`，指定到`$ISAM_REGIONS`檔案的分區名稱內容
  - 此處以中國大陸的[空氣質量預報](http://big5.mee.gov.cn/gate/big5/www.mee.gov.cn/hjzl/dqhj/kqzlyb/)分區為例

|空氣質量預報分區|`$ISAM_REGIONS(REGION(S))`名稱|**ISAM**結果檔名標籤|
| ---- | ---- | ---- |
|華北(河北山東)|AQFZ1|JJZ|
|汾渭平原、山西、陜西、河南|AQFZ2|FWS|
|東北區域|AQFZ3|NEC|
|甘肅塞外|AQFZ4|NWC|
|兩湖華南|AQFZ5|SCH|
|四川廣西青康藏|AQFZ6|SWC|
|華東江蘇浙江安徽|AQFZ7|YZD|


## 程式說明

### **ISAM**執行

#### 批次

```bash
kuang@DEVP /home/cmaqruns/2018base
$ cat do_isam.csh
foreach BSN ('JJZ' 'SCH' 'YZD' 'FWS' 'NEC' 'NWC')
  source run_isamMM_RR_DM.csh2 04 6 d01 $BSN
end
```
#### 執行腳本
- [run_isamMM_RR_DM.csh](https://github.com/sinotec2/cmaq_relatives/blob/master/isam/run_isamMM_RR_DM.csh)

#### 腳本說明
- [執行CMAQ-ISAM](https://sinotec2.github.io/Focus-on-Air-Quality/GridModels/ISAM/run_isamMM_RR_DM/)

### 程式名稱
- [SA_PM10.py](https://github.com/sinotec2/cmaq_relatives/blob/master/isam/SA_PM10.py)

### 執行方式

#### 引數
- `CCTM_SA_ACONC`檔案名稱
- eg. `CCTM_SA_ACONC_v53_gcc_1804_run6_20180404_EAsia_81K_11_SCH.nc`

#### I/O檔案
- `CCTM_SA_ACONC`檔案：為執行**CMAQ-ISAM**的結果
- PM10模版檔案：`template_PM10.nc`
  - 單一污染物、單一時間、地面層
- 輸出結果檔案：`'PM10'+path+'_'+ymdh+'_'+g+'.nc'`
  - `path`：**ISAM**分區(詳前表**ISAM**結果檔名標籤及執行批次)
  - `ymdh`：年月日時
  - `g`：排放類別標籤(`TAG_NAME`)

#### 執行腳本([proc.cs](https://github.com/sinotec2/cmaq_relatives/blob/master/isam/proc.cs))

- 將**ISAM**結果與模版連結到同一目錄
- 每個結果檔案都執行一遍`SA_PM10.py`，
  - 會拆分成逐日、每個排放標籤、每個**分區**之分析濃度
  - 再逐層加總或合併
- 加總使用到python程式[addNC](https://github.com/sinotec2/Focus-on-Air-Quality/blob/main/utilities/netCDF/addNC.md)
  - 欲加總的內容項目太多了，以`ncs`變數累加之
  - 加總結果檔名：`PM10${z}_2018040${d}.nc`  
- 合併(照日期附加)
  - 使用[ncrcat]()程式
  - 可以用[VERDI]()檢視之

```bash
#isam job for 20180404~8, 6 AirQualityForecastZone(AQFS), only GR1~4 and PTA are taken into account
#sum up aerosol results using python program, to be PM10, see SA_PM10.py
in $(ls CCTM*nc);do python ../SA_PM10.py $nc;done >& /dev/null
for z in FWS JJZ NEC NWC SCH YZD;do 
  for d in {4..8};do
    #only GR13、GR24、PTA results(_[GP]*) are summed, see addNC, the python program
    ncs='';for nc in $(ls PM10${z}_2018040${d}_[GP]*.nc);do ncs=${ncs}" "$nc;done;
    python ~/bin/addNC $ncs PM10${z}_2018040${d}.nc
  done
done
# combine all days for each zone
for z in FWS JJZ NEC NWC SCH YZD;do ncrcat -O PM10${z}_2018040?.nc PM10${z}.nc;done
```


### 程式分段說明
- 調用模組

```python
import numpy as np
import netCDF4
import sys, os
```
- 讀取引數(`fname`)
  - 由`fname`中讀取分區路徑(`path`)

```python
fname=sys.argv[1]
intv=fname.split('_')[-1]
path=intv.strip('.nc')
ymdh=fname.split('_')[7]
```
- 開啟**ISAM**執行成果檔案
  - 讀取變數名稱，從其中區分成分項目`v4`，與`TAG_NAME`標籤`grp`

```python
nc = netCDF4.Dataset(fname, 'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))

v4=list(set([i.split('_')[0] for i in V[3]]));v4.sort()
grp=list(set([i.split('_')[1] for i in V[3]]));grp.sort()
```
- `PM10`的定義

```python
Sulfate='ASO4I ANO3I ANH4I ACLI ASO4J ANO3J ANH4J ASO4K ANO3K ANH4K'.split()
BC='AECI AECJ'.split()
OC='APOCI APNCOMI APOCJ AOTHRJ AXYL1J AXYL2J AXYL3J ATOL1J  ATOL2J  ATOL3J  ABNZ1J  ABNZ2J  ABNZ3J\
  AISO1J AISO2J  AISO3J  ATRP1J  ATRP2J  ASQTJ  AALK1J  AALK2J AORGCJ  AOLGBJ  AOLGAJ  APAH1J  APAH2J\
  APAH3J  APNCOMJ AOTHRI'.replace('_','').split()
Dust='AFEJ AALJ ASIJ ACAJ AMGJ AKJ AMNJ ACORS ASOIL ATIJ'.split()
SS='ANAI ANAJ ACLJ ACLK ASEACAT'.split()
Semi='ASVPO1J ASVPO2J  ASVPO3J  ASVPO2I  ASVPO1I ALVPO1J   ALVPO1I  AIVPO1J'.split()
aer=Sulfate+BC+OC+Dust+SS+Semi
```
- 逐一拆解檔案
  - 定義輸結果檔案名稱：`'PM10'+path+'_'+ymdh+'_'+g+'.nc'`

```python
for g in grp:
  fname = 'PM10'+path+'_'+ymdh+'_'+g+'.nc'
  os.system('cp template_PM10.nc '+fname)
  nco= netCDF4.Dataset(fname, 'r+')
```  
- 模版為單一時間檔案，須延長時間，以配合輸入檔長度。

```python
  for t in range(nt):  
    nco['TFLAG'][t,0,:]=nc['TFLAG'][t,0,:]
```
- 累加`PM10`
  - 因**ISAM**未處理氯離子等很多項目，矩陣無內容，因此須研判是否為`nan`，以避免被`netCDF4`[遮蔽](https://sinotec2.github.io/Focus-on-Air-Quality/utilities/netCDF/masked/)

```python
  var=np.zeros(shape=(nt,nlay,nrow,ncol))
  for v in set(aer) & set(v4):
    vg=v+'_'+g
    if np.isnan(np.max(nc[vg][:])):continue
    var[:]+=nc[vg][:]
  nco['PM10'][:]=var[:]
  nco.close()
```

## 程式下載
- 主程式[SA_PM10.py](https://github.com/sinotec2/cmaq_relatives/blob/master/isam/SA_PM10.py)
- 執行腳本[proc.cs](https://github.com/sinotec2/cmaq_relatives/blob/master/isam/proc.cs)

## 成果檢視
- [Northwestern China Source Contributions](https://youtu.be/lh7Eq-um-Ng)

## Reference
- 中華人民共和國生態環境部, **空氣品質預報**, [生態環境部官網](http://big5.mee.gov.cn/gate/big5/www.mee.gov.cn/hjzl/dqhj/kqzlyb/)
