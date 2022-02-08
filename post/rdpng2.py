import pp
import numpy as np
import cv2
from sklearn.cluster import KMeans
from PIL import Image
from save_surfer import *
from mostfreqword import *

def ColorDistance(rgb1,rgb2):
    '''d = {} distance between two colors(3)'''
    rm = 0.5*(rgb1[0]+rgb2[0])/256
    return sum((2+rm,4,max(0,3-rm))*(rgb1-rgb2)**2)**0.5

def maping(mn2,image2,x):
    return [ColorDistance(image2[:],x[k,:]) for k in xrange(484)] 
def map_min(mn2,ll):
    return [ll[i,:].index(min(ll[i,:])) for i in xrange(mn2[0]*mn2[1])]
def rms(a):
    return np.sqrt(np.mean(np.square(a)))

image = cv2.imread('legend.png')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
mn=image.shape
image = image.reshape((mn[0] * mn[1], 3))
clt = KMeans(algorithm='auto', copy_x=True, init='k-means++', max_iter=300, \
    n_clusters=484, n_init=10, n_jobs=-1, precompute_distances='auto', \
    random_state=None, tol=0.0001, verbose=0)
kmeans=clt.fit(image)
x=np.array(clt.cluster_centers_)
for i in xrange(484):
    rgb=x[i,:]
    if abs(np.mean(rgb)-rms(rgb)) < 1.5:
        for j in xrange(mn[0]*mn[1]):
            if kmeans.labels_[j] == i: kmeans.labels_[j]=-1
           
category=np.reshape(kmeans.labels_,(-1,mn[1]))
categoryx=[mostfreqword(category[:,i]) for i in xrange(483)]

image2 = cv2.imread('171010/17101000.png')
image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
mn2=image2.shape
image2 = image2.reshape((mn2[0] * mn2[1], 3))
clt2 = KMeans(algorithm='auto', copy_x=True, init='k-means++', max_iter=300, \
    n_clusters=200, n_init=10, n_jobs=-1, precompute_distances='auto', \
    random_state=None, tol=0.0001, verbose=0)
kmeans2=clt2.fit(image2)
x2=np.array(clt2.cluster_centers_)
category2=np.reshape(kmeans2.labels_,(-1,mn2[1]))

mmapR=[]
for i in xrange(200):
    ldel=[ColorDistance(x[j,:],x2[i,:]) for j in xrange(484)]
    mmapR.append(ldel.index(min(ldel)))
conc=category2
for i in xrange(mn2[0]):
    for j in xrange(mn2[1]):
        m=mmapR[category2[i,j]] #index of x
        if m in categoryx[:]:
            conc[i,j]=(float(categoryx[:].index(m)))**2/484*2
        else:
            conc[i,j]=0

fname_d='dict.grd'
len2=877.50*2
len1=len2/7.88*9.98 #measured on powerpoint
len1x=len2/7.88*14.52 #measured on powerpoint
mnx=-len1x/2
mxx=+len1x/2
mny=-len1/2
mxy=+len1/2
(nyd,nxd)=(mn2[0],mn2[1])
delx=(mxx-mnx)/(nxd-1)
dely=(mxy-mny)/(nyd-1)
xx=[mnx+delx*i for i in xrange(nxd)]
yy=[mny+dely*i for i in xrange(nyd)]
c0=np.empty([nxd,nyd])
for i in xrange(nxd):
    for j in xrange(nyd):
        c0[i,j]=conc[nyd-j-1,i]
mnx2=-len2/2
mxx2=+len2/2
mny2=-len2/2
mxy2=+len2/2
(nx2,ny2)=(65,65)
delx2=(mxx2-mnx2)/nx2
dely2=(mxy2-mny2)/ny2
xx2=[mnx2+delx2*i for i in xrange(nx2)]
yy2=[mny2+dely2*i for i in xrange(ny2)]
cn=np.empty([nx2,ny2])

for i in xrange(nx2):
    for j in xrange(ny2):
        sum1=0
        sum2=0
        ic=int((xx2[i]-mnx)/delx)
        jc=int((yy2[j]-mny)/dely)
        for ii in xrange(max(0,ic-3),min(ic+3,nxd)):
            for jj in xrange(max(0,jc-3),min(jc+3,nyd)):
                d2=(xx2[i]-xx[ii])**2+(yy2[j]-yy[jj])**2
                if d2==0: 
                   cn[i,j]=c0[ii,jj]
                   break
                if c0[ii,jj]<=0:continue
                sum1=sum1+1/d2
                sum2=sum2+c0[ii,jj]/d2
            if d2==0: break
        if d2==0: 
           cn[i,j]=c0[ii,jj]
        else:
            if sum1*sum2 == 0:
                cn[i,j]=0.
            else:
                cn[i,j]=sum2/sum1
save_surfer(fname_d,nx2,ny2,mnx2,mny2,mxx2,mxy2,np.matrix.transpose(cn).reshape(nx2*ny2))

