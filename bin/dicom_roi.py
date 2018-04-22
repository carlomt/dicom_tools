#!/usr/bin/python

import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import sys
from dicom_tools.read_files import read_files

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
parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
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

dataRGB, ROI = read_files(inpath, False, args.verbose, False)
data = dataRGB[:,:,::-1,0]

if args.verbose:
    print(data.shape)
    print("layer: ",layer)

dataswappedY = np.swapaxes(data,0,2)
dataswappedX = np.swapaxes(np.swapaxes(data,0,1),1,2)

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

# orig = np.fliplr(arr)
    
img1a = pg.ImageItem(arr)
#img1a = pg.ImageItem()
imv = pg.ImageView(imageItem=img1a)
# if args.xview:
#     imv.setImage(dataswappedX, xvals=np.linspace(0, dataswappedX.shape[0], dataswappedX.shape[0] ))
# elif args.yview:
#     imv.setImage(dataswappedY, xvals=np.linspace(0,  dataswappedY.shape[0],  dataswappedY.shape[0] ))
# else:
#     imv.setImage(data, xvals=np.linspace(0, data.shape[0], data.shape[0] ))

v1a.addItem(img1a)
img1b = pg.ImageItem()
v1b.addItem(img1b)
# v1a.disableAutoRange('xy')
v1a.autoRange()
#v1b.autoRange()
v1b.disableAutoRange('xy')


#rois = []

roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True)

def update(roi):
    thisroi = roi.getArrayRegion(arr, img1a).astype(int)
    img1b.setImage(thisroi, levels=(0, arr.max()))

    print(type(thisroi[0][0]))
    print("shape: ",thisroi.shape)
    print("size:  ",thisroi.size)
    print("min:   ",thisroi.min())
    print("max:   ",thisroi.max())
    print("mean:  ",thisroi.mean())
    print("mean:  ", ndimage.mean(thisroi))
    print("sd:    ", ndimage.standard_deviation(thisroi))
    print("sum:   ", ndimage.sum(thisroi))
    # print(thisroi
    # print("entropy: ",entropy(thisroi, disk(5))
    # print("maximum: ",maximum(thisroi, disk(5))
    # print("\n"
    # print(disk(5)
    print("\n")
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
