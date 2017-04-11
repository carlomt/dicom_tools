from matplotlib import  pylab as plt
import numpy as np

def colorize(img, mask=None, verbose=False):

    my_cm = plt.cm.get_cmap('jet')
    normed_data = (img - np.min(img)) / (np.max(img) - np.min(img))
    rgb_img = my_cm(normed_data)
    if verbose:
        print("colorize output shape",rgb_img.shape)

    if mask is not None:
        for i in range(0,3):
            rgb_img[:,:,i] -= rgb_img[:,:,i]*np.logical_not(mask)
    return rgb_img
