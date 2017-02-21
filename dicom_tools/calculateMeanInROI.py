import numpy as np

def calculateMeanInROI(data, roi, verbose=False):
    normarea = roi*data
    meaninroi = normarea.sum()/np.count_nonzero(normarea)
    if verbose:
        print("calculateMeanInROI: data.shape",data.shape)
        print("calculateMeanInROI: returning mean",meaninroi) 
    return meaninroi
