#!/usr/bin/python


import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
import sys
import matplotlib.pyplot as plt

#def main(argv=None):




outfname="out.root"
inpath="./"

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-f", "--filterROI", help="filter the image with a ROI (path)")

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


infiles = glob.glob(inpath+"/*.dcm")

if args.verbose:
    print("input directory:\n",inpath)
    print("output file name:\n",outfname)

    # print "input files:\n",infiles

    print(len(infiles)," files will be imported")

dicoms=[]

for thisfile in infiles:
    dicoms.append(dicom.read_file(thisfile))


# Load dimensions based on the number of rows, columns, and slices (along the Z axis)
ConstPixelDims = (int(dicoms[0].Rows), int(dicoms[0].Columns), len(dicoms))

# Load spacing values (in mm)
ConstPixelSpacing = (float(dicoms[0].PixelSpacing[0]), float(dicoms[0].PixelSpacing[1]), float(dicoms[0].SliceThickness))

xsize = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
ysize = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
zsize = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])

data=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape)
dataRGB=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape+tuple([3]))



ROI=np.full(tuple([len(dicoms)])+dicoms[0].pixel_array.shape,False,dtype=bool)

if args.filterROI:
    inpathROI = args.filterROI
    if args.verbose:
        print("ROI requested, path: ",inpathROI)
    infilesROI = glob.glob(inpathROI+"/*.dcm")
    if args.verbose:
        print(len(infilesROI)," files will be imported for the ROI")
    if len(infilesROI) != len(infiles):
        print("ERROR: in the directory ",inpath," there are ",len(infiles)," dicom files")
        print("while in the ROI directory ",inpathROI," there are ",len(infilesROI)," dicom files")
    dicomsROI=[]
    for infileROI in infilesROI:
        dicomsROI.append(dicom.read_file(infileROI))
    # ROI=np.zeros(tuple([len(dicomsROI)])+dicomsROI[0].pixel_array.shape)

    for i, thisROI in enumerate(dicomsROI):
        pix_arr = thisROI.pixel_array
        ROI[i] = pix_arr.T
    # 

for i, thisdicom in enumerate(dicoms):
    pix_arr  = thisdicom.pixel_array
    data[i] = pix_arr.T
    dataRGB[i,:,:,0] = pix_arr.T 
    dataRGB[i,:,:,2] = dataRGB[i,:,:,1] = pix_arr.T - np.multiply(pix_arr.T,ROI[i])
    # dataRGB[i,:,:,2] = pix_arr.T - np.multiply(pix_arr.T,ROI[i])

    
dataswappedY = np.swapaxes(dataRGB,0,2)
dataswappedX = np.swapaxes(dataRGB,0,1)
    
    
dataM=np.multiply(data,ROI)

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
    imv.setImage(dataRGB, xvals=np.linspace(0, data.shape[0], data.shape[0] ))

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

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

    # main(sys.argv)