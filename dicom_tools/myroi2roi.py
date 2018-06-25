from __future__ import print_function
import numpy as np
from skimage.measure import grid_points_in_poly
from dicom_tools.roiFileHandler import roiFileHandler


def convert1roi(myroi, layershape, verbose=False):
    points = np.array(myroi['points'])
    shift = np.array(myroi['pos'])
    shift -= np.array([0.5,0.5])
    if verbose:
        print(type(shift))
        print(myroi)
        print(points+shift)
    return grid_points_in_poly(layershape, points+shift)    

def myroi2roi(myrois, shape, verbose=False):
    if verbose:
        print("myroi2roi: called")
        print("myroi2roi: shape", shape)
    outroi = np.full(shape,False,dtype=bool)
  

    if outroi.ndim > 2:
        if len(myrois) != len(outroi):
            print("error: len rois = ",len(myrois)," but len dicom=",len(outroi))
        for n, myroi in enumerate(myrois):
            if not myroi is None:
                outroi[n] = convert1roi(myroi, outroi[n].shape, verbose)
                if verbose:
                    print("myroi2roi: layer",n,"tot true pixels",outroi[n].sum())
            elif verbose:
                print("myroi2roi: layer",n,"myroi is None")
    else:
        if verbose:        
            print("myroi2roi: only one layer")
        outroi = convert1roi(myrois, outroi.shape, verbose)
        if verbose:
            print("myroi2roi: tot true pixels", outroi.sum())
            
    if verbose:
        print("myroi2roi: returning \n")
    return outroi
