
import numpy as np
import netCDF4
import rasterio
import os
from pyproj import Proj

spec='BC CO NH3 NMVOC NOx OC PM10 PM2.5 SO2'.split()
m='4'
fnames=['v50_'+s+'_2015_4_TNR_Ship.0.1x0.1.nc' for s in spec]
nc = netCDF4.Dataset(fnames[0],'r')
lat0,lon0=nc['lat'][:],nc['lon'][:]
nc.close()

fname='DensGlobD6.nc'
nc = netCDF4.Dataset(fname,'r')
lat1,lon1=nc['lat'][:],nc['lon'][:]
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
v1=V[1][0]
ny1,nx1=nc[v1].shape
dens=np.array(nc[v1][:,:])
nc.close()

fnameO=fname.replace('.nc',spec[0]+'.nc')
os.system('cp DensGlobD6.nc '+fnameO)
nc = netCDF4.Dataset(fnameO,'r+')
I10=np.array([int((i-lon0[0])/0.1) for i in lon1])
J10=np.array([int((j-lat0[0])/0.1) for j in lat1])
sI10,sJ10=list(set(I10)),list(set(J10))
sI10.sort();sJ10.sort()
SumDens=np.sum(dens[:,:])
RatDens=dens[:,:]/SumDens

for ks in range(len(spec)):
  nc = netCDF4.Dataset(fnames[ks],'r')
  v=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]] [1][0]
  EmsGlb=np.sum(np.array(nc[v][sJ10[0]:sJ10[-1]+1,sI10[0]:sI10[-1]+1]))*20*20
  nc.close()
  fnameO=fname.replace('.nc',spec[ks]+'.nc')
  os.system('cp DensGlobD6.nc '+fnameO)
  nc = netCDF4.Dataset(fnameO,'r+')
#  nc[v1][:,:]=np.array(EmsGlb*RatDens[:,:]*10**18,dtype=int)
  nc[v1][:,:]=EmsGlb*RatDens[:,:]
  nc.close()

