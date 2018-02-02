import numpy as np
#import SimpleITK as sitk
#import scipy
from scipy.ndimage.filters import gaussian_laplace

# https://itk.org/SimpleITKDoxygen/html/classitk_1_1simple_1_1CurvatureFlowImageFilter.html#details

def GaussianLaplaceFilter(data, sigma, verbose=False):

    # bx = image[:,1,1].size
    # by = image[1,:,1].size

    # pr_out=np.zeros((bx, by))

    result = np.zeros(data.shape)
    
    for layer in xrange(0, len(data)):
        image = data[layer]

        # pr_out = np.zeros(image.shape)
        prova = gaussian_laplace(image, sigma, result[layer], mode='constant', cval=0.0)
        result[layer] = (result[layer] + abs(result[layer].min()))*100
    return result
