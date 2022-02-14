from PseudoNetCDF.camxfiles.Memmaps import uamiv
import numpy as np
import netCDF4
from pandas import *

#read the interio point indices
fname='/nas1/cmaqruns/2016base/data/land/epic_festc1.4_20180516/gridmask/TWN_CNTY_3X3.nc'
nc = netCDF4.Dataset(fname,'r')
V=[list(filter(lambda x:nc.variables[x].ndim==j, [i for i in nc.variables])) for j in [1,2,3,4]]
s=[i for i in V[3] if len(i)==2 and i!='QT']
nt, nlay, nrow, ncol = (nc.variables[V[3][0]].shape[i] for i in range(4))
var=np.zeros(shape=(nrow,ncol))
for i in s:
  var+=nc.variables[i][0,0,:,:]
idx=np.where(var>0.)

#the avrg files were processed by dmavrg, 8 hr daily max O3 is highlighted
v="O3eD"
#boundary indices
S,N,W,E=[(1,i) for i in range(1,ncol-1)],[(nrow-2,i) for i in range(1,ncol-1)],[(i,ncol-2) for i in range(1,nrow-1)],[(i,ncol-2) for i in range(1,nrow-1)]
Sb,Nb=np.array(S).flatten().reshape(81,2),np.array(S).flatten().reshape(81,2)
Wb,Eb=np.array(W).flatten().reshape(135,2),np.array(E).flatten().reshape(135,2)
lenBC=sum([len(i) for i in [S,N,W,E]])
seq='SNWE'

#initalized the dataframe
df=DataFrame({})
for m in range(1,13):
  fname='16{:02d}baseEF3.S.grd01D'.format(m)
  conc= uamiv(fname,'r+')
  nt, nlay, nrow, ncol = (conc.variables[v].shape[i] for i in range(4))
  # surface daily mean UV10 were also been prepared by dmavrg
  fmet='/nas1/camxruns/2016_v7/met/16{:02d}d4.2dD'.format(m)
  uv10= uamiv(fmet,'r')
  #inward time and location indices at each boundaries
  Si=np.where(uv10.variables['V10_MpSD'][:,0,Sb[:,0],Sb[:,1]]>0)
  Ni=np.where(uv10.variables['V10_MpSD'][:,0,Nb[:,0],Nb[:,1]]<0)
  Wi=np.where(uv10.variables['U10_MpSD'][:,0,Wb[:,0],Wb[:,1]]>0)
  Ei=np.where(uv10.variables['U10_MpSD'][:,0,Eb[:,0],Eb[:,1]]<0)
  bc=np.zeros(shape=(4,nt))
  for s in seq:
    o3bc=[]
    exec('ii='+s+'i')
    for t in range(nt):
      if t in set(ii[0]):
        idxs=np.where(ii[0]==t)
        if s=='S':avg=np.mean(conc.variables[v][t,0,1,Si[1][idxs[0]]])
        if s=='N':avg=np.mean(conc.variables[v][t,0,nrow-2,Ni[1][idxs[0]]])
        if s=='W':avg=np.mean(conc.variables[v][t,0,Wi[1][idxs[0]],1])
        if s=='E':avg=np.mean(conc.variables[v][t,0,Ei[1][idxs[0]],ncol-2])
        o3bc.append(avg)
      else:
        o3bc.append(0.)
    js=seq.index(s)
    bc[js,:]=np.array(o3bc)
  #sort the max. 400 pts among interio points and take mean
  o3in=[]
  for t in range(nt):
    a=list(conc.variables[v][t,0,idx[0],idx[1]])
    a.sort()
    o3in.append(np.mean(a[-lenBC:])) 
  js=seq.index(s)
  DD={'JDATE':np.array(conc.variables['TFLAG'][:,0,0]),'o3in':o3in}
  for s in seq:
    js=seq.index(s)
    DD.update({s:bc[js,:]})
  df=df.append(DataFrame(DD),ignore_index=True)
bcm=[]
for i in range(len(df)):
  a=np.array(df.iloc[i,2:6])
  bcm.append(np.nanmean(np.where(a>0,a,np.nan)))
df['bcR']=[j/i for i,j in zip(list(df.o3in),bcm)]
df.set_index('JDATE').to_csv('bc-in.csv')

P,N,R=[],[],[]
for p in range(60,101):
  a=df.loc[df.o3in>p]
  N.append(len(a))
  R.append(np.mean(a.bcR))
  P.append(p)
DD={}
for s in 'PNR':
  exec('DD.update({"'+s+'":'+s+'})')
dfp=DataFrame(DD)
dfp.set_index('P').to_csv('dfp.csv')
