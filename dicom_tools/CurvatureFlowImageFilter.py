import numpy as np
import SimpleITK as sitk

# https://itk.org/SimpleITKDoxygen/html/classitk_1_1simple_1_1CurvatureFlowImageFilter.html#details

def CurvatureFlowImageFilter(img, verbose=False):
    
    imgOriginal = sitk.GetImageFromArray(img)
    imgSmooth = sitk.CurvatureFlow(image1=imgOriginal,
                                        timeStep=0.125,
                                        numberOfIterations=5)

    
    return sitk.GetArrayFromImage(imgSmooth)
