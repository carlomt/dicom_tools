import numpy as np
import nrrd

class nrrdFileHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose


    def read(self, inFileName):
        nrrdROItmp, nrrdROIoptions = nrrd.read(inFileName)
        nrrdROI = nrrdROItmp.swapaxes(0,1).swapaxes(0,2)
        return nrrdROI[::-1,:,::-1]

    def write(self, outFileName, data):
        if self.verbose:
            print("nrrdFileHandler: type(data)",type(data),"len(data)",len(data))
            
        outData = data.astype(int)
        outData = outData[::-1,:,:]
        outData = outData[:,:,::-1]
        outData= outData.swapaxes(0,2).swapaxes(0,1)
        if not str(outFileName).endswith('.nrrd'):
            filename = outFileName+".nrrd"
        nrrd.write(outFileName, outData)
    
    
