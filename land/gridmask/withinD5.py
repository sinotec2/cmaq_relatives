import shapefile
from pandas import *
import numpy as np
import netCDF4
from pyproj import Proj
from shapely.geometry import Point, Polygon
import sys
nc = netCDF4.Dataset('template_d4.nc', 'r')
Latitude_Pole, Longitude_Pole = nc.YCENT, nc.XCENT
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40,
        lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)
RESm=1000.

V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
xmin=nc.XORIG
ymin=nc.YORIG
xmax=nc.XORIG+(ncol+1)*nc.XCELL
ymax=nc.YORIG+(nrow+1)*nc.YCELL
ncol2=int((xmax-xmin)//RESm)
nrow2=int((ymax-ymin)//RESm)
X=[xmin+RESm*(i+0.5) for i in range(ncol2)]
Y=[ymin+RESm*(i+0.5) for i in range(nrow2)]
x_g, y_g = np.meshgrid(X, Y)
Plon, Plat= pnyc(x_g,y_g, inverse=True)


shp='TOWN_MOI_1090727.shp'
shape = shapefile.Reader(shp)
f=shape.fields
rec=shape.records()
col=[i[0] for i in f[1:]]
df=DataFrame({col[ic]:[rec[i][ic] for i in range(len(rec))] for ic in range(7)})
df.to_csv('record.csv')

plgs,multi=[],[]
for i in range(len(df)):
  tp=shape.shapeRecords()[i].shape.__geo_interface__['type']
  cr=shape.shapeRecords()[i].shape.__geo_interface__['coordinates']
  if len(cr)!=1:
    multi.append(i)
    if type(cr[0][0][0])==tuple:
      plg=[cr[ic][0][:] for ic in range(len(cr))]    
    else:
      plg=[cr[ic][:] for ic in range(len(cr))]    
    plgs.append(plg)
  else:
    plgs.append(cr[0])
[Dplg,mxLon,mnLon,mxLat,mnLat]=[[] for i in range(5)]
for plg in plgs:
  lon=[i[0] for i in plg[:]]
  lat=[i[1] for i in plg[:]]
  crd=[(i,j) for i,j in zip(lat,lon)]
  Dplg.append(crd)
  mxLon.append(np.max(lon))
  mnLon.append(np.min(lon))
  mxLat.append(np.max(lat))
  mnLat.append(np.min(lat))
nplgs=len(df)
DIS=np.zeros(shape=(nrow2,ncol2))
for i in 'mxLon,mnLon,mxLat,mnLat'.split(','):
  exec(i+'=np.array('+i+')')
for j in range(nrow2):
  for i in range(ncol2):
    p1=Point((Plat[j,i],Plon[j,i]))
    idx=np.where((Plat[j,i]-mnLat)*(Plat[j,i]-mxLat)<=0)
    if len(idx[0])==0: continue
    idx2=np.where((Plon[j,i]-mnLon[idx[0][:]])*(Plon[j,i]-mxLon[idx[0][:]])<=0)
    if len(idx2[0])==0: continue
    for n in list(idx[0][idx2[0]]):                                              #loop for each polygons
      if n in multi:continue
      poly = Polygon(Dplg[n])
      if p1.within(poly):                             #boolean to check whether the p1 coordinates is inside the polygon or not
        DIS[j,i]=float(n)
        break
for n in multi:
  idx=np.where((Plat-mnLat[n])*(Plat-mxLat[n])<=0)
  idx2=np.where((Plon[idx[0][:],idx[1][:]]-mnLon[n])*(Plon[idx[0][:],idx[1][:]]-mxLon[n])<=0)
  cr=shape.shapeRecords()[n].shape.__geo_interface__['coordinates']
  if type(cr[0][0][0])==tuple:
    plgs=[cr[ic][0][:] for ic in range(len(cr))]    
  else:
    plgs=[cr[ic][:] for ic in range(len(cr))]    
  for plg in plgs:
    lon=[i[0] for i in plg[:]]
    lat=[i[1] for i in plg[:]]
    crd=[(ii,jj) for ii,jj in zip(lat,lon)]
    for ij in range(len(idx2[0])):
      j=idx[0][idx2[0][ij]]
      i=idx[1][idx2[0][ij]]
      p1=Point((Plat[j,i],Plon[j,i]))
      poly = Polygon(crd)
      if p1.within(poly):                             #boolean to check whether the p1 coordinates is inside the polygon or not
        DIS[j,i]=float(n)

#ncks -O --mk_rec_dmn ROW template_d4_1x1.nc a.nc
#ncks -O --mk_rec_dmn COL b.nc c.nc
#ncks -O -v NO,TFLAG -d TSTEP,0 c.nc template_d4_1x1.nc
#ncrename -v NO,NUM_TOWN $nc
nc = netCDF4.Dataset('template_d4_1x1.nc', 'r+')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
nc.NCOLS=ncol2
nc.NROWS=nrow2
nc.NVARS=1
nc.NSTEPS=1
nc.XCELL=RESm
nc.YCELL=RESm
if nrow!=nrow2 or ncol!=ncol2:
  for j in range(nrow2):
    for i in range(ncol2):
      nc.variables['NUM_TOWN'][0,0,j,i]=DIS[j,i]
else:
  nc.variables['NUM_TOWN'][0,0,:nrow,:ncol]=DIS[:,:]
nc.close()	
