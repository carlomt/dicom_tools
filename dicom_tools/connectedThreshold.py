import SimpleITK as sitk
import numpy as np
import ctypes

def to_uint32(i):
    return ctypes.c_uint32(i).value

def connectedThreshold(img, seedCoordinates, lowerThreshold, upperThreshold):
    imgOriginal = img
    convertOutput = False
    if type(img) != sitk.SimpleITK.Image:
        imgOriginal = sitk.GetImageFromArray(img)
        convertOutput = True
    lstSeeds = [ (to_uint32(int(seed[1])), to_uint32(int(seed[0])) )]
    #ITK inverte gli assi rispetto a numpy
    
    # lstSeeds = [(158,150)]
    # lstSeeds = [seed]
     
    # print(type(lstSeeds))
    labelWhiteMatter = 1
    imgWhiteMatter = sitk.ConnectedThreshold(image1=imgOriginal, seedList=lstSeeds,  lower=lowerThreshold, upper=upperThreshold, replaceValue=labelWhiteMatter)
    if convertOutput:
        imgWhiteMatter = sitk.GetArrayFromImage(imgWhiteMatter)

    return imgWhiteMatter
