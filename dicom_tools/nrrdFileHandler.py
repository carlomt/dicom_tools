import numpy as np
import nrrd

class nrrdFileHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose


    def read(self, inFileName):
        nrrdROItmp, nrrdROIoptions = nrrd.read(inFileName)
        nrrdROI = nrrdROItmp.swapaxes(0,1).swapaxes(0,2)
        return nrrdROI[::-1,:,::-1]
    
    
