from __future__ import print_function
import numpy as np

def intensity_cut(data, ROI, icut, verbose=False):
    nFette = len(data)    
    for layer in xrange(0,nFette):
        if ROI[layer].any():
            imax = np.max(data[layer]*ROI[layer])
            data[layer][data[layer] < (icut*imax)] = 0

    return data
