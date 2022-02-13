import numpy as np
import netCDF4


# cd /nas1/cmaqruns/2018base/data/land
# nc=beld4.EAsia_81K.ncf
# ncks -v MODIS_1,MODIS_2,MODIS_3,MODIS_4,MODIS_5,TFLAG $nc MODIS_1-5_EAsia_81K.nc
fname='MODIS_1-5_EAsia_81K.nc'
nc0 = netCDF4.Dataset(fname, 'r')
var=np.zeros(shape=nc[v].shape)
for i in range(1,6):
    var[:]+=nc0['MODIS_'+str(i)][:]

# ncks -O -d VAR,0 -v MODIS_1,TFLAG $nc forest_EAsia_81K.nc
# ncrename -v MODIS_1,FOREST forest_EAsia_81K.nc
# ncatted -a VAR-LIST,global,o,c,'FOREST          ' forest_EAsia_81K.nc
fname='forest_EAsia_81K.nc'
nc = netCDF4.Dataset(fname, 'r+')
v='FOREST'
nc[v].long_name='FOREST'
nc[v].var_desc='MODIS1~5 summation from WRF geo_em'
nc.NVARS=1
nc[v][:]=var[:]*100.
nc.close()
