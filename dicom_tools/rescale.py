from __future__ import print_function
import numpy as np
from skimage import exposure
from skimage import img_as_ubyte, img_as_uint

def rescale16bit(imgIn, verbose=False):
    # if imgIn.min()<0:
    #     print("rescale16bit: WARNING imgIn has negative value")
    # if imgIn.max() < 2**16:
    #     return imgIn.astype(np.uint16)
    # print("rescale16bit: WARNING imgIn has values greater than 2^16, rescaling (max: ",imgIn.max(),")")
    # return exposure.rescale_intensity(imgIn,in_range='uint16')
    #.astype(np.uint16)
    imgOut = exposure.rescale_intensity(imgIn, in_range='uint16')
    imgOut *= 2**16
    imgOut = imgOut.astype(np.uint16)
    # imgIn /= imgIn.max()
    return img_as_uint(imgOut)    

def rescale8bit(imgIn, verbose=False):
    # if imgIn.min()<0:
    #     print("rescale8bit: WARNING imgIn has negative value")
    # if imgIn.max() < 2**8:
    #     return imgIn.astype(np.uint8)    
    # tmp = rescale16bit(imgIn, verbose)
    # print("rescale8bit: WARNING imgIn has values greater than 2^8, rescaling (max: ",imgIn.max(),")")
    # output = exposure.rescale_intensity(tmp,in_range='uint8')
    #.astype(np.uint8)
    # imgIn = exposure.rescale_intensity(imgIn, in_range='uint16')    
    # imgIn /= imgIn.max()
    # return img_as_ubyte(imgOut)    

    imgOut = exposure.rescale_intensity(imgIn, in_range='uint16')
    imgOut *= 2**8
    imgOut = imgOut.astype(np.uint8)
    # imgIn /= imgIn.max()
    return img_as_ubyte(imgOut)    
