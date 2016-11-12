#!/usr/bin/python
import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
from dicom_tools.FileReader import FileReader
#from dicom_tools.read_files import read_files
from scipy import ndimage

class Window(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)

        outfname="out.root"
        inpath="."
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="increase output verbosity",
                            action="store_true")
        parser.add_argument("-r", "--raw", help="read raw data",
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
        self.layer=0
        
        if args.outfile:
            outfname = args.outfile
            
        if args.inputpath:
            inpath = args.inputpath
            
        if args.layer:
            self.layer = args.layer

        self.raw = args.raw    

        freader = FileReader(inpath, False, args.verbose)
        # dataRGB, unusedROI = read_files(inpath, False, args.verbose, False)
        if self.raw:
            data, unusedROI = freader.read(True)
            self.scaleFactor = 1
            self.data = data[:,:,::-1]
        else:
            dataRGB, unusedROI = freader.read(False)
            self.scaleFactor = freader.scaleFactor
            self.data = dataRGB[:,:,::-1,0]
        # 
        # self.data = dataRGB[:,:,::-1,:]

        #dataswappedX = np.swapaxes(np.swapaxes(self.data,0,1),1,2)
        self.dataswappedX = np.swapaxes(np.swapaxes(self.data,0,1),1,2)[:,::-1,::-1]
        self.dataswappedY = np.swapaxes(self.data,0,2)[:,:,::-1]
        
        if args.verbose:
            print(data.shape)
            print("layer: ",self.layer)

        self.xview = args.xview
        self.yview = args.yview

        self.img1a = pg.ImageItem()
        self.arr = None
        self.updatemain()

        if self.xview:
            imgScaleFactor= 1./freader.scaleFactor
        elif self.yview:
            imgScaleFactor= 1./freader.scaleFactor
        else:
            imgScaleFactor= 1.

            
        self.button_next = QtGui.QPushButton('Next', self)
        self.button_prev = QtGui.QPushButton('Prev', self)
        self.button_next.clicked.connect(self.nextimg)
        self.button_prev.clicked.connect(self.previmg)
        # layout = QtGui.QVBoxLayout(self)
        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.button_next,1,1)
        layout.addWidget(self.button_prev,2,1)

        label = QtGui.QLabel("Click on a line segment to add a new handle. Right click on a handle to remove.")
        
        # label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label,0,0)    
        
            
        self.p1 = pg.PlotWidget()
        self.p1.setAspectLocked(True,imgScaleFactor)
        self.p1.addItem(self.img1a)
        # imv = pg.ImageView(imageItem=img1a)
        layout.addWidget(self.p1,1,0,10,1)

        self.img1b = pg.ImageItem()
        self.roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True)
        self.p2 = pg.PlotWidget()
        # self.p2.disableAutoRange('xy')
        self.p2.setAspectLocked(True,imgScaleFactor)
        self.p2.addItem(self.img1b)
        self.p1.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update)
        layout.addWidget(self.p2,11,0,10,1)

    def update(self):
        thisroi = self.roi.getArrayRegion(self.arr, self.img1a).astype(int)
        self.img1b.setImage(thisroi, levels=(0, self.arr.max()))

        # print(type(thisroi[0][0]))
        # print("shape: ",thisroi.shape)
        # print("size:  ",thisroi.size)
        # print("min:   ",thisroi.min())
        # print("max:   ",thisroi.max())
        # print("mean:  ",thisroi.mean())
        # print("mean:  ", ndimage.mean(thisroi))
        # print("sd:    ", ndimage.standard_deviation(thisroi))
        # print("sum:   ", ndimage.sum(thisroi))
        # # print(thisroi
        # # print("entropy: ",entropy(thisroi, disk(5))
        # # print("maximum: ",maximum(thisroi, disk(5))
        # # print("\n"
        # # print(disk(5)
        # print("\n")
        self.p2.autoRange()

       

    def updatemain(self):
        print "updating",self.layer
        if self.xview:
            # dataswappedX = np.swapaxes(self.data,0,1)
            self.arr=self.dataswappedX[self.layer]
        elif self.yview:
            # dataswappedY = np.swapaxes(self.data,0,2)
            self.arr=self.dataswappedY[self.layer]
        else:
            self.arr=self.data[self.layer]
        self.img1a.setImage(self.arr)
        self.img1a.updateImage()
        
    def nextimg(self):
        if self.xview or self.yview:
            self.layer +=1
        else:
            self.layer += int(self.scaleFactor+0.5)
        self.updatemain()

    def previmg(self):
        if self.xview or self.yview:
            self.layer -=1
        else:
            self.layer -= int(self.scaleFactor+0.5)
        self.updatemain()        


    
        

        
    # def handleButton(self):
    #     print ('Hello World')

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
