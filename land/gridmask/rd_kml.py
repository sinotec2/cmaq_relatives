from pykml import parser
from os import path
from pandas import *

kml_file = path.join('doc.kml')
with open(kml_file) as f:
  doc = parser.parse(f).getroot()
plms=doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark')
names=[i.name for i in plms]

mtgs=doc.findall('.//{http://www.opengis.net/kml/2.2}MultiGeometry')
mtg_tag=[str(i.xpath).split()[-1][:-2] for i in mtgs]

plgs=doc.findall('.//{http://www.opengis.net/kml/2.2}Polygon')
plg_prt=[str(i.getparent().values).split()[-1][:-2] for i in plgs]

lon,lat,num,nam=[],[],[],[]
n=0
for plg in plgs:
  iplg=plgs.index(plg)
  imtg=mtg_tag.index(plg_prt[iplg])
  name=names[imtg]
  coord=plg.findall('.//{http://www.opengis.net/kml/2.2}coordinates')
  c=coord[0].pyval.split()
  for ln in c:
    if n%3==0:
      lon.append(ln.split(',')[0])
      lat.append(ln.split(',')[1])
      num.append('n='+str(n))
      nam.append(name)
    n+=1
#with open('doc.csv','w') as f:
#  for i in range(len(num)):
#    f.write(str(lon[i])+','+str(lat[i])+','+str(num[i])+','+nam[i]+'\n')
#   if n%100==0:print(n)
df=DataFrame({'lon':lon,'lat':lat,'num':num,'nam':nam})
df.set_index('lon').to_csv('doc.csv')
