import numpy as np
from skimage.measure import grid_points_in_poly
from dicom_tools.roiFileHandler import roiFileHandler


def myroi2roi(myrois, shape, verbose=False):
    if verbose:
        print("myroi2roi: called \n")
    outroi = np.full(shape,False,dtype=bool)
    if len(myrois) != len(outroi):
        print("error: len rois = ",len(rois)," but len dicom=",len(outroi))

    for n, myroi, layer in enumerate(zip(myrois,outroi)):
        if not myroi is None:
            layer = grid_points_in_poly(layer.shape, myroi['points'])
            if verbose:
                print("myroi2roi: layer",n,"tot true pixels",layer.sum())
        elif verbose:
            print("myroi2roi: layer",n,"myroi is None")
                
    if verbose:
        print("myroi2roi: returning \n")
    return outroi
