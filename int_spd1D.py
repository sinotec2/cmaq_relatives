#!/opt/anaconda3/envs/py37/bin/python
# /opt/miniconda3/envs/py37/bin/python
from pandas import *
import twd97,os,sys,datetime
import numpy as np
import subprocess
from scipy.interpolate import griddata
from PseudoNetCDF.camxfiles.Memmaps import uamiv
#from PseudoNetCDF import PseudoNetCDFFile
from PseudoNetCDF.pncgen import pncgen
from pyproj import Proj 

def gen_xy():
  try:
    b=read_csv(path+'/xy_d1'+str(len(df))+'.csv')
  except:
    Xcent, Ycent = (0,0) #twd97.fromwgs84(Latitude_Pole, Longitude_Pole)
    pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40, lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)
    lat,lon=np.array(df.Latitude),np.array(df.Longitude)
#    xy = np.array([twd97.fromwgs84(i, j) for i, j in zip(lat,lon)])
#    x,y=(xy[:,i] for i in [0,1])
    x,y = pnyc(lon, lat, inverse=False)
    df['x']=x
    df['y']=y
    minx=[Xcent+newf.XORIG-newf.XCELL]
    miny=[Ycent+newf.YORIG-newf.YCELL]
    maxx=[Xcent+abs(newf.XORIG)+newf.XCELL]
    maxy=[Ycent+abs(newf.YORIG)+newf.YCELL]
#    latMinCP1,lonMinCP1=twd97.towgs84(minx,miny)
#    latMaxCP1,lonMinCP2=twd97.towgs84(minx,maxy)
#    latMinCP2,lonMaxCP1=twd97.towgs84(maxx,miny)
#    latMaxCP2,lonMaxCP2=twd97.towgs84(maxx,maxy)
    lonMinCP1,latMinCP1=pnyc(minx,miny, inverse=True)
    lonMaxCP1,latMinCP2=pnyc(minx,maxy, inverse=True)
    lonMinCP2,latMaxCP1=pnyc(maxx,miny, inverse=True)
    lonMaxCP2,latMaxCP2=pnyc(maxx,maxy, inverse=True)
    latMinCP=min(latMinCP1[0],latMinCP2[0])
    latMaxCP=max(latMaxCP1[0],latMaxCP2[0])
    lonMinCP=min(lonMinCP1[0],lonMinCP2[0])
    lonMaxCP=max(lonMaxCP1[0],lonMaxCP2[0])
    print (latMinCP,latMaxCP,lonMinCP,lonMaxCP)
    boo1=(latMinCP<=df.Latitude) & (df.Latitude <=latMaxCP)
    boo2=(lonMinCP<=df.Longitude) & (df.Longitude <=lonMaxCP)
    boo1=(minx[0]<=df.x) & (df.x <=maxx[0])
    boo2=(miny[0]<=df.y) & (df.y <=maxy[0])

    b=df.loc[boo1 & boo2]
    if len(b)==0:sys.exit('b=0')
    idx=list(b.index)
    b['idx']=idx
    b.set_index('idx').to_csv(path+'/xy_d1'+str(len(df))+'.csv')
  nx,ny=newf.NCOLS,newf.NROWS
  #griddata can not extrapolation
  x,y=np.array(b.x),np.array(b.y)
  dx,dy=(np.max(x)-np.min(x))/nx,(np.max(y)-np.min(y))/ny
  x_mesh = np.linspace(np.min(x)+dx,np.max(x)-dx,nx)
  y_mesh = np.linspace(np.min(y)+dy,np.max(y)-dy,ny)
  x_g, y_g = np.meshgrid(x_mesh, y_mesh)
  points=np.array([(i,j) for i,j in zip(x, y)]).astype(float)
  return points,x_g,y_g,b.idx


#VOCs are in ppbC
TnP=10*28.97*10**9 #T in degC, P in mb
mws={'GO3':48,'NO2':46,'ETH':30.07/2,'FORM':30.031,'ISOP':68.12/5,'PROP':44.1/3,'SO2':64,'TMP':TnP,'SLP':TnP,'STM':TnP}
col=['Latitude','Longitude','Value']

spnm0=sys.argv[1]
yrmo=sys.argv[2]
dt=int(sys.argv[3])
mo_b,mo_e= int(yrmo[2:4]), int(yrmo[2:4])
if '-' in yrmo:
  mo_e=int(yrmo[-2:])
fnameO=spnm0+'_d1.nc'
mw=mws[spnm0]

iy=2000+int(yrmo[:2])
SDATE=iy*1000+(datetime.date(iy,mo_b,1)-datetime.date(iy,1,1)).days+1
if mo_e<12:
  EDATE=iy*1000+(datetime.date(iy,mo_e+1,1)-datetime.date(iy,1,1)).days
