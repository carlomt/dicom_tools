#!/usr/bin/python
import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
import dicom_tools.pyqtgraph as pg
import dicom
from dicom_tools.FileReader import FileReader
from scipy import ndimage
import os
from dicom_tools.roiFileHandler import roiFileHandler
from dicom_tools.highlight_color import highlight_color
from dicom_tools.Normalizer import Normalizer

# class Window(QtGui.QWidget):
class Window_dicom_roi_RGB(QtGui.QMainWindow): 

    def __init__(self):
        # QtGui.QWidget.__init__(self)
        super(Window_dicom_roi_RGB, self).__init__()
        # self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("DICOM roi (vRGB)")
        # self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))

        widgetWindow = QtGui.QWidget(self)
        self.setCentralWidget(widgetWindow)
        
        outfname="roi.txt"
        self.inpath="."
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="increase output verbosity",
                            action="store_true")
        parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
        parser.add_argument("-o", "--outfile", help="define output file name (default roi.txt)")
        parser.add_argument("-l", "--layer", help="select layer",
                            type=int)
        parser.add_argument("-f", "--filterROI", help="filter the image with a ROI (folder path, nrrd file supported)")
        parser.add_argument("-c","--colorRange", help="highlight a color range (expects sometghin like 100:200)")
        parser.add_argument("-r","--raw", help="do not normalize",action="store_true")
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


        openFile = QtGui.QAction("&Open ROI File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open ROI File')
        openFile.triggered.connect(self.file_open)
        
        saveFile = QtGui.QAction("&Save ROI on File", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save ROI on File')
        saveFile.triggered.connect(self.file_save)
        
        # self.statusBar()

        mainMenu = self.menuBar()
        
        fileMenu = mainMenu.addMenu('&ROI')
        # fileMenu.addAction(extractAction)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        self.verbose = args.verbose
        
        freader = FileReader(self.inpath, args.filterROI, args.verbose)
        # dataRGB, unusedROI = read_files(inpath, False, args.verbose, False)

        dataRGB, unusedROI = freader.read(False)
        self.scaleFactor = freader.scaleFactor

        if not args.raw:
            thisNormalizer = Normalizer(self.verbose)
            thisNormalizer.setRootOutput()
            self.dataZ = thisNormalizer.match_all(dataRGB)
            thisNormalizer.writeRootOutputOnFile("checkNorm.root")
        else:
            self.dataZ = dataRGB 
        
        if args.colorRange:
            self.dataZ = highlight_color(dataRGB,args.colorRange,args.verbose)
        

        # self.dataZ = np.swapaxes(dataRGB[:,:,:,:],0,1)
        # 
        # self.data = dataRGB[:,:,::-1,:]

        #dataswappedX = np.swapaxes(np.swapaxes(self.data,0,1),1,2)
        self.dataswappedX = np.swapaxes(np.swapaxes(self.dataZ,0,1),1,2)[:,::-1,::-1,:]
        self.dataswappedY = np.swapaxes(self.dataZ,0,2)[:,:,::-1,:]
        
        if args.verbose:
            print("shape:", self.dataZ.shape)
            print("shape of a channel:", self.dataZ[:,:,:,0].shape)
            print("layer: ",self.layer)

        self.xview = args.xview
        self.yview = args.yview

        self.img1a = pg.ImageItem()
        self.arr = None
        self.firsttime = True

        if self.xview:
            imgScaleFactor= 1./freader.scaleFactor
            self.data =  self.dataswappedX
        elif self.yview:
            imgScaleFactor= 1./freader.scaleFactor
            self.data =  self.dataswappedY
        else:
            imgScaleFactor= 1.
            self.data =  self.dataZ

        if self.verbose:
            print("data len:",len(self.data[:,:,:,0]))

        self.updatemain()            
            
        self.rois = [None]*len(self.data[:,:,:,0])
            
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
        layout.addWidget(self.button_setroi,12,1)
        self.button_delroi = QtGui.QPushButton('Del ROI', self)
        self.button_delroi.clicked.connect(self.delROI)
        layout.addWidget(self.button_delroi,13,1)
        
        label = QtGui.QLabel("Click on a line segment to add a new handle. Right click on a handle to remove.")        
        # label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label,0,0)    

        self.label_layer = QtGui.QLabel("layer: "+str(self.layer+1)+"/"+str(len(self.data[:,:,:,0])))
        self.label_shape = QtGui.QLabel("shape: "+str(self.arr[:,:,0].shape))
        self.label_size = QtGui.QLabel("size: "+str(self.arr[:,:,0].size))
        self.label_min = QtGui.QLabel("min: "+str(self.arr[:,:,0].min()))
        self.label_max = QtGui.QLabel("max: "+str(self.arr[:,:,0].max()))
        self.label_mean = QtGui.QLabel("mean: "+str(self.arr[:,:,0].mean()))
        self.label_sd = QtGui.QLabel("sd: "+str(ndimage.standard_deviation(self.arr[:,:,0])))
        self.label_sum = QtGui.QLabel("sum: "+str(ndimage.sum(self.arr[:,:,0])))
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
        layout.addWidget(self.label2_roisSetted,14,1)
        layout.addWidget(self.label2_shape,15,1)
        layout.addWidget(self.label2_size,16,1)
        layout.addWidget(self.label2_min,17,1)
        layout.addWidget(self.label2_max,18,1)
        layout.addWidget(self.label2_mean,19,1)
        layout.addWidget(self.label2_sd,20,1)
        layout.addWidget(self.label2_sum,21,1)
                                      
        self.p1 = pg.PlotWidget()
        self.p1.setAspectLocked(True,imgScaleFactor)
        self.p1.addItem(self.img1a)
        # imv = pg.ImageView(imageItem=img1a)
        layout.addWidget(self.p1,1,0,10,1)

        # self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(len(self.data[:,:,:,0]))
        self.slider.setValue(self.layer+1)
        self.slider.setSingleStep(1)
        self.slider.setFocus()
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus) 
        # self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        # self.slider.setTickInterval(5)

        # self.slider.sliderMoved.connect(self.slider_jump_to)
        self.slider.valueChanged.connect(self.slider_jump_to)
        layout.addWidget(self.slider,11,0)

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
        layout.addWidget(self.p2,12,0,10,1)

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
            self.label_layer.setText("layer: "+str(self.layer+1)+"/"+str(len(self.data[:,:,:,0])))
            self.label_shape.setText("shape: "+str(self.arr[:,:,0].shape))
            self.label_size.setText("size: "+str(self.arr[:,:,0].size))
            self.label_min.setText("min: "+str(self.arr[:,:,0].min()))
            self.label_max.setText("max: "+str(self.arr[:,:,0].max()))
            self.label_mean.setText("mean: "+str(self.arr[:,:,0].mean()))
            self.label_sd.setText("sd: "+str(ndimage.standard_deviation(self.arr[:,:,0])))
            self.label_sum.setText("sum: "+str(ndimage.sum(self.arr[:,:,0])))
        self.img1a.updateImage()

        
    def nextimg(self):
        if self.layer < (len(self.data[:,:,:,0])-1):
            # if self.xview or self.yview:
            #     self.layer +=1
            # else:
            #     self.layer += int(self.scaleFactor+0.5)
            self.layer +=1
            self.slider.setValue(self.layer+1)
            self.updatemain()

    def previmg(self):
        if self.layer > 0:            
            # if self.xview or self.yview:
            #     self.layer -=1
            # else:
            #     self.layer -= int(self.scaleFactor+0.5)
            self.layer -=1
            self.slider.setValue(self.layer+1)                
            self.updatemain()        

    def setROI(self):
        # self.rois[self.layer] = self.savePolyLineState(self.roi)
        self.rois[self.layer] = self.roi.saveState()
        self.roisSetted = 0
        for thisroi in self.rois:
            if thisroi:
                self.roisSetted +=1
        self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))

    def delROI(self):
        if self.rois[self.layer]:
            self.rois[self.layer] = None
            for thisroi in self.rois:
                if thisroi:
                    self.roisSetted -= 1
            self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))        
        
    def file_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        writer = roiFileHandler()
        writer.dicomsPath = os.path.abspath(self.inpath)
        if not str(filename).endswith('.myroi'):
            filename = filename+".myroi"
        writer.write(filename, self.rois, self.roisSetted)


    def file_open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','ROI files (*.myroi)')
        reader = roiFileHandler()
        originalpath = reader.dicomsPath
        self.rois, self.roisSetted = reader.read(filename)
        self.updatemain()
        self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))
                
    def slider_jump_to(self):
        self.layer = self.slider.value()-1
        self.updatemain()
        
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window_dicom_roi_RGB()
    window.show()
    sys.exit(app.exec_())
