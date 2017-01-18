import numpy as np
from skimage.measure import grid_points_in_poly
from dicom_tools.roiFileHandler import roiFileHandler


def myroi2roi(myrois, shape, verbose=False):
    if verbose:
        print("myroi2roi: called \n")
    outroi = np.full(shape,False,dtype=bool)
    if len(myrois) != len(outroi):
        print("error: len rois = ",len(rois)," but len dicom=",len(outroi))

    for myroi, layer in zip(myrois,outroi):
        if not myroi is None:
            layer = grid_points_in_poly(layer.shape, myroi['points'])
    if verbose:
        print("myroi2roi: returning \n")
    return outroi
