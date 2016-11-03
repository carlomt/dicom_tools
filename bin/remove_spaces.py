#!/usr/bin/python

import os
import argparse
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def removespaces(pathnd):
    path = pathnd.decode("utf8")
    # tree = dict(name=os.path.basename(path), children=[])
    lst = os.listdir(path)
    for name in lst:
        fn = os.path.join(path, name)
        if os.path.isdir(fn):
            newfn = os.path.join(path, name.replace(' ', '_'))
            os.rename(fn, newfn)
            removespaces(newfn)
        else:
            print fn
            os.rename(fn, os.path.join(path, name.replace(' ', '_')))

inpath = "./"

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")


args = parser.parse_args()

if args.inputpath:
    inpath = args.inputpath

removespaces(inpath)

        

            
