import numpy as np
import netCDF4
import os,sys,subprocess

if (len(sys.argv) != 2):
  print ('usage: '+sys.argv[0]+' YYMM(1601)')
yrmn=sys.argv[1]

path={'114-32-164-198.HINET-IP.hinet.net':'/opt/anaconda3/bin/', 'node03':'/usr/bin/','master':'/cluster/netcdf/bin/', \
      'DEVP':'/usr/bin/','centos8':'/opt/anaconda3/envs/py37/bin/'}
hname=subprocess.check_output('echo $HOSTNAME',shell=True).decode('utf8').strip('\n')
if hname not in path:
  sys.exit('wrong HOSTNAME')


fname='moz_41_20'+yrmn+'.nc'

nc = netCDF4.Dataset(fname,'r')
tflag=nc.variables['TFLAG'][:,0,:]
nt,dt=tflag.shape
fname='ICON_tmp.d1'
for j in range(nt):
  fnamej=fname.replace('tmp',str(tflag[j,0])+'{:02d}'.format(int(tflag[j,1]/10000)))
#  if '201600418' not in fnamej:continue
  os.system('cp '+fname+' '+fnamej) 
  nc = netCDF4.Dataset(fnamej,'r+')
  nc.variables['TFLAG'][0,:,0]=[tflag[j,0] for v in range(nc.NVARS)]
  nc.variables['TFLAG'][0,:,1]=[tflag[j,1] for v in range(nc.NVARS)]
  nc.SDATE=tflag[j,0]
  nc.STIME=tflag[j,1]
  nc.close()
  os.system(path[hname]+'/ncatted -O -a TSTEP,global,o,i,60000 '+fnamej)
  a=fnamej+'.tmp'
  os.system(path[hname]+'/ncks -O --mk_rec_dmn TSTEP '+fnamej+' '+a+';mv -f '+a+' '+fnamej)
