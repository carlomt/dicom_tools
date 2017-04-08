import numpy as np
from skimage.filters.rank import entropy as skim_entropy
from skimage.morphology import disk as skim_disk
from skimage.morphology import square as skim_square
from skimage import exposure

def getEntropy(image, ROI=None, square_size=5, verbose=False):
    image = exposure.rescale_intensity(image, in_range='uint16')
    if ROI is None:
        entropyImg = skim_entropy(image,skim_square(square_size))
    else:
        entropyImg = skim_entropy(image,skim_square(square_size), mask=ROI)
    return entropyImg


