from __future__ import print_function
import numpy as np

def getLayerWithLargerROI(ROI, verbose=False):
    if verbose:
        print("getLayerWithLargerROI")
        print("len(ROI)",len(ROI))
    nPixelMax = 0
    layerMax = 0
    for layer in xrange(0,len(ROI)):
        # thisNPixel = len(np.ravel(np.nonzero(ROI[layer])))
        thisNPixel = np.sum(np.ravel(ROI[layer]))
        if thisNPixel > nPixelMax:
            nPixelMax = thisNPixel
            layerMax = layer

    if verbose:
        print("getLayerWithLargerROI returning",layerMax,"which has",nPixelMax,"pixels")
    return layerMax
