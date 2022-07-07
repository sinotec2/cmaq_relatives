from pandas import *
import numpy as np
import netCDF4
import PseudoNetCDF as pnc
import datetime
import os,sys,json
import subprocess

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

fname1=sys.argv[1]
mm=fname1[-5:-3]
mon=int(mm)
last=datetime.datetime(2019,mon,1)+datetime.timedelta(days=-1)
begP=last#+datetime.timedelta(days=0.5) #pt files begin last day 12:00(UTC)
begd=datetime.datetime(last.year,last.month,15)
start=begd+datetime.timedelta(days=4*(5-1))
idx=int((begP-start).seconds/3600)
enddt=begd+datetime.timedelta(days=4*12)
totalH=((enddt-start).days+1)*24+1
#input the CAMx ptsource file
pt=netCDF4.Dataset(fname1, 'r')
v2=list(filter(lambda x:pt.variables[x].ndim==2, [i for i in pt.variables]))
nt,nopts=pt.variables[v2[0]].shape
mpsp={'PNA':'NA','POC':'POA','XYLMN':'XYL'}

fname1=fname1.replace('fortBE.413_','').replace('ptse','19').replace('.nc','')
#nc=/home/cmaqruns/2016_12SE1/emis/inln_point/ptnonipm/inln_mole_ptnonipm_20160701_12US1_cmaq_cb6_2016ff_16j.nc
#ncks -d TSTEP,0,0 -d ROW,1,10000 $nc template.timvar.nc
fname0='template.timvar.nc'
fname=fname1+'.timvar.nc'
path={'114-32-164-198.HINET-IP.hinet.net':'/opt/anaconda3/bin/', 'node03':'/usr/bin/','master':'/cluster/netcdf/bin/'}
path.update({'DEVP':'/usr/bin/','node01':'/cluster/netcdf/bin/','node02':'/cluster/netcdf/bin/'})
hname=subprocess.check_output('echo $HOSTNAME',shell=True).decode('utf8').strip('\n')
if hname not in path:
  sys.exit('wrong HOSTNAME')
if nopts>25000:sys.exit('nopts>25000')
os.system(path[hname]+'ncks -O -d ROW,1,'+str(nopts)+' '+fname0+' '+fname)
XCELL=pt.XCELL
XORIG=pt.XORIG
YORIG=pt.XORIG
V=[list(filter(lambda x:pt.variables[x].ndim==j, [i for i in pt.variables])) for j in [1,2,3,4]]

nc = netCDF4.Dataset(fname,'r+')
jt=nt
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
bdate=jul2dt([pt.SDATE,pt.STIME])
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
nc.SDATE=dt2jul(start)[0]
nc.STIME=dt2jul(start)[1]

for t in range(totalH):
  dt=start+datetime.timedelta(hours=t)
  nc.variables['TFLAG'][t,:,0]=[dt2jul(dt)[0] for j in range(nc.NVARS)]
  nc.variables['TFLAG'][t,:,1]=[dt2jul(dt)[1] for j in range(nc.NVARS)]

z=np.zeros(shape=nopts,dtype='float32')
for v in v4:
  for t in range(totalH):
    nc.variables[v][t,:,:,:]=z
#CAMx_pt part
pmother=(pt.variables['CPRM'][:,:]+pt.variables['FPRM'][:,:])/ 3600.
nc.variables['PMOTHR'][idx:idx+jt,0,:nopts,0]=pmother
for v in mpsp: #mpsp={'PNA':'NA','POC':'POA','XYLMN':'XYL'}
  if mpsp[v] not in V[1]:continue
  nc.variables[v][idx:idx+jt,0,:nopts,0]=np.array(pt.variables[mpsp[v]][:,:nopts], dtype='float32')/ 3600.
for v in v2: #ptse from CAMx
  if v not in v4:continue #outside of v4 (the template)
  print(v)
  var=pt.variables[v][:,:]/3600. #gmole/hr -> gmole/sec
  nc.variables[v][idx:idx+jt,0,:nopts,0]=var[:]
nox= nc.variables['NO2'][:,0,:,0]+nc.variables['NO'][:,0,:,0]

nc.variables['NO2'][:,0,:,0]=nox *1./10.
nc.variables['NO'][:,0,:,0] =nox *9./10.
#np.zeros(shape=(jt,nopts),dtype='float32') #

for v in v4:
  if np.sum(nc.variables[v][:])==0:continue
  if idx>0:
    for t in range(idx):
      nc.variables[v][t,0,:,0]=nc.variables[v][t+24,0,:,0]
  if totalH>idx+jt:
    for t in range(idx+jt,totalH):
      nc.variables[v][t,0,:,0]=nc.variables[v][t-24,0,:,0]
# print(v)
nc.close()
