import xml.etree.cElementTree as ET
from pandas import *

rootElement = ET.parse("TOWN_MOI_1090727.gml").getroot()
s=set()
for subelement in rootElement.getiterator():
  for subsub in subelement:
    s=s|set([subsub.tag])
s=list(s)
s.sort()
xzqy=s[5][44:]
xzqydm=[i for i in s if xzqy in i][1]
all_town=set()
for subelement in rootElement.getiterator():
  for subsub in subelement:
    if xzqydm == subsub.tag:
      all_town=all_town|set([subsub.text])
all_town=list(all_town)
all_town.sort()
twnid={}
isq=0
wkt=[]
for subelement in rootElement.getiterator():
  for subsub in subelement:
    if xzqydm == subsub.tag:tid=subsub.text
    if subsub.tag == "{http://www.opengis.net/gml}coordinates":
      x = subsub.text
      point_for_pol =[(float(i.split(',')[0]),float(i.split(',')[1])) for i in x.split()]
      wkt.append(point_for_pol)
      twnid.update({isq:tid})
      isq+=1

df_twn=read_csv('TOWN_MOI_1090727E.csv')
ii=[int(twnid[i]) for i in range(len(twnid))]
df=DataFrame({'twnid':ii,'lonlats':wkt})
TOWNENG={i:j for i,j in zip(df_twn.TOWNCODE, df_twn.TOWNENG)}
df['TOWNENG']=[TOWNENG[i] for i in df.twnid]
df.set_index('twnid').to_csv('polygons.csv')
