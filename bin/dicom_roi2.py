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
import os

# class Window(QtGui.QWidget):
class Window(QtGui.QMainWindow): 

    def __init__(self):
        # QtGui.QWidget.__init__(self)
        super(Window, self).__init__()
        # self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("DICOM roi (v2)")
        # self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))

        widgetWindow = QtGui.QWidget(self)
        self.setCentralWidget(widgetWindow)
        
        outfname="roi.txt"
        self.inpath="."
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="increase output verbosity",
                            action="store_true")
        parser.add_argument("-r", "--raw", help="dont read raw data",
                            action="store_true")
        parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
        parser.add_argument("-o", "--outfile", help="define output file name (default roi.txt)")
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
            self.inpath = args.inputpath
            
        if args.layer:
            self.layer = args.layer

        self.raw = not args.raw
        
        saveFile = QtGui.QAction("&Save File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        # self.statusBar()

        mainMenu = self.menuBar()
        
        fileMenu = mainMenu.addMenu('&File')
        # fileMenu.addAction(extractAction)
        # fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        self.verbose = args.verbose
        
        freader = FileReader(self.inpath, False, args.verbose)
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
        self.firsttime = True
        self.updatemain()

        if self.xview:
            imgScaleFactor= 1./freader.scaleFactor
        elif self.yview:
            imgScaleFactor= 1./freader.scaleFactor
        else:
            imgScaleFactor= 1.

        self.rois = [None]*len(self.data)
            
        self.button_next = QtGui.QPushButton('Next', self)
        self.button_prev = QtGui.QPushButton('Prev', self)
        self.button_next.clicked.connect(self.nextimg)
        self.button_prev.clicked.connect(self.previmg)
        # layout = QtGui.QVBoxLayout(self)
        # layout = QtGui.QGridLayout(self)
        layout = QtGui.QGridLayout(widgetWindow)
        layout.addWidget(self.button_next,1,1)
        layout.addWidget(self.button_prev,2,1)
        self.button_setroi = QtGui.QPushButton('Set ROI', self)
        self.button_setroi.clicked.connect(self.setROI)
        layout.addWidget(self.button_setroi,11,1)
        self.button_delroi = QtGui.QPushButton('Del ROI', self)
        self.button_delroi.clicked.connect(self.delROI)
        layout.addWidget(self.button_delroi,12,1)
        
        label = QtGui.QLabel("Click on a line segment to add a new handle. Right click on a handle to remove.")        
        # label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label,0,0)    

        self.label_layer = QtGui.QLabel("layer: "+str(self.layer+1)+"/"+str(len(self.data)))
        self.label_shape = QtGui.QLabel("shape: "+str(self.arr.shape))
        self.label_size = QtGui.QLabel("size: "+str(self.arr.size))
        self.label_min = QtGui.QLabel("min: "+str(self.arr.min()))
        self.label_max = QtGui.QLabel("max: "+str(self.arr.max()))
        self.label_mean = QtGui.QLabel("mean: "+str(self.arr.mean()))
        self.label_sd = QtGui.QLabel("sd: "+str(ndimage.mean(self.arr)))
        self.label_sum = QtGui.QLabel("sum: "+str(ndimage.sum(self.arr)))
        layout.addWidget(self.label_layer,3,1)
        layout.addWidget(self.label_shape,4,1)
        layout.addWidget(self.label_size,5,1)
        layout.addWidget(self.label_min,6,1)
        layout.addWidget(self.label_max,7,1)
        layout.addWidget(self.label_mean,8,1)
        layout.addWidget(self.label_sd,9,1)
        layout.addWidget(self.label_sum,10,1)

        self.roisSetted = 0
        self.label2_roisSetted = QtGui.QLabel("ROI setted: 0")
        self.label2_shape = QtGui.QLabel()
        self.label2_size = QtGui.QLabel()
        self.label2_min = QtGui.QLabel()
        self.label2_max = QtGui.QLabel()
        self.label2_mean = QtGui.QLabel()
        self.label2_sd = QtGui.QLabel()
        self.label2_sum = QtGui.QLabel()
        layout.addWidget(self.label2_roisSetted,13,1)
        layout.addWidget(self.label2_shape,14,1)
        layout.addWidget(self.label2_size,15,1)
        layout.addWidget(self.label2_min,16,1)
        layout.addWidget(self.label2_max,17,1)
        layout.addWidget(self.label2_mean,18,1)
        layout.addWidget(self.label2_sd,19,1)
        layout.addWidget(self.label2_sum,20,1)
                                      
        self.p1 = pg.PlotWidget()
        self.p1.setAspectLocked(True,imgScaleFactor)
        self.p1.addItem(self.img1a)
        # imv = pg.ImageView(imageItem=img1a)
        layout.addWidget(self.p1,1,0,10,1)

        self.img1b = pg.ImageItem()
        self.roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True)
        # if self.rois[self.layer]:
        #     self.roi = self.rois[self.layer]
        self.p2 = pg.PlotWidget()
        # self.p2.disableAutoRange('xy')
        self.p2.setAspectLocked(True,imgScaleFactor)
        self.p2.addItem(self.img1b)
        self.p1.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update)
        layout.addWidget(self.p2,11,0,10,1)

    def update(self):
        thisroi = self.roi.getArrayRegion(self.arr, self.img1a).astype(float)
        self.img1b.setImage(thisroi, levels=(0, self.arr.max()))
        self.label2_shape.setText("shape: "+str(thisroi.shape))
        self.label2_size.setText("size: "+str(thisroi.size))
        self.label2_min.setText("min: "+str(thisroi.min()))
        self.label2_max.setText("max: "+str(thisroi.max()))
        self.label2_mean.setText("mean: "+str(thisroi.mean()))
        self.label2_sd.setText("sd: "+str( ndimage.standard_deviation(thisroi) ))
        self.label2_sum.setText("sum: "+str( ndimage.sum(thisroi) ))
        # # print("entropy: ",entropy(thisroi, disk(5))
        # # print("maximum: ",maximum(thisroi, disk(5))
        # # print("\n"
        # # print(disk(5)
        # print("\n")
        self.p2.autoRange()

       

    def updatemain(self):
        if self.verbose:
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
        if self.firsttime:
            self.firsttime = False
        else:
            if self.verbose:
                print self.rois
            if self.rois[self.layer]:
                # self.p1.removeItem(self.roi)
                # self.restorePolyLineState(self.roi, self.rois[self.layer])
                self.roi.setState(self.rois[self.layer])
                # self.p1.addItem(self.roi)
                
            self.update()
            self.label_layer.setText("layer: "+str(self.layer+1)+"/"+str(len(self.data)))
        self.img1a.updateImage()
                    
        
    def nextimg(self):
        if self.layer < (len(self.data)-1):
            if self.xview or self.yview:
                self.layer +=1
            else:
                self.layer += int(self.scaleFactor+0.5)
            self.updatemain()

    def previmg(self):
        if self.layer > 0:            
            if self.xview or self.yview:
                self.layer -=1
            else:
                self.layer -= int(self.scaleFactor+0.5)
            self.updatemain()        

    def setROI(self):
        # self.rois[self.layer] = self.savePolyLineState(self.roi)
        self.rois[self.layer] = self.roi.saveState()
        self.roisSetted += 1
        self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))

    def delROI(self):
        if self.rois[self.layer]:
            self.rois[self.layer] = None
            self.roisSetted -= 1
            self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))        
        
    def file_save(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name,'w')
        text = os.path.abspath(self.inpath)
        file.write(text)
        file.close()
        
    # def savePolyLineState(self, pl):
    #     state = pl.getState()
    #     state['closed'] = pl.closed
    #     state['points'] = [tuple(h.pos()) for h in pl.getHandles()]
    #     return state

    # def restorePolyLineState(self, pl, state):
    #     print state
    #     while len(pl.getHandles()) > 0:
    #         pl.removeHandle(pl.getHandles()[0])
    #     for p in state['points']:
    #         pl.addFreeHandle(p)
    #     pl.closed = state['closed']        
    #     start = -1 if pl.closed else 0
    #     for i in range(start, len(pl.handles)-1):
    #         pl.addSegment(pl.handles[i]['item'], pl.handles[i+1]['item'])
        
    # def handleButton(self):
    #     print ('Hello World')

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
