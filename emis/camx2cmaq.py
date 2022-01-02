import os,sys
import numpy as np
import netCDF4
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

ipth=int(sys.argv[1])
pth='area biog line ptse ship'.split()
ext={i:i for i in pth}
ext.update({'ship':'51Ab','ptse':'ptsG'})
home='/nas1/TEDS/teds10_camx/HourlyWeighted'
for p in pth[ipth:ipth+1]:
  for m in range(1,13):
    mm='{:02d}'.format(m)
    fname=home+'/'+p+'/'+'fortBE.413_teds10.'+ext[p]+mm+'.nc'
    fnameO=p+'_TWN_3X3.16'+mm+'.nc'
    os.system('cp template.nc '+fnameO)
    nc0= netCDF4.Dataset(fname, 'r') 
    nc = netCDF4.Dataset(fnameO, 'r+') 
    V0=[list(filter(lambda x:nc0.variables[x].ndim==j, [i for i in nc0.variables])) for j in [1,2,3,4]]
    V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
    nv=len(V[3])
    nt,nlay,nrow,ncol=nc0.variables[V0[3][0]].shape
    sdatetime=[jul2dt(nc0.variables['TFLAG'][t,0,:]) for t in range(nt)]
    jul2=[dt2jul(i+datetime.timedelta(hours=-8)) for i in sdatetime]
    for t in range(nt):
      nc.variables['TFLAG'][t,:,0]=[jul2[t][0] for i in range(nv)]
      nc.variables['TFLAG'][t,:,1]=[jul2[t][1] for i in range(nv)]
      for iv in range(nv):
        v=V[3][iv]
        if v in V0[3]:
          nc.variables[v][t,:,:,:]=nc0.variables[v][t,:,:,:]/3600.
        else:
          nc.variables[v][t,:,:,:]=0
    nc.SDATE, nc.STIME=(jul2[0][0],jul2[0][1])
    nc.close()
    print(fnameO)
