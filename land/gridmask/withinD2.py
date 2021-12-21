from pandas import *
from pyproj import Proj
import numpy as np
import netCDF4
import os,sys, datetime, json, subprocess
from pykml import parser
from os import path
from shapely.geometry import Point, Polygon



df=read_csv('chn_admbnda_ocha.csv',encoding='big5')
#the dict between name and district abb.
nam2dis={i:j for i,j in zip(df.ADM1_EN,df.district)}
#forming the list of district abbriviations in alphbet sequence
a=list(set(df.district))
a.sort()
dict=['NA']+a

kml_file = path.join('doc.kml')
with open(kml_file) as f:
  doc = parser.parse(f).getroot()
plms=doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
names=[i.name for i in plms]

mtgs=doc.findall('.//{http://www.opengis.net/kml/2.2}MultiGeometry')
mtg_tag=[str(i.xpath).split()[-1][:-2] for i in mtgs]
plgs=doc.findall('.//{http://www.opengis.net/kml/2.2}Polygon')
plg_prt=[str(i.getparent().values).split()[-1][:-2] for i in plgs]

#coord. transf. between WGS and lambert
Latitude_Pole, Longitude_Pole = 23.61000, 120.9900
pnyc = Proj(proj='lcc', datum='NAD83', lat_1=10, lat_2=40,
        lat_0=Latitude_Pole, lon_0=Longitude_Pole, x_0=0, y_0=0.0)

#read a d2 template and generate the LL of grid meshes
fname='tempCMAQ_d2.nc'
fnameO='AQFZones_sChina_27K.nc'
nc = netCDF4.Dataset(fname,'r+')
v4=list(filter(lambda x:nc.variables[x].ndim==4, [i for i in nc.variables]))
nt,nlay,nrow,ncol=(nc.variables[v4[0]].shape[i] for i in range(4))
X=[nc.XORIG+nc.XCELL*i for i in range(ncol)]
Y=[nc.YORIG+nc.YCELL*i for i in range(nrow)]
x_g, y_g = np.meshgrid(X, Y)
Plon, Plat= pnyc(x_g,y_g, inverse=True)

#lists of polygon coordinates
#same sequence of Nplg
Dplg=[]
#names of each polygon, may be duplicated
Nplg=[]
for plg in plgs:
  iplg=plgs.index(plg)
  imtg=mtg_tag.index(plg_prt[iplg])                     #multiplegeometry name, as the parent w.r.t polygon
  Nplg.append(names[imtg])                                              #the name is located throught linkage of parent tag
  coord=plg.findall('.//{http://www.opengis.net/kml/2.2}coordinates')
  c=coord[0].pyval.split()                                              #all the kml (lon,lat,att) strings
  lon=[float(ln.split(',')[0]) for ln in c]             #read all the lon values as a list
  lat=[float(ln.split(',')[1]) for ln in c]             #read lat
  crd=[(i,j) for i,j in zip(lat,lon)]                   #zip (lat,lon) for shapefile operations
  Dplg.append(crd)

nplgs=len(plgs)

DIS=np.zeros(shape=(nrow,ncol),dtype=int)               #fill the container with zeros
for j in range(nrow):
  for i in range(ncol):
    p1=Point((Plat[j,i],Plon[j,i]))                             #in form of wgs
    ids=-1
    for n in range(nplgs):                                              #loop for each polygons
      poly = Polygon(Dplg[n])
      if p1.within(poly):                             #boolean to check whether the p1 coordinates is inside the polygon or not
        ids=n
        break
    if ids!=-1:
      DIS[j,i]=dict.index(nam2dis[Nplg[n]])
#output and check
nc.variables['NO'][0,0,:,:]=DIS[:,:]
zones=nc.variables['NO'][0,0,:]
nc.close()
if v4[0]!='NO':
  s=v4[0]
else:
  sys.exit('V3[0]==NO')
for v in v4[1:]:
  if v=='NO':continue
  s+=','+v
ncks=subprocess.check_output('which ncks',shell=True).decode('utf8').strip('\n')
os.system(ncks+' -O -d TSTEP,0,0 -x -v '+s+' '+fname+' '+fnameO)
nc1=netCDF4.Dataset(fnameO,'r+')
for i in set(zones.flatten()):
  s='AQFZ'+str(int(i))
  nc1.createVariable(s,"f4",("TSTEP","LAY","ROW","COL"))
  nc1.variables[s].units = "fraction        "
  nc1.variables[s].long_name = "China Air Quality Forecast Zone: "+s[-1]
  nc1.variables[s].var_desc = "fractional area per grid cell,1:JJZ,2:FWShanXi,3:DongBei,4:XiBei,5:HuaNan,6:Xinan,7:HuaDong"
  idx=np.where(zones==i)
  nc1.variables[s][:,:,:,:]=np.zeros(shape=(nt,nlay,nrow,ncol))
  for j in range(len(idx[0])):
    nc1.variables[s][0,0,idx[0][j],idx[1][j]]=1.
nc1.close()

