import numpy as np

def convertTypes(input_type):
    if isinstance(input_type,np.uint8):
        return '%d'
    if isinstance(input_type,np.float16):
        return '%.18e'
    if isinstance(input_type,np.string_):
        return '%s'    
    
