# 整併8個批次wrfout成為全月檔案

## 背景
- 全月的空品模擬會減省許多不必要的初始化時間，減少檔案個數，一如CAMx全月模擬的架構。
- 然而`wrfout`中有不少變數、標籤是以批次起始時間為準的。`wrfout`無法靠簡單的`ncrcat`予以整併。
     - 

|變數名稱|變數內容|
|----|----|
|ACGRDFLX| ACCUMULATED GROUND HEAT FLUX|
|ACSNOM| ACCUMULATED MELTED SNOW|
|RAINC| ACCUMULATED TOTAL CUMULUS PRECIPITATION|
|RAINSH| ACCUMULATED SHALLOW CUMULUS PRECIPITATION|
|RAINNC| ACCUMULATED TOTAL GRID SCALE PRECIPITATION|
|SNOWNC| ACCUMULATED TOTAL GRID SCALE SNOW AND ICE|
|GRAUPELNC| ACCUMULATED TOTAL GRID SCALE GRAUPEL|
|HAILNC| ACCUMULATED TOTAL GRID SCALE HAIL|
|ACHFX| ACCUMULATED UPWARD HEAT FLUX AT THE SURFACE|
|ACLHF| ACCUMULATED UPWARD LATENT HEAT FLUX AT THE SURFACE|

## [add_xtime程式](https://github.com/sinotec2/cmaq_relatives/blob/master/mcip/add_xtime.py)說明


### 分段說明
- 
```python
     1	import netCDF4
     2	import subprocess
     3	import datetime
     4	import numpy as np
     5	import sys,os
     6	from calendar import monthrange
     7	#working under 16??, the file in directory(or file by link) will be modified
     8	yrmn=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n').split('/')[-1]
     9	begd=datetime.datetime(2000+int(yrmn[:2]),int(yrmn[2:4]),1)+datetime.timedelta(days=-1)
    10	b,e=monthrange(2000+int(yrmn[:2]),int(yrmn[2:4]))
    11	x='XTIME'
    12	y='ITIMESTEP'
    13	#accumulation variables
    14	acc=['ACGRDFLX', 'ACSNOM', 'RAINC', 'RAINSH', 'RAINNC', 'SNOWNC', 'GRAUPELNC', 'HAILNC', 'ACHFX', 'ACLHF']
    15	#note acc should be saved and restored(if needed) before following actions:
    16	# for dm in 1 2 4;do
    17	#   for i in $(ls wrfout_d0${dm}*);do d=$(echo $i|cut -d'_' -f3)
    18	#     ncks -O -v Times,ACGRDFLX,ACSNOM,RAINC,RAINSH,RAINNC,SNOWNC,GRAUPELNC,HAILNC,ACHFX,ACLHF $i $d.nc;done
    19	#   ncrcat -O 2016*.nc acc_d0${dm}.nc
    20	# done
    21	for DM in ['1', '2','4']:
    22	  #each run must begin with same day(last day of previous month)
    23	  fname='wrfout_d0'+DM+'_'+begd.strftime("%Y-%m-%d")+'_00:00:00'
    24	  nc = netCDF4.Dataset(fname,'r')
    25	  min0=nc.variables[x][-1]+60
    26	  START_DATE=nc.SIMULATION_START_DATE
    27	  JULYR=nc.JULYR
    28	  JULDAY=nc.JULDAY
    29	  if JULYR%4==0:
    30	    JULDAY=min(366,JULDAY)
    31	  else:
    32	    JULDAY=min(365,JULDAY)
    33	  TITLE =nc.TITLE
    34	  # begin with zero accumulation
    35	  acmx={ac:np.zeros(shape=nc.variables[ac].shape) for ac in acc}
    36	  nc.close()
    37	  #run5~12
    38	  for r in range(5,13):
    39	    d0=(r-5)*4+2
    40	    dEnd=d0+4
    41	    if r==12:dEnd=d0+5    
    42	    for d in range(d0,dEnd):
    43	      nowd=(begd+datetime.timedelta(days=d)).strftime("%Y-%m-%d")
    44	      fname='wrfout_d0'+DM+'_'+nowd+'_00:00:00'
    45	      print(r,d,fname)
    46	      nc = netCDF4.Dataset(fname,'r+')
    47	      for ac in acc:
    48	        nc.variables[ac][:]+=acmx[ac]
    49	      if d==d0+3:
    50	        acmx={ac:nc.variables[ac][:] for ac in acc}
    51	      nc.SIMULATION_START_DATE=START_DATE
    52	      nc.START_DATE           =START_DATE
    53	      nc.JULYR                =JULYR
    54	      nc.JULDAY               =JULDAY
    55	      nc.TITLE                =TITLE
    56	      for t in range(24):
    57	        mins=min0+((d-1)*24+t)*60
    58	        nc.variables[x][t]=float(mins)
    59	        nc.variables[x].units='minutes since '+START_DATE
    60	        nc.variables[x].description='minutes since '+START_DATE
    61	        nc.variables[y][t]=int(mins)
    62	      nc.close()
    63	
```

## 程式下載
- [github](https://github.com/sinotec2/cmaq_relatives/blob/master/mcip/add_xtime.py)
