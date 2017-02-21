import numpy as np

def calculateMeanInROI(data, roi, verbose=False):
    if verbose:
        print("calculateMeanInROI: data.shape()",data.shape())
    normarea = roi*data
    meaninroi = normarea.sum()/np.count_nonzero(normarea)

    return meaninroi
