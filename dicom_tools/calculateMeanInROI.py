import numpy as np

def calculateMeanInROI(data, roi, verbose=False):
    if verbose:
        normarea = roi*data
        meaninroi = normarea.sum()/np.count_nonzero(normarea)
        
        print("calculateMeanInROI: data.shape",data.shape)
        print("calculateMeanInROI: returning mean",meaninroi)
        print("calculateMeanInROI: normarea.mean()",normarea.mean())
        print("calculateMeanInROI: np.ma.average(data,weights=roi)",np.ma.average(data,weights=roi))        
        mx = np.ma.masked_array(data,mask=np.logical_not(roi))
        print("calculateMeanInROI: mx.mean()",mx.mean())
    return np.ma.average(data,weights=roi)
