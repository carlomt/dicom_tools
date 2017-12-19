from matplotlib import  pylab as plt
import numpy as np
from scipy import stats

class fractal:

    def __init__(self, verbose=False):
        self.verbose = verbose

    def frattali(self,roi):

#        plt.ion()
#        plt.clf()        

        assex = []
        assey = []
        bx = roi[:,1].size
        by = roi[1,:].size
        
        for size in range(2,15):

            px=int(bx/size) #ciclo for
            py=int(by/size) #ciclo for

#            count=0
            count1=0
            nx=0
            ny=0

            for ny in range (0,py):
                for nx in range (0,px):
#                    count = count + roi[nx*size:(nx+1)*size,ny*size:(ny+1)*size].max()
                    if(np.count_nonzero(roi[nx*size:(nx+1)*size,ny*size:(ny+1)*size])>0):
                        count1=count1 + 1

            assex.append(np.log(1./size))
            assey.append(np.log(count1))

#            print("count:", count)
#            print("count1:", count1)

        nassex=np.array(assex)
        nassey=np.array(assey)

#        plt.plot(assex,assey, 'ro',label='Data')
#        plt.ylabel("log(#box)")
#        plt.axis([min(assex)-1,max(assex)+1, min(assex)-1,max(assey)+10])
#        plt.grid()

        (slope, intercept, r_value, p_value, std_err) = stats.linregress(nassex, nassey)
        
#        print("slope", slope)
#        print("intercept", intercept)
#        print("r-squared:", r_value**2)
#        plt.plot(nassex, intercept + slope*nassex, 'r', label='fitted line')
#        plt.xlabel('log(1/size) slope: %lf ' %slope)
        
#        plt.legend()
#        plt.show()


        return slope
