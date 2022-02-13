#argumens numNest gribFname
import netCDF4
import numpy as np
import datetime
from scipy.interpolate import griddata
import json

from pyproj import Proj
import sys,os,subprocess
from dtconvertor import dt2jul, jul2dt


def trans4_3(tt,ll,mm,ii):
#4-d transform to 3-d
  N=[np.zeros(shape=(tt,ll,mm),dtype=int) for i in range(4)]
  N[0][:,:,:]=np.array([t for t in range(tt)])[:,None,None]
  N[1][:,:,:]=np.array([k for k in range(ll)])[None,:,None]
  N[2][:,:,:]=ii[0][None,None,:]
  N[3][:,:,:]=ii[1][None,None,:]
  for n in range(4):
    N[n]=N[n].flatten()
  return N


for v in ['mws','dic','nms_gas','nms_part']:
  with open(v+'.json', 'r') as jsonfile:
    exec(v+'=json.load(jsonfile)')
uts=['PPM',"ug m-3          "]
l34=['21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', 
     '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
l40=['21', '21', '22', '22', '23', '24', '24', '25', '25', '26', '27', '28', '28', '29', '30', '31', '32', '32', '33', '34', 
     '35', '36', '37', '38', '39', '40', '42', '43', '44', '46', '47', '48', '49', '50', '51', '53', '54', '56', '57', '59']
d40_34={k:l34.index(l40[k]) for k in range(40)}
byr=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n').split('/')[3][2:4]
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
ntA=max([1,int(delt.total_seconds()/3600.)])
JuliHr=[int((bdate+datetime.timedelta(hours=t)).strftime("%Y%j%H")) for t in range(ntA)]

fnameO=sys.argv[2] #weii-prepared BCON file, 
if not os.path.exists(fnameO):sys.exit('BCON file not exist')
nc1= netCDF4.Dataset(fnameO,'r+')
V1=[list(filter(lambda x:nc1.variables[x].ndim==j, [i for i in nc1.variables])) for j in [1,2,3,4]]
nv1=len(V1[2])
nt1,nlay1,nbnd1=nc1.variables[V1[2][0]].shape
#if nt1>ntA:sys.exit('BCON file longer than GRB file ')
nc1.SDATE=JuliHr[0]//100
nc1.STIME=JuliHr[0]%100*10000
var=np.zeros(shape=(ntA,nc1.NVARS,2))
var[:,:,0]=np.array([i//100 for i in JuliHr])[:,None]
var[:,:,1]=np.array([i%100  for i in JuliHr])[:,None]*10000
nc1.variables['TFLAG'][:,:,:]=var[:,:,:]
for v in V1[2]:
  nc1[v][:]=0.
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=nc1.P_ALP, lat_2=nc1.P_BET,lat_0=nc1.YCENT, lon_0=nc1.XCENT, x_0=0, y_0=0.0)
xlon, xlat = nc.variables['lon_0'][:].flatten(), np.flip(nc.variables['lat_0'][:].flatten())
lonm, latm = np.meshgrid(xlon, xlat)
x,y=pnyc(lonm,latm, inverse=False)

#interpolation indexing
nrow1,ncol1=nc1.NROWS,nc1.NCOLS
nrow0,ncol0=nc1.NROWS+5,nc1.NCOLS+5
x1d=[nc1.XORIG+nc1.XCELL*(i-2) for i in range(ncol0)]
y1d=[nc1.YORIG+nc1.YCELL*(i-2) for i in range(nrow0)]
x1,y1=np.meshgrid(x1d, y1d)
i0,j0=1,1
i1,j1=i0+ncol1+1,j0+nrow1+1
idx=[(j0,i) for i in range(i0+1,i1+1)]  +   [(j,i1) for j in range(j0+1,j1+1)] + \
    [(j1,i) for i in range(i1-1,i0-1,-1)] + [(j,i0) for j in range(j1-1,j0-1,-1)]
idxo=np.array(idx,dtype=int).flatten().reshape(nbnd1,2).T
x1,y1=x1[idxo[0],idxo[1]],y1[idxo[0],idxo[1]]
maxx,maxy=max(x1),max(y1)
minx,miny=min(x1),min(y1)
boo=(abs(x) <= (maxx - minx) /2+nc1.XCELL*10) & (abs(y) <= (maxy - miny) /2+nc1.YCELL*10)
idx = np.where(boo)
mp=len(idx[0])
xyc= [(x[idx[0][i],idx[1][i]],y[idx[0][i],idx[1][i]]) for i in range(mp)]
xyc=np.array(xyc).T

idxd=np.zeros(shape=(nbnd1),dtype=int)
for p in range(nbnd1):
  dist=(xyc[0]-x1[p])**2+(xyc[1]-y1[p])**2
  idxd[p]=np.where(dist==np.min(dist))[0][0]

# inner bndy for RHO
i0,j0=0,0
i1,j1=ncol1-1,nrow1-1
idxb=[(j0,i) for i in range(ncol1)] +[(j0,i1)] +   [(j,i1) for j in range(nrow1)] +[(j1,i1)] + \
    [(j1,i) for i in range(i1,i0-1,-1)] +[(j1,i0)] + [(j,i0) for j in range(j1,j0-1,-1)]+[(j0,i0)]
idxb=np.array(idxb,dtype=int).flatten().reshape(nbnd1,2).T

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
#4-d transform to 3-d
N=trans4_3(ntA,nlay1, nbnd1,idxb)
dens2=np.zeros(shape=(ntA,nlay1, nbnd1))
if nlay1==40:
  dens2[:,:,:]=dens[N[0],N[1],N[2],N[3]].reshape(ntA,nlay1, nbnd1)
  dd=d40_34
else:
  for t in range(ntA):
    for k in range(nlay1):
      dens2[t,k,:]=dens[t,dlay[k],idxb[0]-1,idxb[1]-1]
  dd=[k for k in range(nlay1)]
var=np.zeros(shape=(nt, nlay, nrow, ncol))
zz=np.zeros(shape=(nt, nlay1, nbnd1))
var2=np.zeros(shape=(ntA,nlay1, nbnd1))
print('fill the matrix')
N=trans4_3(nt,nlay,mp,idx)
c=np.zeros(shape=(nt,nlay,mp))
M=[np.zeros(shape=(nt,nbnd1),dtype=int) for i in range(2)]
M[0][:,:]=np.array([t for t in range(nt)])[:,None]
M[1][:,:]=idxd[None,:]
M[0],M[1]=M[0].flatten(),M[1].flatten()

for v in list(nms_part)+list(nms_gas) :
  var[:,:,:,:]=np.flip(nc.variables[v][:,:,:,:], [1,2])
  c[:,:,:] = var[N[0],N[1],N[2],N[3]].reshape(nt,nlay,mp) 
  for k in range(nlay1):
    zz[:,k,:] = c[M[0],dd[k],M[1]].reshape(nt,nbnd1)

#Time Interpolation
  if ntA>=3:
    for t in range(0,ntA,3):
      t3=int(t/3)
      var2[t+0,:,:]=zz[t3,:,:]
      var2[t+1,:,:]=zz[t3,:,:]*2/3+zz[t3+1,:,:]*1/3
      var2[t+2,:,:]=zz[t3,:,:]*1/3+zz[t3+1,:,:]*2/3
  else:
    for t in range(0,ntA):
      var2[t,:,:]=zz[0,:,:]

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

