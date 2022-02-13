""" argv[1]: yymm(eg 1601)
"""
import numpy as np
import netCDF4
import os,sys,subprocess
import datetime
from pandas import *


#mechine dependancy
hname=subprocess.check_output('echo $HOSTNAME',shell=True).decode('utf8').strip('\n')
path={\
	'114-32-164-198.HINET-IP.hinet.net':'/opt/anaconda3/bin/', \
	'IMacKuang.local':'/opt/anaconda3/bin/', \
	'node03':'/usr/bin/', \
	'master':'/cluster/netcdf/bin/', \
    'DEVP':'/usr/bin/', \
	'centos8':'/opt/anaconda3/envs/py37/bin/'}
if hname not in path:
  sys.exit('wrong HOSTNAME')

#read the soil file and store the Soil number for indexing
fnameS='epic_festc1.4_20180516/2016_US1_soil_bench.nc'
nc = netCDF4.Dataset(fnameS,'r')
Vs=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlays,nrows,ncols=(nc.variables[Vs[3][0]].shape[i] for i in range(4))
x='L1_SoilNum'
if x not in Vs[3]:sys.exit('soil file not right')
d={x:list(nc.variables[x][0,0,:,:].flatten())}

#epic file template
epi='epic_festc1.4_20180516'
fnameE=epi+'/2016_US1_time20160701_bench.nc'
nc = netCDF4.Dataset(fnameE,'r')
Ve=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlaye,nrowe,ncole=(nc.variables[Ve[3][0]].shape[i] for i in range(4))

#check the mesh consistency
if nrowe !=nrows or ncole != ncols:sys.exit('meshes not match')
#store all the variables in DataFrame
for x in Ve[3]:
    d.update({x:list(nc.variables[x][0,0,:,:].flatten())})
	
SN=DataFrame(d)
SN['idx']=SN.index
SN1=pivot_table(SN,index='L1_SoilNum',values='idx',aggfunc='count').reset_index()
SN1=SN1.sort_values('idx',ascending=False).reset_index(drop=True)
SN1.set_index('L1_SoilNum').to_csv(sys.argv[1]+'/most_freq.L1_SoilNumUS.csv')
SN1=SN1.drop(0).reset_index(drop=True)

#landuse matrix
fname='beld4.EAsia.ncf'
nc = netCDF4.Dataset(fname,'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))

#store the modis(%) to pickup(argmax) the maximum one
modis=np.zeros(shape=(17,nrow,ncol))
for i in range(17):
  v='MODIS_'+str(i)
  modis[i,:,:]=nc.variables[v][0,0,:,:]
#the water(modis0) must be avoided as possible, only 1.0 is regnized  
modis[0,:,:]=modis[0,:,:].astype(int)
df=DataFrame({'modis':list(modis.argmax(axis=0).flatten())})
df['idx']=df.index
MD1=pivot_table(df,index='modis',values='idx',aggfunc='count').reset_index()
MD1=MD1.sort_values('idx',ascending=False).reset_index(drop=True)
MD1.set_index('modis').to_csv(sys.argv[1]+'/most_freq.MODIS.csv')
MD1=MD1.drop(0).reset_index(drop=True)

#matching the most freq. land use to most freq soil number

#blanking whole database
nval=-9.999000e+36
for v in Ve[3]:
  df[v]=[nval for i in range(len(df))]

#each landuse cat. map to 7 soil numbers, 7 = len(SN1) / len(MD1)
for md in MD1.modis:
  #num of priorities
  imd=list(MD1.modis).index(md)
  #all the record fit this modis category
  idx_md=df.loc[df.modis==md].index
  #apply to the soil number by freq. order
  for isn in range(7*imd,min(len(SN1),(imd+1)*7)):
    soilnum=SN1.loc[isn,'L1_SoilNum']
    #apply to all the epic variables
    for v in Ve[3]:
	  #retrieve the US database, stored in DataFrame SN, not include the nvalue
      a=np.array([i for i in np.array(SN.loc[SN.L1_SoilNum==soilnum,v]) if i>=-10])
      mu,sg=np.mean(a),np.std(a)
	  #Gaussion_random choise of values with upper and lower limits
      b=np.random.normal(mu,sg,len(idx_md))
      df.loc[idx_md,v]=np.clip(b,np.min(a),np.max(a))
nc_lu=nc #for transfering the global variables

fnameN=fnameE.replace('US1','EAsia_81K').replace('20160701','').replace(epi,sys.argv[1])
os.system(path[hname]+'ncks -O -d ROW,0,52 -d COL,0,52 '+fnameE+' '+fnameN)
#-d LAY,0,39 (the CMAQ only accepts nlay=42, never try to change this)
nc = netCDF4.Dataset(fnameN,'r+')
#filling the dataframe to the 2d array
for v in Ve[3]:
  a=np.array(df[v]).reshape(nrow,ncol)
  for k in range(42):
    nc.variables[v][0,k,:,:]=a
#transfer the global attributes of landuse file to the new file
atbs=['CDATE', 'CTIME', 'EXEC_ID', 'FTYPE', 'GDNAM', 'GDTYP','IOAPI_VERSION', 'NCOLS', 'NROWS', 'NTHIK', 'P_ALP', 'P_BET', 'P_GAM', 'UPNAM', 'XCELL', 'XCENT', 'XORIG', 'YCELL', 'YCENT', 'YORIG']
for a in atbs:
  cmd='nc.'+a+'=nc_lu.'+a
  exec(cmd)  

#nc.VGTYP = 7 
#nc.VGTOP = 5000.
#nc.VGLVLS =[1., 0.995, 0.99, 0.98, 0.96, 0.93, 0.91, 0.89, 0.85, 0.816, 0.783, 0.751, 0.693, 0.637, 0.586, 0.537, 0.492, 0.449, 0.409, 0.372, 0.337, 0.304, 0.274, 0.245, 0.219, 0.194, 0.172, 0.151, 0.131, 0.113, 0.096, 0.082, 0.068, 0.056, 0.046, 0.036, 0.027, 0.019, 0.012, 0.006, 0.]             
#nc.NLAYS = len(nc.VGLVLS)-1
#for v in range(nc.NVARS):
#  nc.variables['TFLAG'][:,v,0]=nc.SDATE
#  nc.variables['TFLAG'][:,v,1]=nc.STIME
nc.close()
