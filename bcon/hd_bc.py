import netCDF4
import numpy as np
import datetime
from bisect import bisect
from pyproj import Proj
import sys,os,subprocess
from dtconvertor import dt2jul, jul2dt
from scipy.interpolate import CubicSpline

#open the template BC file
fname='BCON_v53_1804_run5_regrid_20180331_HUADON_3k'
nc1= netCDF4.Dataset(fname,'r+')
V1=[list(filter(lambda x:nc1.variables[x].ndim==j, [i for i in nc1.variables])) for j in [1,2,3,4]]
nt1,nlay1,nbnd1=nc1.variables[V1[2][1]].shape
DATES=[jul2dt([i,j]) for i,j in zip(nc1['TFLAG'][:,0,0],nc1['TFLAG'][:,0,1])]
idate={DATES[i]:i for i in range(nt1)}
SDATE=[jul2dt([i,0]) for i in set(nc1['TFLAG'][:,0,0])]
SDATE.sort()
ymds=[i.strftime("%Y%m%d") for i in SDATE]
pnyc1 = Proj(proj='lcc', datum='NAD83', lat_1=nc1.P_ALP, lat_2=nc1.P_BET,lat_0=nc1.YCENT, lon_0=nc1.XCENT, x_0=0, y_0=0.0)
x1d1=[nc1.XORIG+i*nc1.XCELL for i in range(-1,nc1.NCOLS+1)]
y1d1=[nc1.YORIG+j*nc1.YCELL for j in range(-1,nc1.NROWS+1)]

#read the d1 CCTM_ACONC files (K40)
lay32_40={i:i for i in range(25)}
lay32_40.update({25+(i-26)//2:i for i in range(26,40,2)})
root='/u01/cmaqruns/2018base/data/output_CCTM_v53_gcc_1804_run5/CCTM_ACONC_v53_gcc_1804_run5_'
tail='_CWBWRF_15k_11.nc'
fnames=[root+ymd+tail for ymd in ymds]
# turning points among nbnd1 sequence
N0=0
N1=N0+nc1.NCOLS+1
N2=N1+nc1.NROWS+1
N3=N2+nc1.NCOLS+1
N4=N3+nc1.NROWS+1
for fname in fnames[:1]:
  nc = netCDF4.Dataset(fname,'r')
# interpolation indexing
  if fname==fnames[0]: 
    V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
    nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
# traslation of map centers
    dx,dy=pnyc1(nc.XCENT,nc.YCENT, inverse=False)
# parent grid coordinates in new system
    x1d=[nc.XORIG+i*nc.XCELL+dx for i in range(ncol)]
    y1d=[nc.YORIG+j*nc.YCELL+dy for j in range(nrow)]
# locate the corner grids
    i0,i1=bisect(x1d,x1d1[0])-1, bisect(x1d,x1d1[-1]) 
    j0,j1=bisect(y1d,y1d1[0])-1, bisect(y1d,y1d1[-1]) 
  for t in range(nt):
    tt=idate(jul2dt(nc['TFLAG'][t,0,:]))
    for k in range(nlay1):
      kk=lay32_40[k]
# set(V[3])==set(V1[2]) ,checked before running
      for v in V[3]: 
# boundary tract begin with South-West corner(j0,i0), and go around the domain in counter-clock wise direction
        nc1[v][tt,k,N0:N1] =         CubicSpline(x1d[i0:i1+1], nc[v][t,kk,j0,i0:i1+1]) (x1d1[:-1])
        nc1[v][tt,k,N1:N2] =         CubicSpline(y1d[j0:j1+1], nc[v][t,kk,j0:j1+1,i1]) (y1d1[:-1])
        nc1[v][tt,k,N2:N3] = np.flip(CubicSpline(x1d[i0:i1+1], nc[v][t,kk,j1,i0:i1+1]) (x1d1[:-1]),axis=0)
        nc1[v][tt,k,N3:N4] = np.flip(CubicSpline(y1d[j0:j1+1], nc[v][t,kk,j0:j1+1,i0]) (y1d1[:-1]),axis=0)
    print(tt)
  nc.close()
nc1.close()

