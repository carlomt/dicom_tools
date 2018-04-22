#!/usr/bin/python

#import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import sys
from dicom_tools.make_histo import make_histo
from dicom_tools.read_files import read_files
#import nrrd
#import ROOT
#import matplotlib.pyplot as plt
#from scipy import interpolate

#def main(argv=None):



outfname="out.root"
inpath="./"

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-f", "--filterROI", help="filter the image with a ROI (folder path, nrrd file supported)")

group = parser.add_mutually_exclusive_group()
group.add_argument("-y", "--yview", help="swap axes",
                    action="store_true")
group.add_argument("-x", "--xview", help="swap axes",
                    action="store_true")


args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

if args.inputpath:
    inpath = args.inputpath

dataRGB, ROI = read_files(inpath,  args.filterROI, args.verbose)
if args.verbose:
    print(dataRGB.shape)    
    
dataswappedY = np.swapaxes(dataRGB,0,2)
#dataswappedX = np.fliplr(np.swapaxes(np.swapaxes(dataRGB,0,1),1,2))
dataswappedX = np.swapaxes(np.swapaxes(dataRGB,0,1),1,2)
    
    
# dataM=np.multiply(data,ROI)

app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()
# p1.scene().addItem(imv)

# if args.xview:
#     imv.setMinimumSize(dataswappedX.shape[1], dataswappedX.shape[2])
# elif args.yview:
#     imv.setMinimumSize(dataswappedY.shape[1], dataswappedY.shape[2])
    
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('dicom_viewer')

#roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True

# print "data.shape[0]", data.shape[0]
# print "dataswappedX.shape[0]", dataswappedX.shape[0]
# print "dataswappedY.shape[0]", dataswappedY.shape[0]
# print np.linspace(0, len(dataswappedX), dataswappedX.shape[0])

## Display the data and assign each frame a time value from 1.0 to 3.0
# if args.xview:
#     imv.setImage(dataswappedX, xvals=np.linspace(0, len(dataswappedX), dataswappedX.shape[0]))
# elif args.yview:
#     imv.setImage(dataswappedY, xvals=np.linspace(0, len(dataswappedY), dataswappedY.shape[0]))
# else:
#     imv.setImage(dataRGB, xvals=np.linspace(0, len(data), data.shape[0]))
if args.xview:
    # p1.setXRange(0,dicoms[0].SliceThickness*len(dicoms))
    # imv.setXRange(0,dicoms[0].SliceThickness*len(dicoms))
    imv.setImage(dataswappedX, xvals=np.linspace(0, dataswappedX.shape[0], dataswappedX.shape[0] ))
elif args.yview:
    imv.setImage(dataswappedY, xvals=np.linspace(0,  dataswappedY.shape[0],  dataswappedY.shape[0] ))
else:
    imv.setImage(dataRGB, xvals=np.linspace(0, dataRGB.shape[0], dataRGB.shape[0] ))

# ConstPixelDims = (int(dicoms[0].Rows), int(dicoms[0].Columns), len(dicoms))
# print("#D numpy dimensions x,y,z:\n",ConstPixelDims)
# # Load spacing values (in mm)                                                                                            
# ConstPixelSpacing = (float(dicoms[0].PixelSpacing[0]), float(dicoms[0].PixelSpacing[1]), float(dicoms[0].SliceThickness))
# print("pixel spacing:\n",ConstPixelSpacing)
# #calculate axis                                                                                                          
# x = np.arange(0.0, (ConstPixelDims[0])*ConstPixelSpacing[0], ConstPixelSpacing[0])
# y = np.arange(0.0, (ConstPixelDims[1])*ConstPixelSpacing[1], ConstPixelSpacing[1])
# z = np.arange(0.0, (ConstPixelDims[2])*ConstPixelSpacing[2], ConstPixelSpacing[2])
# # The array is sized based on 'ConstPixelDims'                                                                           
# print(y)
# plt.figure(dpi=100)
# plt.axes().set_aspect('auto', 'box')
# plt.set_cmap(plt.gray())
# # plt.pcolormesh(z, y, np.flipud(data[:,:,2]))
# plt.pcolormesh(z, y, np.flipud(data[:,: ,20].T))
# plt.show()    
# canvas = ROOT.TCanvas("C","c",800,600)
# his.Draw()


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    # main(sys.argv)
