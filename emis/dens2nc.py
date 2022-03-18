import numpy as np
import netCDF4
import rasterio
import os
from pyproj import Proj



fname='templateD6.nc'
nc = netCDF4.Dataset(fname,'r')
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=nc.YCENT, lon_0=nc.XCENT, x_0=0, y_0=0.0)
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=nc.variables[V[3][0]].shape
x1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x1,y1=np.meshgrid(x1d,y1d)
lon1,lat1=pnyc(x1,y1, inverse=True)
mnx,mny=min([100,np.min(lon1)]),min([15,np.min(lat1)])
mxx,mxy=max([134,np.max(lon1)]),max([42,np.max(lat1)])
nc.close()

kinds=['Glob','Comm','Fish','Leis','OGas']
fnames=['shipdensity_global.tif','ShipDensity_Commercial1.tif','ShipDensity_Fishing1.tif','ShipDensity_Leisure1.tif','ShipDensity_OilGas1.tif']
knames={k:n for k,n in zip(kinds,fnames)}
for k in kinds[2:]:
  fname=knames[k]
  fnameO='Dens'+k+'D6.nc'
  img = rasterio.open(fname)
  data=img.read() 
  data=np.flip(data[0,:,:],[0]) 
  nx,ny,nz=img.width,img.height,img.count
  dxm,dym=(img.bounds.right-img.bounds.left)/img.width,-(img.bounds.top-img.bounds.bottom)/img.height #間距
  x0,y0=img.xy(0,0)
  lon=np.array([x0+dxm*i for i in range(nx)])
  lat=np.flip(np.array([y0+dym*(i) for i in range(ny)]))
  ix=np.where((lon>=mnx)&(lon<=mxx))[0]
  iy=np.where((lat>=mny)&(lat<=mxy))[0]
  data1=data[iy[0]:iy[-1]+1,ix[0]:ix[-1]+1]
  os.system('cp densiD6.nc '+fnameO)
  nc = netCDF4.Dataset(fnameO,'r+')
  V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
  v=V[1][0]
  try:
    nc[v][:,:]=data1[:,:]
    nc.close()
  except:
    print('fail filling '+k)
