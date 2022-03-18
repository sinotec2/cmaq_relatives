import numpy as np
import netCDF4
import sys, os
from pandas import *
from pyproj import Proj
from scipy.interpolate import griddata

spec='BC CO NH3 NMVOC NOx OC PM10 PM2.5 SO2'.split()
nspec=len(spec)
specn={spec[i]:i for i in range(nspec)}

ny,nx=5400,6800
var=np.zeros(shape=(9+1,ny,nx))
for s in spec:
  fname='DensGlobD6'+s+'.nc'
  nc = netCDF4.Dataset(fname,'r')
  v='emi_so2'
  var[specn[s],:,:]=nc[v][:,:]
var[-1,:,:]=var[specn['PM10'],:,:]-var[specn['PM2.5'],:,:]
var=np.where(var<0,0,var)
spec+=['PMC']
specn.update({'PMC':len(spec)-1})

lonM=list(nc['lon'][:])
latM=list(nc['lat'][:])
lonm, latm = np.meshgrid(lonM, latM)
for ll in ['lon','lat']:
  exec(ll+'n={'+ll+'M[l]:l for l in range(len('+ll+'M))}')


DD=sys.argv[1]
#interpolation indexing from template  # get the argument
tail=DD+'.nc'
fname='template'+tail
nc = netCDF4.Dataset(fname, 'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=nc.variables[V[3][0]].shape
x1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
X2d,Y2d=np.meshgrid(x1d,y1d)
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=nc.YCENT, lon_0=nc.XCENT, x_0=0, y_0=0.0)
lon, lat= pnyc(X2d,Y2d, inverse=True)
lon_ss, lat_ss= np.zeros(shape=(nrow+1,ncol+1), dtype=int)-1, np.zeros(shape=(nrow+1,ncol+1), dtype=int)-1
for ll in ['lon','lat']:
  llss =ll+'_ss'
  lls = np.zeros(shape=(nrow,ncol), dtype=int)-1
  exec('lls=np.searchsorted('+ll+'M,'+ll+')')
  exec(llss+'[:nrow,:ncol]=lls[:,:]')
  for i in range(ncol):
    exec(llss+'[nrow,i]=lls[-1,i]*2-lls[-2,i]')
  for j in range(nrow):
    exec(llss+'[j,ncol]=lls[j,-1]*2-lls[j,-2]')
  exec(llss+'[nrow,ncol]=lls[-1,-1]*2-lls[-2,-2]')


# spec name dict
EDGAR2EMIS={'BC':'PEC','OC':'POA','PM2.5':'FPRM','PMC':'CPRM'}
mw={i:1 for i in EDGAR2EMIS}
mw.update({'CO':28,'NH3':17,'NMVOC':58,'NOx':46,'SO2':64})
EDGAR2EMIS.update({'NOx':'NO2'})
EDGAR2EMIS.update({i:i for i in 'CO NH3 SO2'.split()})
VOCs=['ALD2','ALDX','BENZ','ETH','ETHA','ETHY','ETOH','FORM','HONO','IOLE','ISOP','KET','MEOH','OLE','PAR','PRPA','TERP','TOL','XYL']
nv=len(VOCs)

fname='EDGAR'+tail
os.system('cp template'+tail+' '+fname)
nc = netCDF4.Dataset(fname, 'r+')

# elongate the new ncf
# fill the new nc file
for v in V[3]:
  nc[v][:]=0.

#summation scheme, for resolution >> 500m (0.005deg)
for v in spec:
  if v not in EDGAR2EMIS.keys():continue #(PM10 and NMVOC)
  ispec=specn[v]
  vc=EDGAR2EMIS[v]
  if vc not in V[3]:continue
  for j in range(nrow):
    for i in range(ncol):
#Since the unit is in intensive mode, must take mean not sum
      zz=np.mean(var[ispec,lat_ss[j,i]:lat_ss[j+1,i+1],lon_ss[j,i]:lon_ss[j+1,i+1]],axis=(0,1))
      nc[vc][0,0,j,i]=zz/mw[v]*1000.*nc.XCELL*nc.YCELL
  print (v)
fname='2015_'+DD+'.nc'
nc0 = netCDF4.Dataset(fname, 'r')
Vspl=np.zeros(shape=(nv,nrow,ncol))
for v in VOCs:
  iv=VOCs.index(v)
  Vspl[iv,:,:]+=np.sum(nc0[v][:,0,:,:],axis=0)
vss=np.sum(Vspl[:,:,:],axis=0)
iidx=np.where(vss>0)
Vspl_mean=np.array([np.mean(Vspl[i,iidx[0],iidx[1]]) for i in range(nv)])
Vspl_mean/=sum(Vspl_mean)

iidx=np.where(vss==0)
vss=np.where(vss==0,1,vss)
Vspl[:,:,:]/=vss[None,:,:]
for i in range(nv):
  Vspl[i,iidx[0],iidx[1]]=Vspl_mean[i]
v='NMVOC'
ispec=specn[v]
mwv=mw[v]
for j in range(nrow):
  for i in range(ncol):
    zz=np.mean(var[ispec,lat_ss[j,i]:lat_ss[j+1,i+1],lon_ss[j,i]:lon_ss[j+1,i+1]],axis=(0,1))
    for v in VOCs:
      iv=VOCs.index(v)
      nc[v][0,0,j,i]=zz*Vspl[iv,j,i]/mwv*1000.*nc.XCELL*nc.YCELL
nc.close()
