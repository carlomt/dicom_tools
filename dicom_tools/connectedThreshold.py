import SimpleITK as sitk
import numpy as np

def connectedThreshold(img, seed, lowerThreshold, upperThreshold):
    imgOriginal = img
    convertOutput = False
    if type(img) != sitk.SimpleITK.Image:
        imgOriginal = sitk.GetImageFromArray(img)
        convertOutput = True
    lstSeeds = [seed]
    # lstSeeds = [(158,150)]
    
    print(type(lstSeeds))
    labelWhiteMatter = 1
    imgWhiteMatter = sitk.ConnectedThreshold(image1=imgOriginal, seedList=lstSeeds,  lower=lowerThreshold, upper=upperThreshold, replaceValue=labelWhiteMatter)
    if convertOutput:
        imgWhiteMatter = sitk.GetArrayFromImage(imgWhiteMatter)

    return imgWhiteMatter
