import numpy as np
#import SimpleITK as sitk
import scipy

# https://itk.org/SimpleITKDoxygen/html/classitk_1_1simple_1_1CurvatureFlowImageFilter.html#details

def GaussianLaplaceFilter(image,sigma,simple, verbose=False):

    bx = image[:,1,1].size
    by = image[1,:,1].size

    pr_out=np.zeros((bx, by))

    prova=scipy.ndimage.filters.gaussian_laplace(image[:,:,0],sigma,pr_out, mode='constant', cval=0.0)

    if simple:
        pr_out[pr_out[:,:]<1] = 0;
        pr_out[pr_out[:,:]>1] = 1;

    return pr_out
