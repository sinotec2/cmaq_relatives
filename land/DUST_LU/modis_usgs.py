import numpy as np
import netCDF4


mod_des=['1. MODIS: 1 evergreen needleleaf forest',
 '2. MODIS: 2 evergreen broadleaf forest',
 '3. MODIS: 3 deciduous needleleaf forest',
 '4. MODIS: 4 deciduous broadleaf forest',
 '5. MODIS: 5 mixed forests',
 '6. MODIS: 6 closed shrublands',
 '7. MODIS: 7 open shrublands',
 '8. MODIS: 8 woody savannas',
 '9. MODIS: 9 savannas',
 '10. MODIS: 10 grasslands',
 '11. MODIS: 11 permanent wetlands',
 '12. MODIS: 12 croplands',
 '13. MODIS: 13 urban and built up',
 '14. MODIS: 14 cropland / natural vegetation mosaic',
 '15. MODIS: 15 permanent snow and ice',
 '16. MODIS: 16 barren or sparsely vegetated',
 '17. MODIS: 17 water',
 '18. MODIS: 18 wooded tundra',
 '19. MODIS: 19 mixed tundra',
 '20. MODIS: 20 barren tundra',]
mod_des=[mod_des[i].split(':')[1][3:] for i in range(17)]

modis_usgs={
1:[14],
2:[13],
3:[12],
4:[11],
5:[15],
6:[9],
7:[8],
8:[0],
9:[10],
10:[7],
11:[17,18],
12:[2,3,4],
13:[1],
14:[5,6],
15:[24],
16:[19],
17:[16],
18:[21],
19:[22,23],
20:[20]
}
modis_usgs2={str(i):modis_usgs[i] for i in modis_usgs}
modis_usgs2.update({'Res3':[16]})
usgs_nam={
1:'USGS_urban',
2:'USGS_drycrop',
3:'USGS_irrcrop',
4:'USGS_cropgrass',
5:'USGS_cropwdlnd',
6:'USGS_shrubgrass',
7:'USGS_grassland',
8:'USGS_shrubland',
9:'USGS_shrubland',
10:'USGS_savanna',
11:'USGS_decidforest',
12:'USGS_decidforest',
13:'USGS_evbrdleaf',
14:'USGS_coniferfor',
15:'USGS_mxforest',
16:'USGS_water',
17:'USGS_wetwoods',
18:'USGS_wetwoods',
19:'USGS_sprsbarren',
20:'USGS_mxtundra',
21:'USGS_woodtundr',
22:'USGS_mxtundra',
24:'USGS_snowice',
}

fname='beld4.EAsia_81K.ncf'
nc0 = netCDF4.Dataset(fname, 'r')
V0=[list(filter(lambda x:nc0.variables[x].ndim==j, [i for i in nc0.variables])) for j in [1,2,3,4]]
nt,nlay,nrow,ncol=(nc0.variables['MODIS_0'].shape[i] for i in range(4))
var=np.zeros(shape=(25,nrow,ncol))
c=0
for i in modis_usgs2:
    v='MODIS_'+i
    if i=='17':v=v='MODIS_0'
    if v not in V0[3]:continue
    var[c,:,:]=nc0[v][0,0,:,:]
    c+=1

# nc=/home/kuang/mac/cmaqruns/2016base/Spatial-Allocator/data/beld3/b3_a.tile10.nzero.ncf
# ncks -d ROW,0,52 -d COL,0,52 -d VAR,0,18 -v TFLAG,USGS_coniferfor,USGS_cropgrass,USGS_cropwdlnd,USGS_decidforest,USGS_drycrop,USGS_evbrdleaf,USGS_grassland,USGS_irrcrop,USGS_mxforest,USGS_mxtundra,USGS_savanna,USGS_shrubgrass,USGS_shrubland,USGS_snowice,USGS_sprsbarren,USGS_urban,USGS_water,USGS_wetwoods,USGS_woodtundr $nc USGS_EAsia_81K.nc
# nc=beld4.EAsia_81K.ncf
# ncpdq -O -a TSTEP,VAR,DATE-TIME $nc a;ncks -O --mk_rec_dmn TSTEP a b
# ncrcat -O b USGS_EAsia_81K.nc c
# ncks -A USGS_EAsia_81K.nc c;mv c USGS_EAsia_81K.nc
# nc=USGS_EAsia_81K.nc
# ncpdq -O -a TSTEP,VAR,DATE-TIME $nc a;ncks -O --mk_rec_dmn TSTEP a $nc

fname='USGS_EAsia_81K.nc'
nc = netCDF4.Dataset(fname, 'r+')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
for v in V[3]:
  nc[v][:]=0.
usgs=[i for i in V[3] if 'USGS' in i]
c=0
for i in modis_usgs2:
    v='MODIS_'+i
    if i=='17':v=v='MODIS_0'
    if v not in V0[3]:continue
    if np.sum(var[c,:,:])==0:continue
    for u in modis_usgs2[i]:
        if u==0:continue
        vv=usgs_nam[u]
        if vv not in V[3]:continue
        nc[vv][0,0,:,:]+=var[c,:,:]
    c+=1
var=np.zeros(shape=(len(usgs),nrow,ncol))
for v in usgs:
  iv=usgs.index(v)
  var[iv,:,:]=nc[v][0,0,:,:]
  mxnc=np.max(var[iv,:,:])
  if mxnc>1:
    var[iv,:,:]/=mxnc
sumv=np.sum(var[:,:,:],axis=0)  
idx=np.where(sumv>0)
for v in usgs:
  iv=usgs.index(v)
  var[iv,idx[0][:],idx[1][:]]/=sumv[idx[0][:],idx[1][:]]
  nc[v][0,0,:,:]=100.*var[iv,:,:]
atts=['CDATE',  'CTIME', 'EXEC_ID', 'FILEDESC', 'FTYPE', 'GDNAM', 'GDTYP', 'HISTORY', 'IOAPI_VERSION', 'NCO', 'NCOLS', 'NLAYS', 'NROWS',
 'NTHIK', 'NVARS', 'P_ALP', 'P_BET', 'P_GAM', 'SDATE', 'STIME', 'TSTEP', 'UPNAM', 'VGLVLS', 'VGTOP', 'VGTYP', 'WDATE', 
 'WTIME', 'XCELL', 'XCENT', 'XORIG', 'YCELL', 'YCENT', 'YORIG']
if nc.XORIG != nc0.XORIG:
  for i in atts:
    exec('nc.'+i+'=nc0.'+i)
nc['TFLAG'][0,:,0]=nc.SDATE
nc['TFLAG'][0,:,1]=nc.STIME
nc.NVARS=len(V[3])
nc.TSTEP=24*30*10000
s=''
for i in V[3]:
  s+=i+' '*(16-len(i))
print(s)  
# ncatted -a VAR-LIST,global,o,c,"..." $nc
nc.close()    
