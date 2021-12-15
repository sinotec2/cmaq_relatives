import numpy as np
import netCDF4
import PseudoNetCDF as pnc
import os,twd97,sys
import datetime
from pyproj import Proj
if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(1601) + metCRO3D_file')
yrmn=sys.argv[1]
CRS=sys.argv[2] #only vertical levels are used
nc = netCDF4.Dataset(CRS,'r')
lvs_crs0= nc.VGLVLS[:]
lvs_crs=((1013-50)*lvs_crs0+50)*-1
nlays=nc.NLAYS

#store the mozart model results
fname='moz_41_20'+yrmn+'.nc' #may be other source
nc = netCDF4.Dataset(fname,'r')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
lvs= nc.VGLVLS[:]*-1
sp_crs=np.searchsorted(lvs,lvs_crs)
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
A5=np.zeros(shape=(nc.NVARS,nt,nlay,nrow,ncol))
for ix in range(nc.NVARS):
  A5[ix,:,:,:,:]=nc.variables[v4[ix]][:,:,:,:]

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
