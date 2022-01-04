import numpy as np
import netCDF4
import sys, os
from pandas import *
from pyproj import Proj
from scipy.interpolate import griddata

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

#read the coordinates
lon,lat=[],[]
for fname in fnames:
  if '0.25x0.25' not in fname:continue
  with open(fname,'r') as f:
    l=[i.strip('\n').strip('_') for i in f]
  if len(l)<=9:continue
  lon=list(set(lon+[float(i.split()[0]) for i in l[9:]]))
  lat=list(set(lat+[float(i.split()[1]) for i in l[9:]]))
# generate the x and y arrays for REAS datafile
for ll in ['lon','lat']:
  exec(ll+'.sort()')
  exec('n'+ll+'=nn=int(('+ll+'[-1]-'+ll+'[0])/0.25)+1')
  exec(ll+'M=['+ll+'[0]+0.25*i for i in range(nn)]')
  exec(ll+'n={l:'+ll+'M.index(l) for l in '+ll+'M}')
lonm, latm = np.meshgrid(lonM, latM)
x,y=pnyc(lonm,latm, inverse=False)

#interpolation indexing from template  # get the argument
tail=sys.argv[1]+'.nc'
fname='template'+tail
nc = netCDF4.Dataset(fname, 'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=nc.variables[V[3][0]].shape
x1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x1,y1=np.meshgrid(x1d,y1d)
maxx,maxy=x1[-1,-1],y1[-1,-1]
minx,miny=x1[0,0],y1[0,0]
boo=(abs(x) <= (maxx - minx) /2+nc.XCELL*10) & (abs(y) <= (maxy - miny) /2+nc.YCELL*10)
idx = np.where(boo)
mp=len(idx[0])
xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]

# category of REAS emission files
cate=['DOMESTIC', 'EXTRACTION', 'FERTILIZER', 'INDUSTRY', 'MISC', 'SOLVENTS', 'WASTE',
'ROAD_TRANSPORT', 'OTHER_TRANSPORT', 'POWER_PLANTS_NON-POINT',  'MANURE_MANAGEMENT']
cate.sort()
ncat=len(cate)
catn={cate[i]:i for i in range(ncat)}

# read the monthly REAS emissions and store in var matrix
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
  print(fname)

# spec name dict
df=read_csv('REAS2CMAQ.csv')
c_dup=[i for i in set(df.CMAQ) if list(df.CMAQ).count(i)>1]
REAS2CMAQ={i:j for i,j in zip(df.REAS,df.CMAQ) if i in spec}
r_dup=[i for i in REAS2CMAQ if REAS2CMAQ[i] in c_dup and i in spec]

icat=int(sys.argv[2])
#for icat in range(ncat):
fname=cate[icat]+'_'+tail
os.system('cp template'+tail+' '+fname)
nc = netCDF4.Dataset(fname, 'r+')

# elongate the new ncf
for t in range(12):
  nc['TFLAG'][t,:,1]=t*100*100
nc['TFLAG'][:,:,0]=nc.SDATE
# fill the new nc file
for v in V[3]:
  nc[v][:]=0.

#interpolation scheme, for D0/D2 resolution(15Km/27Km)
for v in spec:
  ispec=specn[v]
  if np.sum(var[icat,ispec,:,:,:])==0.:continue
  if v not in REAS2CMAQ:continue
  vc=REAS2CMAQ[v]
  if vc not in V[3]:continue
  zz=np.zeros(shape=(12,nrow,ncol))
  for t in range(12):
    c = np.array([var[icat,ispec,t,idx[0][i], idx[1][i]] for i in range(mp)])
    zz[t,:,: ] = griddata(xyc, c[:], (x1, y1), method='linear')
  zz=np.where(np.isnan(zz),0,zz)
  if v in r_dup:
    nc[vc][:,0,:,:]+=zz[:,:,:]
  else:
    nc[vc][:,0,:,:] =zz[:,:,:]
nc.close()
