#!/usr/bin/python

import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
import sys
# from skimage.filters.rank import entropy
# from skimage.filters.rank import maximum
# from skimage.morphology import disk
from scipy import ndimage

#def main(argv=None):


outfname="out.root"
inpath="."

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-l", "--layer", help="select layer",
                    type=int)

group = parser.add_mutually_exclusive_group()
group.add_argument("-y", "--yview", help="swap axes",
                    action="store_true")
group.add_argument("-x", "--xview", help="swap axes",
                    action="store_true")

args = parser.parse_args()
layer=0

if args.outfile:
    outfname = args.outfile

if args.inputpath:
    inpath = args.inputpath

if args.layer:
    layer = args.layer

    
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
    np.swapaxes(pix_arr,0,1)
    data[i] = pix_arr[::-1].T

dataswappedY = np.swapaxes(data,0,2)
dataswappedX = np.swapaxes(data,0,1)

## create GUI
app = QtGui.QApplication([])
w = pg.GraphicsWindow(size=(1280,768), border=True)
w.setWindowTitle('dicom with  ROI')

text = """Click on a line segment to add a new handle.
Right click on a handle to remove.
"""

w1 = w.addLayout(row=0, col=0)
label1 = w1.addLabel(text, row=0, col=0)
v1a = w1.addViewBox(row=1, col=0, lockAspect=True)
v1b = w1.addViewBox(row=2, col=0, lockAspect=True)
if args.xview:
    arr=dataswappedX[layer]
elif args.yview:
    arr=dataswappedY[layer]
else:
    arr=data[layer]
img1a = pg.ImageItem(arr)
v1a.addItem(img1a)
img1b = pg.ImageItem()
v1b.addItem(img1b)
v1a.disableAutoRange('xy')
v1b.disableAutoRange('xy')
v1a.autoRange()
v1b.autoRange()

#rois = []

roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True)

def update(roi):
    thisroi = roi.getArrayRegion(arr, img1a).astype(int)
    img1b.setImage(thisroi, levels=(0, arr.max()))

    print type(thisroi[0][0])
    print "shape:\t",thisroi.shape
    print "size:\t",thisroi.size
    print "min:\t",thisroi.min()
    print "max:\t",thisroi.max()
    print "mean:\t",thisroi.mean()
    print "mean:\t", ndimage.mean(thisroi)
    print "sd:\t", ndimage.standard_deviation(thisroi)
    print "sum:\t", ndimage.sum(thisroi)
    # print thisroi
    # print "entropy:\t",entropy(thisroi, disk(5))
    # print "maximum:\t",maximum(thisroi, disk(5))
    # print "\n"
    # print disk(5)
    print "\n"
    v1b.autoRange()

roi.sigRegionChanged.connect(update)
v1a.addItem(roi)



## Display the data and assign each frame a time value from 1.0 to 3.0
#imv.setImage(data, xvals=np.linspace(0., len(data), data.shape[0]))
    
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    # main(sys.argv)
