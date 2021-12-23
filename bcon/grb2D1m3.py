#argumens numNest gribFname
import netCDF4
import numpy as np
import datetime
from scipy.interpolate import griddata
import json

from pyproj import Proj
import sys,os,subprocess
from dtconvertor import dt2jul, jul2dt


for v in ['mws','dic','nms_gas','nms_part']:
  with open(v+'.json', 'r') as jsonfile:
    exec(v+'=json.load(jsonfile)')
uts=['PPM',"ug m-3          "]
l34=['21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', 
     '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
l40=['21', '21', '22', '22', '23', '24', '24', '25', '25', '26', '27', '28', '28', '29', '30', '31', '32', '32', '33', '34', 
     '35', '36', '37', '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
d40_23={39-k:l34.index(l40[k]) for k in range(40)}
byr=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n')[-2:]
#read a BC file as rate base
fname='/nas1/cmaqruns/2019base/data/bcon/BCON_v53_1912_run5_regrid_20191201_TWN_3X3'
nc = netCDF4.Dataset(fname,'r')
Vb=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
rate={}
for v in nms_part:
  nms=nms_part[v]
  for nm in nms:
    if nm not in Vb[2]:sys.exit(v+' not in BCON file')
  avg=[np.mean(nc.variables[nm][:]) for nm in nms]
  sum_avg=sum(avg)
  if sum_avg==0:sys.exit('sum_avg==0')
  ratev=[avg[i]/sum_avg for i in range(len(avg))]
  rate.update({v:ratev})
for v in nms_gas:
  rate.update({v:[1.]})

#read the merged grib files (ncl_convert2nc)
#lay,row in reversed directions
fname=sys.argv[1]
nc = netCDF4.Dataset(fname,'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))
#read the timestamp in nc and store at /expand the nc1
SDATE=[datetime.datetime.strptime(''.join([str(i, encoding='utf-8') for i in list(nc.variables[V[1][0]][t, :])]),\
 '%m/%d/%Y (%H:%M)') for t in range(nt)]
bdate,edate=SDATE[0],SDATE[-1]
delt=edate-bdate
ntA=int(delt.total_seconds()/3600.)
JuliHr=[int((bdate+datetime.timedelta(hours=t)).strftime("%Y%j%H")) for t in range(ntA)]

N='D1'
tmps={'D1':'templateD1.ncV49K34','D2':'templateD2.ncV49K34'}
path='./'
fnameO=fname.replace('.nc',N+'.m3.nc')
if not os.path.exists(fnameO):os.system('cp '+path+tmps[N]+' '+fnameO)
nc1= netCDF4.Dataset(fnameO,'r+')
V1=[list(filter(lambda x:nc1.variables[x].ndim==j, [i for i in nc1.variables])) for j in [1,2,3,4]]
nv1=len(V1[3])
nt1,nlay1,nrow1,ncol1=nc1.variables[V1[3][0]].shape
if nt1<ntA:
  print('expand the matrix')
  for t in range(ntA):
    nc1.variables['TFLAG'][t,0,0]=0
if nt1>ntA:
  nc1.close()
  ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
  os.system(ncks+' -O -d TSTEP,0,'+str(ntA-1)+' '+fnameO+' '+fnameO+'_tmp;mv '+fnameO+'_tmp '+fnameO) 
  nc1= netCDF4.Dataset(fnameO,'r+')
nc1.SDATE=JuliHr[0]//100
nc1.STIME=JuliHr[0]%100*10000
var=np.zeros(shape=(ntA,nc1.NVARS,2))
var[:,:,0]=np.array([i//100 for i in JuliHr])[:,None]
var[:,:,1]=np.array([i%100  for i in JuliHr])[:,None]*10000
nc1.variables['TFLAG'][:,:,:]=var[:,:,:]
Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40,
        lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

xlon, xlat = nc.variables['lon_0'][:].flatten(), np.flip(nc.variables['lat_0'][:].flatten())
lonm, latm = np.meshgrid(xlon, xlat)
x,y=pnyc(lonm,latm, inverse=False)

#interpolation indexing
x1d=[nc1.XORIG+nc1.XCELL*i for i in range(ncol1)]
y1d=[nc1.YORIG+nc1.YCELL*i for i in range(nrow1)]
x1,y1=np.meshgrid(x1d, y1d)
maxx,maxy=x1[-1,-1],y1[-1,-1]
minx,miny=x1[0,0],y1[0,0]
boo=(abs(x) <= (maxx - minx) /2+nc1.XCELL*10) & (abs(y) <= (maxy - miny) /2+nc1.YCELL*10)
idx = np.where(boo)
mp=len(idx[0])
xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]

print('read the density of air')
dlay=np.array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30, 32, 34, 35, 37, 39])
dens=np.zeros(shape=(ntA,40, nrow1, ncol1))
caldat=list(set([int((bdate+datetime.timedelta(hours=t)).strftime("%Y%m%d")) for t in range(ntA)]))
caldat.sort()
for c in caldat:
  iday=caldat.index(c)
  fname='/nas1/cmaqruns/20'+byr+'base/data/mcip/RHO/RHO.'+str(c)+'.nc'
  ncr = netCDF4.Dataset(fname,'r')
  ntr=min(24,ncr.dimensions['TSTEP'].size)
  t1=iday*24
  t2=min(ntA,t1+min(24,ntr))
  hrs=t2-t1
  dens[t1:t2,:,:,:]=ncr.variables['DENS'][:hrs,:,:,:] *1E9 #(kg to microgram)
dens2=np.zeros(shape=(ntA,nlay1, nrow1, ncol1))
for k in range(nlay1):
  dens2[:,k,:,:]=dens[:,dlay[k],:,:]
var=np.zeros(shape=(nt, nlay, nrow, ncol))
zz=np.zeros(shape=(nt, nlay1, nrow1, ncol1))
var2=np.zeros(shape=(ntA,nlay1, nrow1, ncol1))
print('fill the matrix')
for v in list(nms_gas)+list(nms_part) :
  var[:,:,:,:]=np.flip(nc.variables[v][:,:,:,:], [1,2])
  for t in range(nt):
    c = np.array([var[t,:,idx[0][i], idx[1][i]] for i in range(mp)])
    for k in range(nlay1):
      zz[t,k,:,: ] = griddata(xyc, c[:,k], (x1, y1), method='linear')
  for t in range(0,ntA,3):
    t3=int(t/3)
    var2[t+0,:,:,:]=zz[t3,:,:,:]
    var2[t+1,:,:,:]=zz[t3,:,:,:]*2/3+zz[t3+1,:,:,:]*1/3
    var2[t+2,:,:,:]=zz[t3,:,:,:]*1/3+zz[t3+1,:,:,:]*2/3
  if v in nms_gas:
    nc1.variables[nms_gas[v]][:]=var2[:]*rate[v][0] * 28.E6/mws[dic[v]] #mixing ratio to ppm
  else:
#    unit=1E9*dens[:] #28.E6/mvol #mixing ratio(kg/kg) to microgram/M3
    nms=nms_part[v]
    for nm in nms:
      nc1.variables[nm][:]+=var2[:] * rate[v][nms.index(nm)] * dens2[:]
  print(v)

nc1.SDATE,nc1.STIME=nc1.variables['TFLAG'][0,0,:]
nc1.NLAYS=nlay1
nc1.TSTEP=10000
nc1.close()

