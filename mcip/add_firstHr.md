# 增添mcip結果的初始小時值

```bash
#!/bin/bash
for i in $(ls [GL]*.nc);do python ~/bin/add_firstHr.py ${i};done
for i in $(ls [MS]*.nc);do ncks -O -d TSTEP,0,0 $i ${i}_1; python ~/bin/add_firstHr.py ${i}_1;ncrcat -O ${i}_1 ${i} a;mv a ${i};rm ${i}_1;done
```

```python
import netCDF4
import sys
fname=sys.argv[1]
nc = netCDF4.Dataset(fname,'r+')
nc.variables['TFLAG'][0,:,1]=[0 for i in range(nc.NVARS)]
nc.STIME=0
nc.close()
```
