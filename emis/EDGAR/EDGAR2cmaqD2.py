import numpy as np
import netCDF4
import sys, os
from pandas import *
from pyproj import Proj
from scipy.interpolate import griddata

spec='BC CO NH3 NMVOC NOx OC PM10 PM2.5 SO2'.split()
nspec=len(spec)
specn={spec[i]:i for i in range(nspec)}

ny,nx=1800,3600
var=np.zeros(shape=(9+1,ny,nx))
for s in spec:
  fname='v50_'+s+'_2015.0.1x0.1.nc'
  nc = netCDF4.Dataset(fname,'r')
  v='emi_'+s.lower()
  var[specn[s],:,:]=nc[v][:,:]
var[-1,:,:]=var[specn['PM10'],:,:]-var[specn['PM2.5'],:,:]
var=np.where(var<0,0,var)
spec+=['PMC']
specn.update({'PMC':len(spec)-1})

lonM=[  0.05+i*0.1 for i in range(nx)]
latM=[-89.95+i*0.1 for i in range(ny)]
lonm, latm = np.meshgrid(lonM, latM)


DD=sys.argv[1]
#interpolation indexing from template  # get the argument
tail=DD+'.nc'
fname='template'+tail
nc = netCDF4.Dataset(fname, 'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=nc.variables[V[3][0]].shape
x1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x1,y1=np.meshgrid(x1d,y1d)
maxx,maxy=x1[-1,-1],y1[-1,-1]
minx,miny=x1[0,0],y1[0,0]

pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=nc.YCENT, lon_0=nc.XCENT, x_0=0, y_0=0.0)
x,y=pnyc(lonm,latm, inverse=False)

boo=(x<=maxx+nc.XCELL*10) & (x>=minx-nc.XCELL*10) & (y<=maxy+nc.YCELL*10) & (y>=miny-nc.YCELL*10)
idx = np.where(boo)
mp=len(idx[0])
xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]

# spec name dict
EDGAR2EMIS={'BC':'PEC','OC':'POA','PM2.5':'FPRM','PMC':'CPRM'}

spec='BC CO NH3 NMVOC NOx OC PM10 PM2.5 SO2'.split()
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

#interpolation scheme, for D0/D2 resolution(15Km/27Km)
for v in spec:
  if v not in EDGAR2EMIS.keys():continue #(PM10 and NMVOC)
  ispec=specn[v]
  vc=EDGAR2EMIS[v]
  if vc not in V[3]:continue
  zz=np.zeros(shape=(nrow,ncol))
  c = np.array([var[ispec,idx[0][i], idx[1][i]] for i in range(mp)])
  zz[:,: ] = griddata(xyc, c[:], (x1, y1), method='linear')
  zz=np.where(np.isnan(zz),0,zz)
  nc[vc][0,0,:,:] =zz[:,:]/mw[v]*1000.*nc.XCELL*nc.YCELL
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
zz=np.zeros(shape=(nrow,ncol))
c = np.array([var[specn[v],idx[0][i], idx[1][i]] for i in range(mp)])
zz[:,: ] = griddata(xyc, c[:], (x1, y1), method='linear')
zz=np.where(np.isnan(zz),0,zz)/mw[v]*1000.*nc.XCELL*nc.YCELL
for v in VOCs:
  iv=VOCs.index(v)
  nc[v][0,0,:,:]=zz[:,:]*Vspl[iv,:,:]
  
nc.close()
