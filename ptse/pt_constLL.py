import numpy as np
import netCDF4
import PseudoNetCDF as pnc
import os,sys,twd97
from pyproj import Proj
import subprocess
from pandas import *
import datetime

def dt2jul(dt):
  yr=dt.year
  deltaT=dt-datetime.datetime(yr,1,1)
  deltaH=int((deltaT.total_seconds()-deltaT.days*24*3600)/3600.)
  return (yr*1000+deltaT.days+1,deltaH*10000)

def jul2dt(jultm):
  jul,tm=jultm[:]
  yr=int(jul/1000)
  ih=int(tm/10000.)
  return datetime.datetime(yr,1,1)+datetime.timedelta(days=int(jul-yr*1000-1))+datetime.timedelta(hours=ih)


mon=int(sys.argv[1][-5:-3])
#join the pollutants for this month
pth='/nas1/cmaqruns/2016base/data/ptse/'
#prepare interceptions
Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

fname1=sys.argv[1]
pt=netCDF4.Dataset(fname1, 'r')
v3=list(filter(lambda x:pt.variables[x].ndim==3, [i for i in pt.variables]))
v2=list(filter(lambda x:pt.variables[x].ndim==2, [i for i in pt.variables]))
v1=list(filter(lambda x:pt.variables[x].ndim==1, [i for i in pt.variables]))
nhr,nvar,dt=pt.variables[v3[0]].shape
nt,nopts=pt.variables[v2[0]].shape
XCELL=pt.XCELL
XORIG=pt.XORIG
YORIG=pt.XORIG

tb=pt.STIME-80000 #UTC
bdate=jul2dt([pt.SDATE,pt.STIME])
fname1=fname1.replace('fortBE.413_','').replace('ptse','19').replace('.nc','')
fname=fname1+'.const.nc'
fname0=pth+'stack_groups_ptnonipm_12US1_2016ff_16j.nc' #as template

#ncks path
path={'114-32-164-198.HINET-IP.hinet.net':'/opt/anaconda3/bin/', 'node03':'/usr/bin/', \
        'master':'/cluster/netcdf/bin/','DEVP':'/usr/bin/'}
hname=subprocess.check_output('echo $HOSTNAME',shell=True).decode('utf8').strip('\n')
if hname not in path:
  sys.exit('wrong HOSTNAME')
ncks=path[hname]+'ncks'
x=list(pt.variables['xcoord'][:nopts])
y=list(pt.variables['ycoord'][:nopts])
lon, lat = pnyc(x, y, inverse=True)

os.system(ncks+' -O -d ROW,1,'+str(nopts)+' '+fname0+' '+fname)
nc = netCDF4.Dataset(fname,'r+')
nc.NROWS=nopts
nc.GDNAM='TWN_3X3'
nc.P_ALP = np.array(10.)
nc.P_BET = np.array(40.)
nc.P_GAM = np.array(120.98999786377)
nc.XCENT = np.array(120.98999786377)
nc.YCENT = np.array(23.6100196838379)
nc.XCELL=XCELL #27000.000
nc.YCELL=XCELL #27000.000
nc.XORIG=XORIG #-877500.0
nc.YORIG=XORIG #-877500.0
nc.SDATE,nc.STIME=dt2jul(bdate+datetime.timedelta(hours=-8))

mp={'STKDM':'stkdiam','STKHT':'stkheight','STKTK':'stktemp','STKVE':'stkspeed','XLOCA':'xcoord', 'YLOCA':'ycoord',}

for v in mp:
  nc.variables[v][0,0,:,0]=pt.variables[mp[v]][:]
#velocity is m/hr in CAMx pt, but in m/s in CMAQ_pt
nc.variables['STKVE'][0,0,:,0]=pt.variables[mp[v]][:]/3600.
nc.variables['IFIP'][0,0,:,0]=[1000+i for i in range(nopts)]
nc.variables['ISTACK'][0,0,:,0]=[1+i for i in range(nopts)]

nc.variables['COL'][0,0,:,0]=[int((i-nc.XORIG)/nc.XCELL) for i in x]
nc.variables['ROW'][0,0,:,0]=[int((i-nc.YORIG)/nc.YCELL) for i in y]
nc.variables['TFLAG'][0,:,0]=[nc.SDATE for i in range(nc.NVARS)]
nc.variables['TFLAG'][0,:,1]=[nc.STIME for i in range(nc.NVARS)]
nc.variables['LATITUDE'][0,0,:,0]=lat
nc.variables['LONGITUDE'][0,0,:,0]=lon
nc.close()
