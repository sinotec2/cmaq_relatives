# MOZARD/WACCM模式輸出轉成CMAQ初始條件_垂直對照

## 背景

## 程式說明

### 程式執行
- 引數：年月(4碼)與`METCRO3D`路徑及檔案名稱

### 程式分段說明
- 調用模組

```python
import numpy as np
import netCDF4
import os,sys
```
- 讀取引數：年月(4碼)與`METCRO3D`路徑及檔案名稱

```python
if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(1601) + metCRO3D_file')
  #eg. moz2cmaqV.py 1804 /nas1/cmaqruns/2018base/data/mcip/METCRO3D_1804_run6.nc
yrmn=sys.argv[1]
CRS=sys.argv[2] #only vertical levels are used
```
- 定義垂直高度與層數

```python
nc = netCDF4.Dataset(CRS,'r')
lvs_crs0= nc.VGLVLS[:]
lvs_crs=((1013-50)*lvs_crs0+50)*-1
nlays=nc.NLAYS
```
- 將`mozart`檔案內的高度及空品數據記下
  - 此處另外定義`fname`的用意，在於保持讀取其他檔案的可能及彈性(避免覆蓋)。
  - 此處選擇覆蓋原檔案，是節省磁碟機空間的方案

```python
#store the mozart model results
fname='moz_41_20'+yrmn+'.nc' #may be other source
nc = netCDF4.Dataset(fname,'r')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
```
- 將`mozart`垂直層數及高度記錄下來
  - 使用[searchsorted](https://vimsky.com/zh-tw/examples/usage/numpy-searchsorted-in-python.html)指令，在排序的數組中查找索引。

```python
lvs= nc.VGLVLS[:]*-1
sp_crs=np.searchsorted(lvs,lvs_crs)
```
- 空品數據存記起來，成為A5矩陣

```python
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
A5=np.zeros(shape=(nc.NVARS,nt,nlay,nrow,ncol))
for ix in range(nc.NVARS):
  A5[ix,:,:,:,:]=nc.variables[v4[ix]][:,:,:,:]
```
- 開啟新檔並進行**垂直內插**

```python
fname='moz_41_20'+yrmn+'.nc'
nc = netCDF4.Dataset(fname,'r+')
nc.VGLVLS=lvs_crs0
for kcrs in range(nlays):
  kmz=sp_crs[kcrs]
  if kmz==0:
    for ix in range(nc.NVARS):
      nc.variables[v4[ix]][:,kcrs,:,:]=A5[ix,:,0,:,:]
  else:
    r=(lvs_crs[kcrs]-lvs[kmz-1])/(lvs[kmz]-lvs[kmz-1])
    A4=A5[:,:,kmz,:,:]*r+A5[:,:,kmz-1,:,:]*(1-r)
    for ix in range(nc.NVARS):
      nc.variables[v4[ix]][:,kcrs,:,:]=A4[ix,:,:,:]
nc.close()
```
## 程式下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/moz2cmaqV.py)

## Reference
-  純淨天空, **Python numpy.searchsorted()用法及代碼示例** [vimsky](https://vimsky.com/zh-tw/examples/usage/numpy-searchsorted-in-python.html)