#!/usr/bin/python
import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
from dicom_tools.read_files import read_files

class Window(QtGui.QWidget):

    def updatemain(self):
        print "updating",self.layer
        if self.xview:
            dataswappedX = np.swapaxes(np.swapaxes(self.data,0,1),1,2)
            arr=dataswappedX[self.layer]
        elif self.yview:
            dataswappedY = np.swapaxes(self.data,0,2)
            arr=dataswappedY[self.layer]
        else:
            arr=self.data[self.layer]
        self.img1a.setImage(arr)
        self.img1a.updateImage()
        
    def nextimg(self):
        self.layer +=1
        self.updatemain()

    def previmg(self):
        self.layer -=1
        self.updatemain()        


    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.button_next = QtGui.QPushButton('Next', self)
        self.button_prev = QtGui.QPushButton('Prev', self)
        self.button_next.clicked.connect(self.nextimg)
        self.button_prev.clicked.connect(self.previmg)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.button_next)
        layout.addWidget(self.button_prev)


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
        self.layer=0
        
        if args.outfile:
            outfname = args.outfile
            
        if args.inputpath:
            inpath = args.inputpath
            
        if args.layer:
            self.layer = args.layer
                
        dataRGB, ROI = read_files(inpath, False, args.verbose, False)
        self.data = dataRGB[:,:,::-1,0]
                
        if args.verbose:
            print(data.shape)
            print("layer: ",self.layer)

        self.xview = args.xview
        self.yview = args.yview

        self.img1a = pg.ImageItem()
        self.updatemain()

        self.p1 = pg.PlotWidget()
        # imv = pg.ImageView(imageItem=img1a)
        layout.addWidget(self.p1)


        
    # def handleButton(self):
    #     print ('Hello World')

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
