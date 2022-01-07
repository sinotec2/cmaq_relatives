$ cat ./2016base/data/ptse/pt_timvar.py
from pandas import *
import numpy as np
import netCDF4
import PseudoNetCDF as pnc
import datetime
import os,sys,json
import subprocess
from dtconvertor import dt2jul, jul2dt


mm=sys.argv[1][-2:]
mon=int(sys.argv[1][-2:])
last=datetime.datetime(2016,mon,1)+datetime.timedelta(days=-1)
begP=last+datetime.timedelta(days=0.5) #pt files begin last day 12:00(UTC)
begd=datetime.datetime(last.year,last.month,15)
start=begd+datetime.timedelta(days=4*(5-1))
idx=int((begP-start).seconds/3600)
enddt=begd+datetime.timedelta(days=4*12)
totalH=(enddt-start).days*24+1
#input the results of pt_const.py fortBE.14.teds.baseMM
df=read_csv('point_reas16'+mm+'.csv')
#input the CAMx ptsource file
pt=pnc.pncopen(sys.argv[1],format='point_source')
v2=list(filter(lambda x:pt.variables[x].ndim==2, [i for i in pt.variables]))
nt,nopts=pt.variables[v2[0]].shape
mpsp={'PNA':'NA','POC':'POA','XYLMN':'XYL'}

fname1=sys.argv[1].replace('fortBE.14.','').replace('base','16')
#nc=/home/cmaqruns/2016_12SE1/emis/inln_point/ptnonipm/inln_mole_ptnonipm_20160701_12US1_cmaq_cb6_2016ff_16j.nc
#ncks -d TSTEP,0,0 -d ROW,1,10000 $nc template.timvar.nc
fname0='template.timvar.nc'
fname=fname1+'.timvar.nc'
ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
if len(ncks) ==0:  sys.exit('wrong NCKS')
os.system(ncks+' -O -d ROW,1,'+str(nopts+len(df))+' '+fname0+' '+fname)
XCELL=81000.000
XORIG=-2389500.
nc = netCDF4.Dataset(fname,'r+')
jt=nt
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
tb= int(pt.STIME[0]-8) #UTC
nc.NROWS=nopts+len(df)
nc.GDNAM='EAsia_81K'
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
  dt=start+datetime.timedelta(days=t/24.)
  nc.variables['TFLAG'][t,:,0]=[dt2jul(dt)[0] for j in range(nc.NVARS)]
  nc.variables['TFLAG'][t,:,1]=[dt2jul(dt)[1] for j in range(nc.NVARS)]

for v in v4:
  nc.variables[v][:,0,:,0]=np.zeros(shape=(totalH,nopts+len(df)),dtype='float32')

#CAMx_pt part
nc.variables['PMOTHR'][idx:idx+jt,0,:nopts,0]=(pt.variables['CPRM'][:,:]+pt.variables['FPRM'][:,:])/ 3600.
for v in mpsp: #mpsp={'PNA':'NA','POC':'POA','XYLMN':'XYL'}
  nc.variables[v][idx:idx+jt,0,:nopts,0]=np.array(pt.variables[mpsp[v]][:,:nopts], dtype='float32')/ 3600.
for v in v2: #ptse from CAMx
  if v not in v4:continue #outside of v4 (the template)
  nc.variables[v][idx:idx+jt,0,:nopts,0]=np.array(pt.variables[v][:,:nopts],dtype='float32') / 3600. #gmole/hr -> gmole/sec
nox= nc.variables['NO2'][:,0,:,0]+nc.variables['NO'][:,0,:,0]

for t in range(idx,idx+jt):
  nox[t,nopts:]=np.array(df['NOX'])
nc.variables['NO2'][:,0,:,0]=nox *1./10.
nc.variables['NO'][:,0,:,0] =nox *9./10.
#np.zeros(shape=(jt,nopts),dtype='float32') #

#REAS part
specs=[ i for i in df.columns if i not in ['lon','lat','x_m','y_m']]
with open('reas2cmaq.json','r') as f:
  r2c=json.load(f)
for v in specs:
  if v == 'NOX':continue
  if sum(np.array(df[v]))==0.:continue
  if v not in r2c :continue
  if type(r2c[v])==str: #simple mapping of specs
    if r2c[v] not in v4:continue
    for t in range(idx,idx+jt):
      nc.variables[r2c[v]][t,0,nopts:,0]=np.array(df[v])
  else:                 #in case CBM's
    for i in r2c[v]:
      for t in range(idx,idx+jt):
        nc.variables[i][t,0,nopts:,0]+=np.array(df[v])
for v in v4:
  if np.sum(nc.variables[v][:])==0:continue
  for t in range(idx):
    nc.variables[v][t,0,:,0]=nc.variables[v][t+24,0,:,0]
  for t in range(idx+jt,totalH):
    nc.variables[v][t,0,:,0]=nc.variables[v][t-24,0,:,0]
# print(v)
nc.close()
