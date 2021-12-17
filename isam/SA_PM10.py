import numpy as np
import netCDF4
import sys, os

fname=sys.argv[1]
intv=fname.split('_')[-1]
path=intv.strip('.nc')
ymdh=fname.split('_')[7]

nc = netCDF4.Dataset(fname, 'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc.variables[V[3][0]].shape[i] for i in range(4))

v4=list(set([i.split('_')[0] for i in V[3]]));v4.sort()
grp=list(set([i.split('_')[1] for i in V[3]]));grp.sort()

Sulfate='ASO4I ANO3I ANH4I ACLI ASO4J ANO3J ANH4J ASO4K ANO3K ANH4K'.split()
BC='AECI AECJ'.split()
OC='APOCI APNCOMI APOCJ AOTHRJ AXYL1J AXYL2J AXYL3J ATOL1J  ATOL2J  ATOL3J  ABNZ1J  ABNZ2J  ABNZ3J\
  AISO1J AISO2J  AISO3J  ATRP1J  ATRP2J  ASQTJ  AALK1J  AALK2J AORGCJ  AOLGBJ  AOLGAJ  APAH1J  APAH2J\
  APAH3J  APNCOMJ AOTHRI'.replace('_','').split()
Dust='AFEJ AALJ ASIJ ACAJ AMGJ AKJ AMNJ ACORS ASOIL ATIJ'.split()
SS='ANAI ANAJ ACLJ ACLK ASEACAT'.split()
Semi='ASVPO1J ASVPO2J  ASVPO3J  ASVPO2I  ASVPO1I ALVPO1J   ALVPO1I  AIVPO1J'.split()
aer=Sulfate+BC+OC+Dust+SS+Semi

for g in grp:
  fname = 'PM10'+path+'_'+ymdh+'_'+g+'.nc'
  os.system('cp template_PM10.nc '+fname)
  nco= netCDF4.Dataset(fname, 'r+')
  for t in range(nt):  
    nco['TFLAG'][t,0,:]=nc['TFLAG'][t,0,:]
  var=np.zeros(shape=(nt,nlay,nrow,ncol))
  for v in set(aer) & set(v4):
    vg=v+'_'+g
    if np.isnan(np.max(nc[vg][:])):continue
    var[:]+=nc[vg][:]
  nco['PM10'][:]=var[:]
  nco.close()

