# MOZARD/WACCM模式輸出轉成CMAQ初始條件_水平對照

## 背景

## 程式說明

### 程式分段說明
- 調用模組

```python
import numpy as np
import netCDF4
import os,sys, datetime, json
from pyproj import Proj


Latitude_Pole, Longitude_Pole = 23.61000, 120.990
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, 
		lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(16001)')
yrjulhh=sys.argv[1]
yrmn=datetime.datetime.strptime(yrjulhh[:-2], '%y%j').strftime('%y%m')

#read the mozart model results
fname='moz_41_20'+yrmn+'.nc'
if not os.path.exists(fname):sys.exit(fname+' not exist')
ncM = netCDF4.Dataset(fname,'r')
v4M=list(filter(lambda x:ncM.variables[x].ndim==4, [i for i in ncM.variables]))
ntM,nlayM,nrowM,ncolM=(ncM.variables[v4M[0]].shape[i] for i in range(4))
lonM=[ncM.XORIG+ncM.XCELL*i for i in range(ncolM)]
latM=[ncM.YORIG+ncM.YCELL*i for i in range(nrowM)]
tflagM=[str(i*100+j//10000)[2:] for i,j in zip(ncM.variables['TFLAG'][:,0,0],ncM.variables['TFLAG'][:,0,1])]
tM=tflagM.index(yrjulhh)

#load mz2cmaq map
with open('cb6_new.json','r') as f:
  mz2cm=json.load(f)
with open('cb6_newNum.json','r') as f:
  mz2cmNum=json.load(f)
with open('lay2VGLEVLS.json','r') as f:
  lay2VGLEVLS=json.load(f)
lay2VGLEVLS.update({'40':40})

#read the template(s)
fname='ICON_20'+yrjulhh+'.d1'
nc = netCDF4.Dataset(fname,'r')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
X=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
Y=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
lon, lat= pnyc(X,Y, inverse=True)
lon_ss=np.searchsorted(lonM,lon)
lat_ss=np.searchsorted(latM,lat)
tflag=nc.variables['TFLAG'][:,0,:]
nc.close()

#drop keys which values not in new CMAQ spec_list
mc=list(mz2cm)
for i in mc:
  if i not in v4M:
    mz2cm.pop(i)
    continue
  if mz2cm[i] not in v4:
    mz2cm.pop(i)

#save the matrix
v4M=list(mz2cm)
A5=np.zeros(shape=(len(v4M),nlayM,nrowM,ncolM))
for ix in range(len(v4M)):
  for k in range(nlayM):
    A5[ix,k,:,:]=ncM.variables[v4M[ix]][tM,lay2VGLEVLS[str(k)],:,:]*1000.*1000. #Volume Mixing Ratio to PPM
ncM.close()

#perform the horizontal interpolation and write results
fname='ICON_20'+yrjulhh+'.d1'
nc = netCDF4.Dataset(fname,'r+')
for x in v4M:
  nc.variables[mz2cm[x]][0,:,:,:]=0

for jcrs in range(nrow):
  jmz=lat_ss[jcrs]
  for icrs in range(ncol):
    imz=lon_ss[icrs]
    rx=(lon[icrs]-lonM[imz-1])/(lonM[imz]-lonM[imz-1])
    ry=(lat[jcrs]-latM[jmz-1])/(latM[jmz]-latM[jmz-1])
    A2x=A5[:,:,jmz,imz]*rx+A5[:,:,jmz,imz-1]*(1-rx)
    A2y=A5[:,:,jmz,imz]*ry+A5[:,:,jmz-1,imz]*(1-ry)
    A2=(A2x+A2y)/2.
    for x in v4M:
      nc.variables[mz2cm[x]][0,:,jcrs,icrs]+=A2[v4M.index(x),:-1]*mz2cmNum[x]
nc.close()
```
## 程式下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/moz2cmaqHd1J.py)

## Reference
-  純淨天空, **Python numpy.searchsorted()用法及代碼示例** [vimsky](https://vimsky.com/zh-tw/examples/usage/numpy-searchsorted-in-python.html)