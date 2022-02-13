import os, sys
import numpy as np
from PseudoNetCDF.camxfiles.Memmaps import uamiv
from bisect import bisect
import netCDF4
from pandas import *

path='/nas1/camxruns/2016_v7/outputs/'
fname=path+'con01/1601baseT.S.grd02'
newf2 = uamiv(fname,'r')
x=[newf2.XORIG+i*newf2.XCELL for i in range(newf2.NCOLS)]
y=[newf2.YORIG+i*newf2.YCELL for i in range(newf2.NROWS)]

fname=path+'con01/1601baseEF3.S.grd01'
newf4 = uamiv(fname,'r')
ib=bisect(x,  newf4.XORIG)-1
ie=bisect(x, -newf4.XORIG)+1
je=bisect(y, -newf4.YORIG)+1
jb=bisect(y,  newf4.YORIG)-1
idx=[]
for i in range(ib,ie+1):
  idx.append((jb,i))
  idx.append((je,i))
for j in range(jb+1,je):
  idx.append((j,ib))
  idx.append((j,ie))
idx.sort()
idx=np.array(idx)
idd=(idx[:,0],idx[:,1])

fname='/nas1/cmaqruns/2016base/data/land/epic_festc1.4_20180516/gridmask/CNTY_TWN_3X3.nc'
nc = netCDF4.Dataset(fname,'r')
V=[v for v in nc.variables if v[-2:]!='53']
nv=len(V)
f=np.zeros(shape=(nv,nc.NROWS,nc.NCOLS))
for v in V:
  iv=V.index(v)
  f[iv,:,:]=nc.variables[v][0,0,:,:]
fs=np.sum(f,axis=0)
idfs=np.where(fs==1.0)
idx={2:idd,4:idfs}

v='PM25'
root={2:'baseT.S.grd02',4:'baseEF3.S.grd01'}
ms=['{:02d}'.format(m+1) for m in range(12)]
fnames={i:[path+'con'+ms[m]+'/16'+ms[m]+root[i] for m in range(12)] for i in [2,4]}
pm25={2:0,4:0}
with open('pm25_rat.csv','w') as fn:
  fn.write('pm25_2,pm25_4,pm25_2/pm25_4\n')
  for m in range(12):
    for d in [2,4]:
      newf = uamiv(fnames[d][m],'r')
      pm25.update({d:np.mean(np.array(newf.variables[v][:,0,idx[d][0],idx[d][1]]))})
    fn.write('{:7f},{:7f},{:5f}\n'.format(pm25[2],pm25[4],pm25[2]/pm25[4]))
df=read_csv('pm25_rat.csv')
a=np.array(df['pm25_2/pm25_4'])
print(np.mean(a))
print(np.mean(a[2:8])) #march to august
print(np.mean([a[i] for i in [0,1,8,9,10,11]]))
