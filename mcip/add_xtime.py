import netCDF4
import subprocess
import datetime
import numpy as np
import sys,os
from calendar import monthrange
#working under 16??, the file in directory(or file by link) will be modified
yrmn=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n').split('/')[-1]
begd=datetime.datetime(2000+int(yrmn[:2]),int(yrmn[2:4]),1)+datetime.timedelta(days=-1)
b,e=monthrange(2000+int(yrmn[:2]),int(yrmn[2:4]))
x='XTIME'
y='ITIMESTEP'
#accumulation variables
acc=['ACGRDFLX', 'ACSNOM', 'RAINC', 'RAINSH', 'RAINNC', 'SNOWNC', 'GRAUPELNC', 'HAILNC', 'ACHFX', 'ACLHF']
#note acc should be saved and restored(if needed) before following actions:
# for dm in 1 2 4;do
#   for i in $(ls wrfout_d0${dm}*);do d=$(echo $i|cut -d'_' -f3)
#     ncks -O -v Times,ACGRDFLX,ACSNOM,RAINC,RAINSH,RAINNC,SNOWNC,GRAUPELNC,HAILNC,ACHFX,ACLHF $i $d.nc;done
#   ncrcat -O 2016*.nc acc_d0${dm}.nc
# done
for DM in ['1', '2','4']:
  #each run must begin with same day(last day of previous month)
  fname='wrfout_d0'+DM+'_'+begd.strftime("%Y-%m-%d")+'_00:00:00'
  nc = netCDF4.Dataset(fname,'r')
  min0=nc.variables[x][-1]+60
  START_DATE=nc.SIMULATION_START_DATE
  JULYR=nc.JULYR
  JULDAY=nc.JULDAY
  if JULYR%4==0:
    JULDAY=min(366,JULDAY)
  else:
    JULDAY=min(365,JULDAY)
  TITLE =nc.TITLE
  # begin with zero accumulation
  acmx={ac:np.zeros(shape=nc.variables[ac].shape) for ac in acc}
  nc.close()
  #run5~12
  for r in range(5,13):
    d0=(r-5)*4+2
    dEnd=d0+4
    if r==12:dEnd=d0+5    
    for d in range(d0,dEnd):
      nowd=(begd+datetime.timedelta(days=d)).strftime("%Y-%m-%d")
      fname='wrfout_d0'+DM+'_'+nowd+'_00:00:00'
      print(r,d,fname)
      nc = netCDF4.Dataset(fname,'r+')
      for ac in acc:
        nc.variables[ac][:]+=acmx[ac]
      if d==d0+3:
        acmx={ac:nc.variables[ac][:] for ac in acc}
      nc.SIMULATION_START_DATE=START_DATE
      nc.START_DATE           =START_DATE
      nc.JULYR                =JULYR
      nc.JULDAY               =JULDAY
      nc.TITLE                =TITLE
      for t in range(24):
        mins=min0+((d-1)*24+t)*60
        nc.variables[x][t]=float(mins)
        nc.variables[x].units='minutes since '+START_DATE
        nc.variables[x].description='minutes since '+START_DATE
        nc.variables[y][t]=int(mins)
      nc.close()

