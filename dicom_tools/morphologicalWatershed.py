import SimpleITK as sitk
import numpy as np
import ctypes

def to_uint32(i):
    return ctypes.c_uint32(i).value

def morphologicalWatershed(img, level=10,fullyConnected=False):
    imgOriginal = img
    convertOutput = False
    if type(img) != sitk.SimpleITK.Image:
        imgOriginal = sitk.GetImageFromArray(img)
        convertOutput = True
    feature_img = sitk.GradientMagnitude(imgOriginal)
    ws_img = sitk.MorphologicalWatershed(feature_img, level=level, markWatershedLine=True, fullyConnected=fullyConnected)
    ws_img = sitk.LabelToRGB(ws_img)

    if convertOutput:
        ws_img = sitk.GetArrayFromImage(ws_img).astype(float) 
    
    return ws_img
