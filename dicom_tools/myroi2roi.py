import numpy as np
from skimage.measure import grid_points_in_poly
from dicom_tools.roiFileHandler import roiFileHandler


def myroi2roi(myrois, shape, verbose=False):
    if verbose:
        print("myroi2roi: called")
    outroi = np.full(shape,False,dtype=bool)
    if len(myrois) != len(outroi):
        print("error: len rois = ",len(rois)," but len dicom=",len(outroi))

    for n, myroi in enumerate(myrois):
        if not myroi is None:
            outroi[n] = grid_points_in_poly(outroi[n].shape, myroi['points'])
            if verbose:
                print("myroi2roi: layer",n,"tot true pixels",outroi[n].sum())
        elif verbose:
            print("myroi2roi: layer",n,"myroi is None")
        
    if verbose:
        print("myroi2roi: returning \n")
    return outroi
