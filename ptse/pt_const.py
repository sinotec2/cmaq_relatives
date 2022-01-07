import numpy as np
import netCDF4
import PseudoNetCDF as pnc
import os,sys,twd97
from pyproj import Proj
import subprocess
from pandas import *
from calendar import monthrange

mon=int(sys.argv[1][-2:])
#join the pollutants for this month
pth='.' #~/mac/cmaqruns/2016base/data/ptse'
fnames=subprocess.check_output('ls '+pth+'/point_*csv|grep -v reas|grep -v all',shell=True).decode('utf8').strip('\n').split()
#prepare interceptions
Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)
XCELL=81000.000
XORIG=-2389500.

dfa=DataFrame({})
for fn in fnames:
  spec=fn.split('/')[-1].replace('point_','').replace('.csv','').replace('./','')
  df=read_csv(fn)
  #interceptions
  lat,lon=(list(df.lat),list(df.lon))
  x,y=pnyc(lon, lat, inverse=False)
  df['x_m'],df['y_m']=(x,y)
  boo=(df['x_m']>=XORIG) & (df['x_m']<=-XORIG) & (df['y_m']>=XORIG) & (df['y_m']<=-XORIG)
  df=df.loc[boo].reset_index(drop=True)
  #reduction
  df.lat=[round(i,1) for i in df.lat]
  df.lon=[round(i,1) for i in df.lon]
  c=df.iloc[:,[0,1,mon+1]]
  c.columns=['lon','lat',spec]
  c=pivot_table(c,index=['lon','lat'],values=spec,aggfunc=sum).reset_index()
  if fn==fnames[0]:
    dfa=c
  else:
    dfa=merge(dfa,c,on=['lon','lat'],how='outer')
df=dfa.fillna(0)

fac=1000.*1000./monthrange(2015,mon)[1]/24/3600.
mws={'BC':1,'BENZENE':78.11,'BUTANES':58.12,'CO':28, 'CO2':44, 'ETHANE':30.07,
       'FORMALDEHYDE':30.031, 'INTERNAL_ALKENES':28.05, 'KETONES':86.13, 'NH3':17, 'NOX':46, 'OC':1,
       'OTHER_ALKANES':58.12, 'OTHER_AROMATICS':106.16, 'PENTANES':72.15, 'PM10':1, 'PM25':1,
       'PROPANE':44.1 , 'SO2':64, 'TERMINAL_ALKENES':28.05, 'TOLUENE':92.14, 'TOTAL_NMV':58.12,
       'XYLENES':106.16}

#units of gmole/s or gram/s
for c in [ i for i in df.columns if i not in ['lon','lat']]:
  if c not in mws:continue
  df[c]=np.array(df[c])*fac/mws[c]
lat,lon=(list(df.lat),list(df.lon))
x,y=pnyc(lon, lat, inverse=False)
df['x_m'],df['y_m']=(x,y)
df.set_index('lon').to_csv('point_reas16'+sys.argv[1][-2:]+'.csv')

fname1=sys.argv[1]
pt=pnc.pncopen(fname1,format='point_source')
v3=list(filter(lambda x:pt.variables[x].ndim==3, [i for i in pt.variables]))
v2=list(filter(lambda x:pt.variables[x].ndim==2, [i for i in pt.variables]))
v1=list(filter(lambda x:pt.variables[x].ndim==1, [i for i in pt.variables]))
nhr,nvar,dt=pt.variables[v3[0]].shape
nt,nopts=pt.variables[v2[0]].shape

tb=pt.STIME[0]-8 #UTC
fname1=fname1.replace('fortBE.14.','').replace('base','16')
fname=fname1+'.const.nc'
fname0='stack_groups_ptnonipm_12US1_2016ff_16j.nc' #as template

#ncks path
path={'114-32-164-198.HINET-IP.hinet.net':'/opt/anaconda3/bin/', 'node03':'/usr/bin/', \
        'master':'/cluster/netcdf/bin/','DEVP':'/usr/bin/'}
hname=subprocess.check_output('echo $HOSTNAME',shell=True).decode('utf8').strip('\n')
if hname not in path:
  sys.exit('wrong HOSTNAME')

x=list(pt.variables['XSTK'][:nopts])+list(df.x_m)
y=list(pt.variables['YSTK'][:nopts])+list(df.y_m)
lon, lat = pnyc(x, y, inverse=True)

os.system(path[hname]+'ncks -O -d ROW,1,'+str(nopts+len(df))+' '+fname0+' '+fname)
nc = netCDF4.Dataset(fname,'r+')
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
nc.SDATE=2000000+pt.SDATE[0]
nc.STIME=tb*10000
mp={'STKDM':'DSTK','STKHT':'HSTK','STKTK':'TSTK','STKVE':'VSTK','XLOCA':'XSTK', 'YLOCA':'YSTK',}
va={'STKDM':17.0  ,'STKHT':250   ,'STKTK':373.  ,'STKVE':19.0}

#velocity is m/hr in CAMx pt, but in m/s in CMAQ_pt
v='STKVE'
STKVE=list(pt.variables[mp[v]][:]/3600.)

for i in va:
  val=va[i]
  va.update({i:[val for i in range(len(df))]})
va.update({'XLOCA':list(df.x_m),'YLOCA':list(df.y_m)})
nc.variables['LMAJOR'][0,0,:,0]=[0 for i in range(nopts+len(df))]
nc.variables['LPING'][0,0,:,0]=[0 for i in range(nopts+len(df))]
for i in range(nopts+len(df)):
  HSTK=250.
  if i<nopts:
    HSTK=pt.variables['HSTK'][i]
  if HSTK>150.:
    nc.variables['LPING'][0,0,i,0]=1
    nc.variables['LMAJOR'][0,0,i,0]=1
for v in mp:
  if v=='STKVE' :continue
  nc.variables[v][0,0,:,0]=np.array(list(pt.variables[mp[v]][:])+va[v])
v='STKVE'
nc.variables[v][0,0,:,0]=np.array(STKVE+va[v])
nc.variables['IFIP'][0,0,:,0]=[1000+i for i in range(nopts+len(df))]
nc.variables['ISTACK'][0,0,:,0]=[1+i for i in range(nopts+len(df))]

nc.variables['COL'][0,0,:,0]=[int((i-nc.XORIG)/nc.XCELL) for i in x]
nc.variables['ROW'][0,0,:,0]=[int((i-nc.YORIG)/nc.YCELL) for i in y]
nc.variables['TFLAG'][0,:,0]=[nc.SDATE for i in range(nc.NVARS)]
nc.variables['TFLAG'][0,:,1]=[nc.STIME for i in range(nc.NVARS)]
nc.variables['LATITUDE'][0,0,:,0]=lat
nc.variables['LONGITUDE'][0,0,:,0]=lon
nc.close()
