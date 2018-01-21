from __future__ import print_function
import numpy as np
from skimage.filters.rank import entropy as skim_entropy
from skimage.morphology import disk as skim_disk
from skimage.morphology import square as skim_square
from skimage import exposure
from skimage import img_as_uint, img_as_ubyte
import ROOT
from dicom_tools.histFromArray import histFromArray
from dicom_tools.rescale import rescale16bit, rescale8bit

def getEntropy(image, ROI=None, square_size=5, verbose=False):
    # image = img_as_ubyte(exposure.rescale_intensity(image, in_range='uint8'))
    image = rescale8bit(image)
    # image = rescale16bit(image)    
    # image = exposure.rescale_intensity(image, in_range='uint16')
    # image = image.astype(np.uint8)
    
    if ROI is None:
        entropyImg = skim_entropy(image,skim_square(square_size))
    else:
        entropyImg = skim_entropy(image,skim_square(square_size), mask=ROI)
    return entropyImg

def getEntropyCircleMask(image, ROI=None, circle_radius=5, verbose=False):
    if verbose:
        message = "getEntropyCircleMask "
        if ROI is not None:
            message += "ROI length "+str(len(ROI))
        message += "circle radius "+str(circle_radius)
        print(message)
        print("type(image) ",type(image))
        print("type(image[0][0]) ",type(image[0][0]))        
    image = rescale8bit(image, verbose)
    if verbose:
        print("type(image[0][0]) ",type(image[0][0]))        
    if ROI is None:
        entropyImg = skim_entropy(image,skim_disk(circle_radius))
    else:
        ROI = ROI.astype(np.bool)
        entropyImg = skim_entropy(image,skim_disk(circle_radius), mask=ROI)
    return entropyImg


def make_histo_entropy(data, ROI, suffix="", verbose=False):
    entropy3D = np.zeros( tuple([len(data)])+data[0,:,:].shape)
    for layer in xrange(0,len(data)):
        entropy3D[layer] = getEntropy(data[layer], ROI[layer])
    
    # his = ROOT.TH1F("entropy"+suffix,"entropy",nbin,binmin,binmax)
    # nbin = 10000
    # binmin=entropy3D.min() *0.8
    # binmax=entropy3D.max() *1.2
    if verbose:
        print("getEntropy creating histogram","hEntropy"+suffix)
    his = histFromArray(data, name="hEntropy"+suffix, verbose=verbose)        
    allhistos = []
    
    for i, layer in enumerate(entropy3D):
        if verbose:
            print("getEntropy creating histogram","hEntropy"+str(i)+suffix)        
        thishisto = histFromArray(layer, name="hEntropy"+str(i)+suffix)
        if thishisto is not None:
            allhistos.append(thishisto)


    return his, allhistos
