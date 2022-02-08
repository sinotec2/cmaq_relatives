import numpy
def save_surfer(fname,nx,ny,x0,y0,xn,yn,grd):
    cmin=numpy.min(grd)
    cmax=numpy.max(grd)
    output=('DSAA\n',(nx,ny),(x0,xn),(y0,yn),(cmin,cmax),grd)
    fo=open(fname,'rw+')
    fo.write(output[0])
    for i in range(1,2):
        numpy.savetxt(fo,numpy.array(output[i]).reshape(1,-1),fmt='%i') 
    for i in range(2,6):
        numpy.savetxt(fo,numpy.array(output[i]).reshape(1,-1)) 
    fo.close()
    return
def save_surferi(fname,nx,ny,x0,y0,xn,yn,grd):
    cmin=numpy.min(grd).astype(int)
    cmax=numpy.max(grd).astype(int)
    output=('DSAA\n',(nx,ny),(x0,xn),(y0,yn),(cmin,cmax),grd)
    fo=open(fname,'rw+')
    fo.write(output[0])
    for i in range(1,6):
        numpy.savetxt(fo,numpy.array(output[i]).reshape(1,-1),fmt='%i') 
    fo.close()
    return


