from __future__ import print_function
import numpy as np

def convertTypes(input_type):
    if input_type is np.uint8:
        return '%d'
    if input_type is np.float16:
        return '%.18e'
    if input_type is np.string_:
        return '%s'
    raise TypeError(input_type,"not recognized.")


def convertTypesROOT(input_type):
    if input_type is np.uint8:
        return 'I'
    if input_type is np.float16:
        return 'F'
    if input_type is np.string_:
        return 'C'
    raise TypeError(input_type,"not recognized.")
    
