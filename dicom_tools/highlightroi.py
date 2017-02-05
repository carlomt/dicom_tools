import numpy as np

def highligthroi(data, roi, verobse=False):
    data[:,:,2] = data[:,:,2] - np.multiply(data[:,:,2],roi)
    return data
        
