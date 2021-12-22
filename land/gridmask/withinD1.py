from pandas import *
from pykml import parser
from os import path, system
import numpy as np
import netCDF4
import subprocess
from pyproj import Proj
from shapely.geometry import Point, Polygon

kml_file = path.join('doc.kml')
with open(kml_file) as f:
  doc = parser.parse(f).getroot()
plms=doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
names=[i.name for i in plms]

mtgs=doc.findall('.//{http://www.opengis.net/kml/2.2}MultiGeometry')
mtg_tag=[str(i.xpath).split()[-1][:-2] for i in mtgs]

plgs=doc.findall('.//{http://www.opengis.net/kml/2.2}Polygon')
nplgs=len(plgs)
plg_prt=[str(i.getparent().values).split()[-1][:-2] for i in plgs]

lon,lat,num,nam=[],[],[],[]
n=0
#store the polygons
Dplg=[]
#name for the polygons
Nplg=[]
for plg in plgs:
  iplg=plgs.index(plg)
  imtg=mtg_tag.index(plg_prt[iplg])
  name=names[imtg]
  Nplg.append(name)
  coord=plg.findall('.//{http://www.opengis.net/kml/2.2}coordinates')
  c=coord[0].pyval.split()
  long=[float(ln.split(',')[0]) for ln in c]
  lati=[float(ln.split(',')[1]) for ln in c]
  crd=[(i,j) for i,j in zip(lati,long)]
  Dplg.append(crd)
  for ln in c:
    if n%3==0:
      lon.append(ln.split(',')[0])
      lat.append(ln.split(',')[1])
      num.append('n='+str(n))
      nam.append(name)
    n+=1
#output the coordinates for checking
df=DataFrame({'lon':lon,'lat':lat,'num':num,'nam':nam})
df.set_index('lon').to_csv('doc.csv')


#form the dict of name to district from csv file
df=read_csv('chn_admbnda_ocha.csv',encoding='big5')
nam2dis={i:j for i,j in zip(df.ADM1_EN,df.district)}
a=list(set(df.district));a.sort()
a=['NA']+a
dist={a[i]:i for i in range(len(a))}

#check the content of names
for i in names:
    if i not in nam2dis:print(i)

Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40,
        lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

#reading the d1 template
fname='PM25_202001-05_d1.nc'
nc = netCDF4.Dataset(fname,'r+')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
X=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
Y=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x_g, y_g = np.meshgrid(X, Y)
Plon, Plat= pnyc(x_g,y_g, inverse=True)
Plat1d,Plon1d=Plat.flatten(),Plon.flatten()
p1d=[Point(Plat1d[i],Plon1d[i]) for i in range(nrow*ncol)]


#store the index of districts(1~7) for each grids for VERDI cheking
DIS=np.zeros(shape=(nrow,ncol),dtype=int)
for n in range(nplgs):
  poly = Polygon(Dplg[n])
  a=np.array([i.within(poly) for i in p1d]).reshape(nrow,ncol)
  idx=np.where(a==True)
  if len(idx[0])==0:continue
  DIS[idx[0],idx[1]]=dist[nam2dis[Nplg[n]]]
nc.variables['NO'][0,0,:,:]=DIS[:,:]
nc.close()

ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
system(ncks+' -O -d TSTEP,0,0 PM25_202001-05_d1.nc AQFZones_EAsia_81K.nc')
nc1=netCDF4.Dataset('AQFZones_EAsia_81K.nc','r+')
for i in set(DIS.flatten()):
  s='AQFZ'+str(int(i))
  nc1.createVariable(s,"f4",("TSTEP","LAY","ROW","COL"))
  nc1.variables[s].units = "fraction        "
  nc1.variables[s].long_name = "China Air Quality Forecast Zone: "+s[-1]
  nc1.variables[s].var_desc = "fractional area per grid cell,1:JJZ,2:FWShanXi,3:DongBei,4:XiBei,5:HuaNan,6:Xinan,7:HuaDong"
  idx=np.where(DIS==i)
  nc1.variables[s][:,:,:,:]=0
  for j in range(len(idx[0])):
    nc1.variables[s][0,0,idx[0][j],idx[1][j]]=1.
nc1.close()
system(ncks+' -O -x -v NO,PM25 AQFZones_EAsia_81K.nc a;mv a AQFZones_EAsia_81K.nc')

