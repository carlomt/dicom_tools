#!/usr/bin/env python

import pyfits as pf
import numpy as np
import sys
import argparse
from dicom_tools import qualcosa

def main(argv=None):
    parser = argparse.ArgumentParser()
    
    

    parser.add_argument('out_file_name', type=str, help='out_file',default='out.fits' )
    parser.add_argument('-input_files', type=str,nargs='+', help='input files',default=None,required=True )
    
    args = parser.parse_args()
    
    merge_out_analysis_files(args.input_files,args.out_file_name)
    
def merge_out_analysis_files(files_list,out_file):
    
    

    qualcosa.fare(.....)

            
                        
if __name__=="__main__":
    main(sys.argv)
        
