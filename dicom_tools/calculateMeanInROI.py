import numpy as np

def calculateMeanInROI(data, roi, verbose=False):
    normarea = roi*data
    meaninroi = normarea.sum()/np.count_nonzero(normarea)

    return meaninroi
