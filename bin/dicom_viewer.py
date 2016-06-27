#!/usr/bin/python

import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
import sys

#def main(argv=None):




outfname="out.root"
inpath="."

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")


args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

if args.inputpath:
    inpath = args.inputpath


infiles=glob.glob(inpath+"/*.dcm")

if args.verbose:
    print "input directory:\n",inpath
    print "output file name:\n",outfname

    # print "input files:\n",infiles

    print len(infiles)," files will be imported"

dicoms=[]


for thisfile in infiles:
    dicoms.append(dicom.read_file(thisfile))

data=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape)


for i, thisdicom in enumerate(dicoms):
    pix_arr  = thisdicom.pixel_array
    data[i] = pix_arr.T


app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('pyqtgraph example: ImageView')

#roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True

## Display the data and assign each frame a time value from 1.0 to 3.0
imv.setImage(data, xvals=np.linspace(0., len(data), data.shape[0]))
    
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    # main(sys.argv)
