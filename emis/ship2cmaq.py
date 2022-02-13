from pandas import *
import datetime
import netCDF4
import numpy as np
import os,sys
from calendar import monthrange
from dtconvertor import dt2jul, jul2dt
from pyproj import Proj
from scipy.interpolate import griddata


pi=3.14159265359
peri_x=40075.02
peri_y=40008
r_x=peri_x/2./pi
r_y=peri_y/2./pi

path=''
fname=path+'NOx_allHeights_2015-01-01T00_2015-12-31T00.nc'
nc = netCDF4.Dataset(fname,'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nrow,ncol,nt=(nc[V[0][i]].shape[0] for i in range(3))
NOx=np.array(nc.variables['NOx'][:,:,:])
lst={'lat':list(nc.variables['latitude'][:])}
lst.update({'lon':list(nc.variables['longitude'][:])})
lst.update({'time':[i for i in range(nt)]})

df=read_csv('shp_sum.csv')
dfs=read_csv('REAS2CMAQ.csv')

spec=[i.lower() for i in dfs.REAS];cmaq=list(dfs.CMAQ);mw=list(dfs.wt);mole=list(dfs.mole)
spz={i:j for i,j in zip(spec,cmaq)}
CBM=[i for i in set(cmaq) if cmaq.count(i)>1]
mws={i:j for i,j in zip(spec,mw)}
mol={i:j for i,j in zip(spec,mole)}
facG=1E3/24/3600. # 10^3 for kg/day to gmole/s
unit_SHIP={i:facG/mw for i,mw in zip(spec,mw)}

#calculate the area of each grid cell
dlon=(max(lst['lon'])-min(lst['lon']))/(ncol-1)
dlat=(max(lst['lat'])-min(lst['lat']))/(nrow-1)
lat,lon=np.array(lst['lat']),np.array(lst['lon'])
rad=abs(lat/90.)*pi/2.
r=(r_x*np.cos(rad)+r_y*np.sin(pi/2.-rad))/2.
dx=2.*pi*r * dlon/360.
dx=list(dx)+[dx[-1]]
dx=np.array([(dx[i]+dx[i+1])/2. for i in range(nrow)])  
dy=dlat/180.*(peri_x*np.cos(rad)**2+peri_y*np.sin(rad)**2)/2.
area=dx*dy
NOx=NOx/area[None,:,None]

yrmn=sys.argv[1] #given yr. month

fname='shipD0_'+yrmn+'.nc'
m=int(yrmn[2:])
y=2000+int(yrmn[:2])
os.system('cp templateD0.nc '+fname)
nc = netCDF4.Dataset(fname,'r+')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
x1d=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
y1d=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x1,y1=np.meshgrid(x1d,y1d)
maxx,maxy=x1[-1,-1],y1[-1,-1]
minx,miny=x1[0,0],y1[0,0]

bdate=datetime.datetime(y,m,1)+datetime.timedelta(days=-1)
ntm=(monthrange(y,m)[1]+2)*24+1
sdate=[bdate+datetime.timedelta(hours=t) for t in range(ntm)]
js=np.array([int(datetime.datetime.strftime(dt,"%j")) for dt in sdate],dtype=int)

#reducing NOx in day dimension
NOx=NOx[min(js):max(js)+1,:,:]*nc.XCELL/1000*nc.YCELL/1000
js=js-min(js)
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=nc.P_ALP, lat_2=nc.P_BET,lat_0=nc.YCENT, lon_0=nc.XCENT, x_0=0, y_0=0.0)
lonm, latm = np.meshgrid(lst['lon'],lst['lat'])
x,y=pnyc(lonm,latm, inverse=False)
boo=(abs(x) <= (maxx - minx) /2+nc.XCELL*10) & (abs(y) <= (maxy - miny) /2+nc.YCELL*10)
idx = np.where(boo)
mp=len(idx[0])
xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]

#expansion in TFLAG
for t in range(ntm):
  nc['TFLAG'][t,:,0]=dt2jul(sdate[t])[0]
  nc['TFLAG'][t,:,1]=dt2jul(sdate[t])[1]
#unmasking all variables
for v in V[3]:
  nc[v][:]=0.

dfm=df.loc[(df.mon==m)].reset_index(drop=True)
dfm.spec=[i.lower() for i in dfm.spec]
vNOx=list(dfm.loc[dfm.spec=='NOx','sum_file'])[0]
if vNOx==0.:sys.exit('vNOx==0')
for j in range(min(js),max(js)+1):
  idt=np.where(js==j)[0]
  NOx2d=NOx[js[idt[0]],:,:]
  var=np.zeros(shape=(nrow,ncol))
  c = NOx2d[idx[0][:],idx[1][:]]
  var[:,:] = griddata(xyc, c[:], (x1, y1), method='linear')
  for s in set(dfm.spec):
    if s not in spec:continue
    if spz[s]=='None': continue
    if spz[s] not in V[3]: continue
    if mws[s]==0.:continue
    rat=list(dfm.loc[dfm.spec==s,'sum_file'])[0]/vNOx
    if s=='NOx': rat=1.
    arr=np.zeros(shape=(len(idt),nrow,ncol))
    arr[:,:,:]=var[None,:,:]*rat*unit_SHIP[s]
    if spz[s] in CBM:
      nc[spz[s]][idt[0]:idt[-1]+1,0,:,:]+=arr[:,:,:]
    else:
      nc[spz[s]][idt[0]:idt[-1]+1,0,:,:] =arr[:,:,:]
nc.close()
  

