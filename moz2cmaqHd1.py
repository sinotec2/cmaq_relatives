import numpy as np
import netCDF4
import os,sys, datetime, json
from pyproj import Proj


Latitude_Pole, Longitude_Pole = 23.61000, 120.990
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, 
		lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(1601)')
yrmn=sys.argv[1]

#read the mozart model results
fname='moz_41_20'+yrmn+'.nc'

ncM = netCDF4.Dataset(fname,'r')
v4M=list(filter(lambda x:ncM.variables[x].ndim==4, [i for i in ncM.variables]))
ntM,nlayM,nrowM,ncolM=(ncM.variables[v4M[0]].shape[i] for i in range(4))
lonM=[ncM.XORIG+ncM.XCELL*i for i in range(ncolM)]
latM=[ncM.YORIG+ncM.YCELL*i for i in range(nrowM)]

#load mz2cmaq map
with open('cb6_new.json','r') as f:
  mz2cm=json.load(f)
with open('cb6_newNum.json','r') as f:
  mz2cmNum=json.load(f)
with open('lay2VGLEVLS.json','r') as f:
  lay2VGLEVLS=json.load(f)
lay2VGLEVLS.update({'40':40})

#read the template(s)
fname='ICON_d1_20'+yrmn+'.nc'
nc = netCDF4.Dataset(fname,'r')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
X=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
Y=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
lon, lat= pnyc(X,Y, inverse=True)
lon_ss=np.searchsorted(lonM,lon)
lat_ss=np.searchsorted(latM,lat)
tflag=nc.variables['TFLAG'][:,0,:]
zi=np.zeros(shape=(nlay,nrow,ncol))

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
A5=np.zeros(shape=(len(v4M),ntM,nlayM,nrowM,ncolM))
for ix in range(len(v4M)):
  for k in range(nlayM):
    A5[ix,:,k,:,:]=ncM.variables[v4M[ix]][:,lay2VGLEVLS[str(k)],:,:]*1000.*1000. #Volume Mixing Ratio to PPM
ncM.close()

#perform the horizontal interpolation and write results
for t in range(nt):
  td=tflag[t,0]*100+int(tflag[t,1]/10000)
#  if td<201636400:continue
#  if td!=201600418:continue
  fnamet='ICON_'+str(tflag[t,0])+'{:02d}'.format(int(tflag[t,1]/10000))+'.d1'
  print (fnamet)
  nc = netCDF4.Dataset(fnamet,'r+')
  for x in v4M:
    nc.variables[mz2cm[x]][0,:,:,:]=zi[:,:,:]
  
  for jcrs in range(nrow):
    jmz=lat_ss[jcrs]
    for icrs in range(ncol):
      imz=lon_ss[icrs]
      rx=(lon[icrs]-lonM[imz-1])/(lonM[imz]-lonM[imz-1])
      ry=(lat[jcrs]-latM[jmz-1])/(latM[jmz]-latM[jmz-1])
      A2x=A5[:,t,:,jmz,imz]*rx+A5[:,t,:,jmz,imz-1]*(1-rx)
      A2y=A5[:,t,:,jmz,imz]*ry+A5[:,t,:,jmz-1,imz]*(1-ry)
      A2=(A2x+A2y)/2.
      for x in v4M:
        nc.variables[mz2cm[x]][0,:,jcrs,icrs]+=A2[v4M.index(x),:-1]*mz2cmNum[x]
  nc.close()