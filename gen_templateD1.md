# 產生D1範圍之`CMAQ`初始濃度檔案序列

## 背景

## 程式說明

### 程式執行
#### 引數
- 年月(4碼)
#### 輸入檔
1. 全球模式模擬結果(經垂直內插)
 - 檔名規則：`'moz_41_20'+yrmn+'.nc'`
 - 只讀取時間標籤
1. D1範圍`CMAQ`濃度檔模版：`ICON_tmp.d1`，規格如下：

```bash
kuang@node03 /nas1/cmaqruns/2016base/data/bcon
$ nc=ICON_tmp.d1
(py37)
kuang@node03 /nas1/cmaqruns/2016base/data/bcon
$ ncdump -h $nc|H
netcdf ICON_tmp {
dimensions:
        TSTEP = UNLIMITED ; // (1 currently)
        LAY = 40 ;
        ROW = 57 ;
        COL = 57 ;
        VAR = 248 ;
        DATE-TIME = 2 ;
variables:
        float AACD(TSTEP, LAY, ROW, COL) ;
```


#### 輸出檔
- 每個時間D1範圍`CMAQ`之濃度檔

### 分段說明
- 引用模組及讀取引數

```python
import numpy as np
import netCDF4
import os,sys,subprocess

if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(1601)')
yrmn=sys.argv[1]
```
- 程式會使用到系統的[ncks](https://sinotec2.github.io/Focus-on-Air-Quality/utilities/netCDF/ncks/)、`ncatted` 2支程式

```python
ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
ncatted=subprocess.check_output('which ncatted',shell=True).decode('utf8').strip('\n')
```
- 開啟舊檔，讀取時間標籤`tflag`

```python
fname='moz_41_20'+yrmn+'.nc'
nc = netCDF4.Dataset(fname,'r')
tflag=nc.variables['TFLAG'][:,0,:]
nt,dt=tflag.shape
```
- 將每個時間分別寫成`CMAQ`初始濃度檔案備用

```python
fname='ICON_tmp.d1'
for j in range(nt):
  fnamej=fname.replace('tmp',str(tflag[j,0])+'{:02d}'.format(int(tflag[j,1]/10000)))
#  if '201600418' not in fnamej:continue
  os.system('cp '+fname+' '+fnamej) 
  nc = netCDF4.Dataset(fnamej,'r+')
  nc.variables['TFLAG'][0,:,0]=[tflag[j,0] for v in range(nc.NVARS)]
  nc.variables['TFLAG'][0,:,1]=[tflag[j,1] for v in range(nc.NVARS)]
  nc.SDATE=tflag[j,0]
  nc.STIME=tflag[j,1]
  nc.close()
  os.system(ncatted+' -O -a TSTEP,global,o,i,60000 '+fnamej)
  a=fnamej+'.tmp'
  os.system(ncks+' -O --mk_rec_dmn TSTEP '+fnamej+' '+a+';mv -f '+a+' '+fnamej)
```

## 程式下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/gen_templateD1.py)

### Reference
- sinotec2, **NCKS 在空品模式中的應用**, [FAQ](https://sinotec2.github.io/Focus-on-Air-Quality/utilities/netCDF/ncks/), Dec 10 2021