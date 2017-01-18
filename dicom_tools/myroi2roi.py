import numpy as np
from skimage.measure import grid_points_in_poly
from dicom_tools.roiFileHandler import roiFileHandler


def myroi2roi(myrois, shape, verbose=False):
    if self.verbose:
        print("myroi2roi: called \n")
    outroi = np.full(shape,False,dtype=bool)
    if len(myrois) != len(outroi):
        print("error: len rois = ",len(rois)," but len dicom=",len(outroi))

    for myroi, layer in zip(myrois,outroi):
        layer = grid_points_in_poly(layer.shape, myroi['points'])
    if self.verbose:
        print("myroi2roi: returning \n")
    return outroi
