from matplotlib import  pylab as plt
import numpy as np
from scipy import stats

class fractal:

    def __init__(self, verbose=False):
        self.verbose = verbose

    def frattali(self,roi):

        #CV plt.ion()
        #CV plt.clf()        

        assex = []
        assey = []
        bx = roi[:,1].size
        by = roi[1,:].size
        
        for size in range(2,15):

            px=int(bx/size) #ciclo for
            py=int(by/size) #ciclo for

            count=0
            nx=0
            ny=0

            for ny in range (0,py):
                for nx in range (0,px):
                    count = count + roi[nx*size:(nx+1)*size,ny*size:(ny+1)*size].max()

            assex.append(np.log(1./size))
            assey.append(np.log(count))

        nassex=np.array(assex)
        nassey=np.array(assey)

        #CVplt.plot(assex,assey, 'ro',label='Data')
        #CVplt.ylabel("log(#box)")
        #CVplt.axis([min(assex)-1,max(assex)+1, min(assex)-1,max(assey)+10])
        #CVplt.grid()

        (slope, intercept, r_value, p_value, std_err) = stats.linregress(nassex, nassey)
        
        #CVprint("slope", slope)
        #CVprint("intercept", intercept)
        #CVprint("r-squared:", r_value**2)
        #CVplt.plot(nassex, intercept + slope*nassex, 'r', label='fitted line')
        #CVplt.xlabel('log(1/size) slope: %lf ' %slope)
        
        #CVplt.legend()
        #CVplt.show()

        return slope
