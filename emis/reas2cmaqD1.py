import numpy as np
import netCDF4
import sys, os
from pandas import *

from pyproj import Proj

Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)


os.system('~/bin/findc "REASv*" >fnames.txt')
os.system('for i in $(cat fnames.txt);do echo $i $(grep "/mon" $i|cut -d[ -f1);done >spec.txt')
with open('spec.txt','r') as f:
  l=[i.strip('\n').strip('_') for i in f]
fname_spec={i.split()[0]:i.split()[1] for i in l}
spec=list(set(fname_spec.values()))
spec.sort()
nspec=len(spec)
specn={spec[i]:i for i in range(nspec)}
fnames=list(fname_spec)
nmv=set([fname_spec[f] for f in fnames if 'NMV' in f])
specNonV=set([fname_spec[f] for f in fnames if 'NMV' not in f]) #共9種CNPS，part(BC,OC,PM2.5,PM10),CO2,ACNS

cate=['DOMESTIC', 'EXTRACTION', 'FERTILIZER', 'INDUSTRY', 'MISC', 'SOLVENTS', 'WASTE',
'ROAD_TRANSPORT', 'OTHER_TRANSPORT', 'POWER_PLANTS_NON-POINT',  'MANURE_MANAGEMENT']
cate.sort()
ncat=len(cate)
catn={cate[i]:i for i in range(ncat)}


#read the coordinates
lon,lat=[],[]
for fname in fnames:
  if '0.25x0.25' not in fname:continue
  with open(fname,'r') as f:
    l=[i.strip('\n').strip('_') for i in f]
  if len(l)<=9:continue
  lon=list(set(lon+[float(i.split()[0]) for i in l[9:]]))
  lat=list(set(lat+[float(i.split()[1]) for i in l[9:]]))
for ll in ['lon','lat']:
  exec(ll+'.sort()')
  exec('n'+ll+'=nn=int(('+ll+'[-1]-'+ll+'[0])/0.25)+1')
  exec(ll+'M=['+ll+'[0]+0.25*i for i in range(nn)]')
  exec(ll+'n={l:'+ll+'M.index(l) for l in '+ll+'M}')

# read the monthly emissions
var=np.zeros(shape=(ncat,nspec,12,nlat,nlon))
for fname in fnames:
  if '0.25x0.25' not in fname:continue
  icat=-1
  for c in cate:
    if c in fname:icat=catn[c]
  if icat==-1:continue
  ispec=specn[fname_spec[fname]]
  with open(fname,'r') as f:
    l=[i.strip('\n').strip('_') for i in f]
  if len(l)<=9:continue
  lenl=len(l[9:])
  arr=np.array([float(i.split()[j]) for i in l[9:] for j in range(14)]).reshape(lenl,14)
  for i in range(lenl):
    var[icat,ispec,:,latn[arr[i,1]],lonn[arr[i,0]]]=arr[i,2:]

df=read_csv('REAS2CMAQ.csv')
c_dup=[i for i in set(df.CMAQ) if list(df.CMAQ).count(i)>1]
REAS2CMAQ={i:j for i,j in zip(df.REAS,df.CMAQ) if i in spec}
r_dup=[i for i in REAS2CMAQ if REAS2CMAQ[i] in c_dup and i in spec]
r_mole={i:j for i,j in zip(df.REAS,df.mole)}
mw={i:j for i,j in zip(df.REAS,df.wt)}

for icat in range(ncat):
  fname=cate[icat]+'_D1.nc'
  os.system('cp templateD1.nc '+fname)
  nc = netCDF4.Dataset(fname, 'r+')

# elongate the new ncf
  for t in range(12):
    nc['TFLAG'][t,:,1]=t*100*100
  nc['TFLAG'][:,:,0]=nc.SDATE

# search for newgrid points first time
  if icat==0:
    V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
    nt,nlay,nrow,ncol=nc.variables[V[3][0]].shape
    X1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
    Y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
    X2d,Y2d=np.meshgrid(X1d,Y1d)
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
# fill the new nc file      
  for v in V[3]:
    nc[v][:]=0.

#summation scheme, for D1 resolution(81Km)
# len(set(lon_ss))==len(lon_ss) and len(set(lat_ss))==len(lat_ss):
# variables need to accumulate
  for v in r_dup:
    ispec=specn[v]
    if np.sum(var[icat,ispec,:,:,:])==0.:continue
    vc=REAS2CMAQ[v]
    if vc not in V[3]:continue
    for j in range(nrow):
      for i in range(ncol):
        nc[vc][:,0,j,i]+=np.sum(var[icat,ispec,:,lat_ss[j,i]:lat_ss[j+1,i+1],lon_ss[j,i]:lon_ss[j+1,i+1]],axis=(1,2))*r_mole[v]/mw[v]
# variables no need to accumulate
  for v in set(spec)-set(r_dup):
    ispec=specn[v]
    if np.sum(var[icat,ispec,:,:,:])==0.:continue
    if v not in REAS2CMAQ:continue
    vc=REAS2CMAQ[v]
    if vc not in V[3]:continue
    for j in range(nrow):
      for i in range(ncol):
        nc[vc][:,0,j,i]=np.sum(var[icat,ispec,:,lat_ss[j,i]:lat_ss[j+1,i+1],lon_ss[j,i]:lon_ss[j+1,i+1]],axis=(1,2))*r_mole[v]/mw[v]
  nc.close()
