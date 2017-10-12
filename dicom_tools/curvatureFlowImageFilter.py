import numpy as np
import SimpleITK as sitk

# https://itk.org/SimpleITKDoxygen/html/classitk_1_1simple_1_1CurvatureFlowImageFilter.html#details

def curvatureFlowImageFilter(img, verbose=False):

    imgOriginal = img
    convertOutput = False
    if type(img) != sitk.SimpleITK.Image:
        imgOriginal = sitk.GetImageFromArray(img)
        convertOutput = True
        
    imgSmooth = sitk.CurvatureFlow(image1=imgOriginal,
                                        timeStep=0.125,
                                        numberOfIterations=5)
    if convertOutput:
        imgSmooth = sitk.GetArrayFromImage(imgSmooth).astype(float) 

    return imgSmooth
