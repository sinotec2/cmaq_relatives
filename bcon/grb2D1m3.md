# EAC4檔案轉成m3.nc格式

## 背景

## [grb2D1m3.py](https://github.com/sinotec2/cmaq_relatives/blob/master/bcon/grb2D1m3.py)程式說明

### 引數
- [grb2D1m3.py](https://github.com/sinotec2/cmaq_relatives/blob/master/bcon/grb2D1m3.py) [YYMM.nc]((https://sinotec2.github.io/Focus-on-Air-Quality/AQana/GAQuality/ECMWF/EC_ReAna/#%E6%A9%AB%E5%90%91%E5%90%88%E4%BD%B5))

### I/O檔案
- Inputs
  - BCON模版
  - `m3.nc`模版
  - 逐日密度檔案
- Output
  - *YYMM*D1.m3.nc
  
### 分段說明
- 使用scipy的griddata進行水平的內插
- 將dt2jul、jul2dt寫成副程式`dtconvertor`，簡化程式版面
- 對照表也寫成`json`檔案

```python
     1	#argumens numNest gribFname
     2	import netCDF4
     3	import numpy as np
     4	import datetime
     5	from scipy.interpolate import griddata
     6	import json
     7	
     8	from pyproj import Proj
     9	import sys,os,subprocess
    10	from dtconvertor import dt2jul, jul2dt
    11	
    12	
```
- 分別讀取分子量(`mws`)、EAC4物質代碼(`dic`)、與對照到CMAQ氣狀物(`nms_gas`)及粒狀物(`nms_part`)之名稱
  - 層數的對照表(deprecated，改在wsite進行對照)

```python
    13	for v in ['mws','dic','nms_gas','nms_part']:
    14	  with open(v+'.json', 'r') as jsonfile:
    15	    exec(v+'=json.load(jsonfile)')
    16	uts=['PPM',"ug m-3          "]
    17	l34=['21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', 
    18	     '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
    19	l40=['21', '21', '22', '22', '23', '24', '24', '25', '25', '26', '27', '28', '28', '29', '30', '31', '32', '32', '33', '34', 
    20	     '35', '36', '37', '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
    21	d40_23={39-k:l34.index(l40[k]) for k in range(40)}
```
- 讀取一個BCON的樣版。從中取得粒狀物之間的比例關係(`rate`)
  - 因為EAC4的粒狀物沒有粒徑I、J之分，需要將其切分。

```python
    22	byr=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n')[-2:]
    23	#read a BC file as rate base
    24	fname='/nas1/cmaqruns/2019base/data/bcon/BCON_v53_1912_run5_regrid_20191201_TWN_3X3'
    25	nc = netCDF4.Dataset(fname,'r')
    26	Vb=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
    27	rate={}
    28	for v in nms_part:
    29	  nms=nms_part[v]
    30	  for nm in nms:
    31	    if nm not in Vb[2]:sys.exit(v+' not in BCON file')
    32	  avg=[np.mean(nc.variables[nm][:]) for nm in nms]
    33	  sum_avg=sum(avg)
    34	  if sum_avg==0:sys.exit('sum_avg==0')
    35	  ratev=[avg[i]/sum_avg for i in range(len(avg))]
    36	  rate.update({v:ratev})
    37	for v in nms_gas:
    38	  rate.update({v:[1.]})
    39	
```
- 讀取[合併](https://sinotec2.github.io/Focus-on-Air-Quality/AQana/GAQuality/ECMWF/EC_ReAna/#%E6%A9%AB%E5%90%91%E5%90%88%E4%BD%B5)後之EAC4檔案

```python
    40	#read the merged grib files (ncl_convert2nc)
    41	#lay,row in reversed directions
    42	fname=sys.argv[1]
    43	nc = netCDF4.Dataset(fname,'r')
    44	V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
    45	nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
    46	#read the timestamp in nc and store at /expand the nc1
    47	SDATE=[datetime.datetime.strptime(''.join([str(i, encoding='utf-8') for i in list(nc.variables[V[1][0]][t, :])]),\
    48	 '%m/%d/%Y (%H:%M)') for t in range(nt)]
    49	bdate,edate=SDATE[0],SDATE[-1]
    50	delt=edate-bdate
    51	ntA=int(delt.total_seconds()/3600.)
    52	JuliHr=[int((bdate+datetime.timedelta(hours=t)).strftime("%Y%j%H")) for t in range(ntA)]
    53	
```
- 讀取`m3.nc`模版
  - 污染項目需事先按照`nms_gas`和`nms_part`的對照表挑選污染項目。
  - 先對時間進行展開

```python
    54	N='D1'
    55	tmps={'D1':'templateD1.ncV49K34','D2':'templateD2.ncV49K34'}
    56	path='./'
    57	fnameO=fname.replace('.nc',N+'.m3.nc')
    58	if not os.path.exists(fnameO):os.system('cp '+path+tmps[N]+' '+fnameO)
    59	nc1= netCDF4.Dataset(fnameO,'r+')
    60	V1=[list(filter(lambda x:nc1.variables[x].ndim==j, [i for i in nc1.variables])) for j in [1,2,3,4]]
    61	nv1=len(V1[3])
    62	nt1,nlay1,nrow1,ncol1=nc1.variables[V1[3][0]].shape
    63	if nt1<ntA:
    64	  print('expand the matrix')
    65	  for t in range(ntA):
    66	    nc1.variables['TFLAG'][t,0,0]=0
    67	if nt1>ntA:
    68	  nc1.close()
    69	  ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
    70	  os.system(ncks+' -O -d TSTEP,0,'+str(ntA-1)+' '+fnameO+' '+fnameO+'_tmp;mv '+fnameO+'_tmp '+fnameO) 
    71	  nc1= netCDF4.Dataset(fnameO,'r+')
    72	nc1.SDATE=JuliHr[0]//100
    73	nc1.STIME=JuliHr[0]%100*10000
    74	var=np.zeros(shape=(ntA,nc1.NVARS,2))
    75	var[:,:,0]=np.array([i//100 for i in JuliHr])[:,None]
    76	var[:,:,1]=np.array([i%100  for i in JuliHr])[:,None]*10000
    77	nc1.variables['TFLAG'][:,:,:]=var[:,:,:]
```
- 空間內插之準備
  - 因EAC4檔案為等經緯度、非直角座標系統，因此選擇以scipy.griddata方式內插

```python
    78	Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
    79	pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40,
    80	        lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)
    81	
    82	xlon, xlat = nc.variables['lon_0'][:].flatten(), np.flip(nc.variables['lat_0'][:].flatten())
    83	lonm, latm = np.meshgrid(xlon, xlat)
    84	x,y=pnyc(lonm,latm, inverse=False)
    85	
    86	#interpolation indexing
    87	x1d=[nc1.XORIG+nc1.XCELL*i for i in range(ncol1)]
    88	y1d=[nc1.YORIG+nc1.YCELL*i for i in range(nrow1)]
    89	x1,y1=np.meshgrid(x1d, y1d)
    90	maxx,maxy=x1[-1,-1],y1[-1,-1]
    91	minx,miny=x1[0,0],y1[0,0]
    92	boo=(abs(x) <= (maxx - minx) /2+nc1.XCELL*10) & (abs(y) <= (maxy - miny) /2+nc1.YCELL*10)
    93	idx = np.where(boo)
    94	mp=len(idx[0])
    95	xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]
    96	
```
- 讀取[空氣密度]數據，以備粒狀物濃度的計算

```python
    97	print('read the density of air')
    98	dlay=np.array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
    99	       17, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30, 32, 34, 35, 37, 39])
   100	dens=np.zeros(shape=(ntA,40, nrow1, ncol1))
   101	caldat=list(set([int((bdate+datetime.timedelta(hours=t)).strftime("%Y%m%d")) for t in range(ntA)]))
   102	caldat.sort()
   103	for c in caldat:
   104	  iday=caldat.index(c)
   105	  fname='/nas1/cmaqruns/20'+byr+'base/data/mcip/RHO/RHO.'+str(c)+'.nc'
   106	  ncr = netCDF4.Dataset(fname,'r')
   107	  ntr=min(24,ncr.dimensions['TSTEP'].size)
   108	  t1=iday*24
   109	  t2=min(ntA,t1+min(24,ntr))
   110	  hrs=t2-t1
   111	  dens[t1:t2,:,:,:]=ncr.variables['DENS'][:hrs,:,:,:] *1E9 #(kg to microgram)
   112	dens2=np.zeros(shape=(ntA,nlay1, nrow1, ncol1))
   113	for k in range(nlay1):
   114	  dens2[:,k,:,:]=dens[:,dlay[k],:,:]
```
- 讀取EAC4濃度內容，進行空間內插
  - EAC4的高度方式自頂到底、緯度自北向南，與`m3.nc`定義相反，需要進行[翻轉](https://vimsky.com/zh-tw/examples/usage/python-numpy.flip.html)(`np.flip`)，4個軸中高度、緯度分別是第1、2軸。
  - 翻轉後矩陣、併同前述d01網格座標系統，一起呼叫griddata進行(線性)內插。

```python
   115	var=np.zeros(shape=(nt, nlay, nrow, ncol))
   116	zz=np.zeros(shape=(nt, nlay1, nrow1, ncol1))
   117	var2=np.zeros(shape=(ntA,nlay1, nrow1, ncol1))
   118	print('fill the matrix')
   119	for v in list(nms_gas)+list(nms_part) :
   120	  var[:,:,:,:]=np.flip(nc.variables[v][:,:,:,:], [1,2])
   121	  for t in range(nt):
   122	    c = np.array([var[t,:,idx[0][i], idx[1][i]] for i in range(mp)])
   123	    for k in range(nlay1):
   124	      zz[t,k,:,: ] = griddata(xyc, c[:,k], (x1, y1), method='linear')
```
- 時間(線性)內插

```python
   125	  for t in range(0,ntA,3):
   126	    t3=int(t/3)
   127	    var2[t+0,:,:,:]=zz[t3,:,:,:]
   128	    var2[t+1,:,:,:]=zz[t3,:,:,:]*2/3+zz[t3+1,:,:,:]*1/3
   129	    var2[t+2,:,:,:]=zz[t3,:,:,:]*1/3+zz[t3+1,:,:,:]*2/3
```
- 氣狀物單位轉換(重量混合比轉PPM)

```python
   130	  if v in nms_gas:
   131	    nc1.variables[nms_gas[v]][:]=var2[:]*rate[v][0] * 28.E6/mws[dic[v]] #mixing ratio to ppm
```
- 粒狀物單位轉換(重量混合比轉 &mu; g/M<sup>3</sup>)

```python
   132	  else:
   133	#    unit=1E9*dens[:] #28.E6/mvol #mixing ratio(kg/kg) to microgram/M3
   134	    nms=nms_part[v]
   135	    for nm in nms:
   136	      nc1.variables[nm][:]+=var2[:] * rate[v][nms.index(nm)] * dens2[:]
   137	  print(v)
   138	
```
- 給定全域屬性，存檔，離開。

```python
   139	nc1.SDATE,nc1.STIME=nc1.variables['TFLAG'][0,0,:]
   140	nc1.NLAYS=nlay1
   141	nc1.TSTEP=10000
   142	nc1.close()
   143	
```

## 程式下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/bcon/grb2D1m3.py)

## Reference
- 純淨天空, **python numpy flip用法及代碼示例**, [vimsky](https://vimsky.com/zh-tw/examples/usage/python-numpy.flip.html)