else:
  EDATE=iy*1000+(datetime.date(iy,12,31)-datetime.date(iy,1,1)).days+1
nd=EDATE-SDATE+1


Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
mmm2ppb=28.97/mw*1000*1000*1000
spnam=spnm0.split()
hmp=subprocess.check_output('pwd',shell=True).decode('utf8').strip('\n').split('/')[1]
path='/'+hmp+'/camxruns/2019/ICBC/ecmwf/near_real_time'
os.system('cp '+path+'/NO_d2.grd01 '+fnameO)

newf = uamiv(fnameO,'r+')
newf.TSTEP = dt*10000 # designed
nh=int(24/dt)
nt=nd*nh
newf.NROWS = 59 
newf.NCOLS = 59
newf.NLAYS = 1
newf.NVARS = 2
newf.NSTEPS = nt
newf.createDimension('ROW', newf.NROWS)
newf.createDimension('COL', newf.NCOLS)
newf.createDimension('LAY', newf.NLAYS)
newf.createDimension('VAR', newf.NVARS)
newf.createDimension('TSTEP',nt)
newf.createDimension('DATE-TIME', 2)
newf.XORIG = -2389500
newf.YORIG = -2389500
newf.XCELL = 81000
newf.YCELL = 81000
newf.SDATE = SDATE
newf.STIME = 80000
newf.NAME = 'AIRQUALITY'
newf.NOTE = ' '*60
newf.CPROJ = 2
newf.TLAT1 = 10
newf.TLAT2 = 40
newf.ISTAG = 0
newf.ITZON = 15
newf.IUTM = 51
newf.PLON = Longitude_Pole
newf.PLAT = Latitude_Pole
#newf.VAR\-LIST=spnm0
zz=newf.createVariable('TFLAG',"i4",("TSTEP","VAR","DATE-TIME"))
zz=newf.createVariable('ETFLAG',"i4",("TSTEP","VAR","DATE-TIME"))
for s in spnam+['NO']:
  zz=newf.createVariable(s,"f4",("TSTEP","LAY","ROW","COL"))
  newf.variables[s][:,0,:,:]=np.zeros(shape=(nt,newf.NROWS,newf.NCOLS))

for s in spnam[:1]:
  it=0
  for id in range(nd):
    for ih in range(nh):
      ij='{:02d}'.format(id+1)+'{:02d}'.format(ih+1) #if 6:00 is number 2/ if nh=1,+1
      fname=s+'_'+ij
      df=read_csv(fname,header=None)
      df['Latitude']=[float(i.split()[0]) for i in df.iloc[:,0]]
      df['Longitude']=[float(i.split()[1]) for i in df.iloc[:,0]]
      df['Value']=[float(i.split()[2]) for i in df.iloc[:,0]]
      if it==0:
        points,x_g,y_g,idx=gen_xy()
        len_df_old=len(df)
      else:
        if len(df)!=len_df_old: 
          points,x_g,y_g,idx=gen_xy()
          len_df_old=len(df)
      c=np.array(df.loc[idx,'Value']) * mmm2ppb
      js=spnam.index(s)
      newf.variables[s][it,0,:,:]= griddata(points, c, (x_g, y_g), method='linear')
      it+=1
  print (js,s)
for s in ['NO']:
  for t in range(nt):
    newf.variables[s][t,0,:,:]= np.array(newf.variables[spnam[0]][t,0,:,:])
i=0
for id in range(nd):
  for ih in range(nh):
    jh=ih*dt+newf.STIME/10000
    tm=np.array([jh%24 for j in range(newf.NVARS)])
    newf.variables['TFLAG'][i,:,0]=[newf.SDATE+id+int(jh/24) for j in range(newf.NVARS)]
    newf.variables['TFLAG'][i,:,1]=tm*10000
    newf.variables['ETFLAG'][i,:,0]=[newf.SDATE+id+max(int(jh/24),int((ih+1)/nh)) for j in range(newf.NVARS)]
    newf.variables['ETFLAG'][i,:,1]=(tm+dt)%24*10000
    i+=1
pncgen(newf, fnameO)#, format = 'uamiv')
newf.close
#os.system('/cluster/miniconda/envs/py37/bin/pncgen --out-format=uamiv -O ./'+fnameO+' ./'+fnameO.replace('.nc','.grd01'))
'''
pncgen -f uamiv base.grd02.1909.ic base.grd02.1909.nc
ncks -v NO,TFLAG,ETFLAG base.grd02.1909.nc NO.nc
ncatted -a VAR-LIST,global,o,c,'NO              ' NO.nc
ncatted -a NVARS,global,o,i,1 NO.nc
pncgen --out-format=uamiv -O NO.nc NO_d2.grd01
'''
