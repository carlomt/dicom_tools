#!/usr/bin/python
from __future__ import print_function
import glob
import argparse
import numpy as np
from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
from dicom_tools.pyqtgraph.Qt import QtWidgets
import dicom_tools.pyqtgraph as pg
from dicom_tools.FileReader import FileReader
from scipy import ndimage
import os
import nrrd
from dicom_tools.roiFileHandler import roiFileHandler
from dicom_tools.nrrdFileHandler import nrrdFileHandler
from dicom_tools.highlight_color import highlight_color
from dicom_tools.Normalizer import Normalizer
from dicom_tools.myroi2roi import myroi2roi
from dicom_tools.calculateMeanInROI import calculateMeanInROI
import scipy
from dicom_tools.curvatureFlowImageFilter import curvatureFlowImageFilter
from dicom_tools.gaussianlaplace import GaussianLaplaceFilter #AR
from dicom_tools.connectedThreshold import connectedThreshold
from dicom_tools.morphologicalWatershed import morphologicalWatershed
from dicom_tools.wardHierarchical import wardHierarchical
from dicom_tools.colorize import colorize
from dicom_tools.getEntropy import getEntropy
from dicom_tools.getEntropy import getEntropyCircleMask
from skimage.filters.rank import gradient as skim_gradient

from dicom_tools.rescale import rescale8bit, rescale16bit
from skimage.morphology import square as skim_square

#from scipy.ndimage.morphology import binary_fill_holes
#import ROOT
from dicom_tools.histFromArray import histFromArray
from dicom_tools.getLayerWithLargerROI import getLayerWithLargerROI

import matplotlib.pyplot as plt

from dicom_tools.BrukerMRI import ReadFolder as brukerReadFolder
from dicom_tools.read_plist_roi_file import read_plist_roi_file

from qtconsole.rich_ipython_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

class AboutWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__(parent)
        
        self.closeButton = QtGui.QPushButton(self.tr("&Close"))
        self.closeButton.setDefault(True)
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.addButton(self.closeButton, QtGui.QDialogButtonBox.ActionRole)
        self.closeButton.clicked.connect(self.close)
        # self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        # self.closeButton.connect(self.o)
        # QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.o)

        
        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.append("DICOM tool (v2.2)")
        self.textBrowser.append("for comments and bug reports please write to:")
        self.textBrowser.append("carlo.mancini.terracciano@roma1.infn.it")
        # self.textBrowser.append("site: http://www.roma1.infn.it/~mancinit/?action=Software/dicom_tools")
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.addWidget(self.buttonBox)

    def o(self):
        # print("close the window") 
        self.close()
        
# class Window(QtGui.QWidget):
class Window_dicom_tool(QtGui.QMainWindow): 

    def __init__(self):
        # QtGui.QWidget.__init__(self)
        super(Window_dicom_tool, self).__init__()
        # self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle("DICOM tool (v3.1) [dicom_tools v 0.9]")
        # self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))
        
        widgetWindow = QtGui.QWidget(self)
        self.setCentralWidget(widgetWindow)
        
        outfname="roi.txt"
        self.inpath="."        
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="increase output verbosity",
                            action="store_true")
        parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
        parser.add_argument("-ib", "--inputbruker", help="path of the Bruker directory")        
        parser.add_argument("-o", "--outfile", help="define output file name (default roi.txt)")
        parser.add_argument("-l", "--layer", help="select layer",
                            type=int)
        parser.add_argument("-fp", "--roipath", help="filter the image with a ROI (DICOM folder path)")
        parser.add_argument("-fn", "--roifile", help="filter the image with a ROI (nrrd file)")
        parser.add_argument("-fo", "--roiosirix", help="filter the image with a ROI from Osirix (xml file)")        
        parser.add_argument("-c","--colorRange", help="highlight a color range (expects sometghin like 100:200)")
        parser.add_argument("-r","--raw", help="do not normalize",action="store_true")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-y", "--yview", help="swap axes",
                           action="store_true")
        group.add_argument("-x", "--xview", help="swap axes",
                           action="store_true")
        
        args = parser.parse_args()
        self.layer=0
        self.layerZ=0
        self.layerX=0
        self.layerY=0        
        self.verbose = args.verbose
        self.xview = args.xview
        self.yview = args.yview
        self.zview = not self.xview and not self.yview
        self.imgScaleFactor = 1
        self.secondaryImage3D = False
        self.ROI=[]
        self.lastSeed=(1,1)
        self.leftSideTemporaryWidgets = []

        
        if args.outfile:
            outfname = args.outfile
            
            
        if args.layer:
            self.layer = args.layer

        openDicomDirectory = QtGui.QAction("&Open DICOM Directory", self)
        openDicomDirectory.setShortcut("Ctrl+O")
        openDicomDirectory.setStatusTip("Open DICOM Directory (dcm uncompressed)")
        openDicomDirectory.triggered.connect(self.select_dicom_folder)
            
        # openDicomFile = QtGui.QAction("&Open DICOM File", self)
        # openDicomFile.setStatusTip("Open DICOM File (dcm uncompressed)")
        # openDicomFile.triggered.connect(self.read_dicom_file)
        
        openDicomDirectoryGDCM = QtGui.QAction("&Open DICOM Directory with GDCM", self)
        openDicomDirectoryGDCM.setStatusTip("Open DICOM Directory with GDCM (dcm also compressed)")
        openDicomDirectoryGDCM.triggered.connect(self.select_dicom_folderGDCM)

        openDicomDirectoryBruker = QtGui.QAction("&Open Bruker Directory", self)
        openDicomDirectoryBruker.setStatusTip("Open Bruker Directory with data files")
        openDicomDirectoryBruker.triggered.connect(self.select_dicom_folderBruker)    
        
        openMyROIFile = QtGui.QAction("&Open MyROI File", self)
        # openFile.setShortcut("Ctrl+O")
        openMyROIFile.setStatusTip('Open ROI File (myroi format)')
        openMyROIFile.triggered.connect(self.myroi_file_open)

        openOsirixROIFile = QtGui.QAction("&Open Osirix ROI File", self)
        openOsirixROIFile.setStatusTip('Open Osirix ROI File (xml format)')
        openOsirixROIFile.triggered.connect(self.osirix_roi_file_open)        
        
        saveMyROIFile = QtGui.QAction("&Save ROI on File", self)
        saveMyROIFile.setShortcut("Ctrl+S")
        saveMyROIFile.setStatusTip('Save ROI on File (myroi format)')
        saveMyROIFile.triggered.connect(self.myroi_file_save)

        saveROIonNRRD = QtGui.QAction("&Save ROI on nrrd File", self)
        saveROIonNRRD.setStatusTip('Save ROI on File (nrrd format)')
        saveROIonNRRD.triggered.connect(self.nrrdroi_file_save)

        highlightDCMROIaction = QtGui.QAction("&Highlight DICOM ROI", self)
        highlightDCMROIaction.setStatusTip("&Highlight ROI (dcm folder)")
        highlightDCMROIaction.triggered.connect(self.highlightDCMROI)
        
        highlightnrrdROIaction = QtGui.QAction("&Highlight nrrd ROI", self)
        highlightnrrdROIaction.setStatusTip("&Highlight ROI (nrrd file)")
        highlightnrrdROIaction.triggered.connect(self.highlightnrrdROI)
        
        highlightMyROIaction = QtGui.QAction("&Highlight myroi ROI", self)
        highlightMyROIaction.setStatusTip("&Highlight ROI (myroi file)")
        highlightMyROIaction.triggered.connect(self.highlightMyROI)        
        
        # self.statusBar()
        normalizeHistogramMatching = QtGui.QAction("&Normalize using hm", self)
        # normalizeHistogramMatching.setShortcut("Ctrl+O")
        normalizeHistogramMatching.setStatusTip('Normalize using histogram matching')
        normalizeHistogramMatching.triggered.connect(self.histogram_matching_normalization)

        normalizeToROIAction = QtGui.QAction("&Normalize to ROI", self)
        normalizeToROIAction.setStatusTip("&Normalize to a ROI (myroi file)")
        normalizeToROIAction.triggered.connect(self.normalizeToROI)
        
        switchToZViewAction = QtGui.QAction("&Switch to Z view", self)
        switchToZViewAction.setStatusTip('Switch to Z view')
        switchToZViewAction.triggered.connect(self.switchToZView)
        
        switchToXViewAction = QtGui.QAction("&Switch to X view", self)
        switchToXViewAction.setStatusTip('Switch to X view')
        switchToXViewAction.triggered.connect(self.switchToXView)

        switchToYViewAction = QtGui.QAction("&Switch to Y view", self)
        switchToYViewAction.setStatusTip('Switch to Y view')
        switchToYViewAction.triggered.connect(self.switchToYView)

        # adjusteExposureMainImgAction = QtGui.QAction("&Adjuste Exposure", self)
        # adjusteExposureMainImgAction.setStatusTip('Adjuste exposure')
        # adjusteExposureMainImgAction.triggered.connect(self.adjusteExposureMainImg)

        superimposeSecOnMainAction = QtGui.QAction("&Superimpose secondary image on primary",self)
        superimposeSecOnMainAction.setStatusTip('Superimpose secondary image on primary')
        superimposeSecOnMainAction.triggered.connect(self.superimposeSecondaryToPrimary)
        
        colorMainImgAction = QtGui.QAction("&Use colors for main image", self)
        colorMainImgAction.setStatusTip('Use colors for main image')
        colorMainImgAction.triggered.connect(self.colorMainImg)
        
        saveToTiffAction = QtGui.QAction("&Save to TIFF", self)
        saveToTiffAction.setStatusTip('Save current view to TIFF file')
        saveToTiffAction.triggered.connect(self.saveToTIFFImage)
        saveToPngAction = QtGui.QAction("&Save to PNG", self)
        saveToPngAction.setStatusTip('Save current view to PNG file')
        saveToPngAction.triggered.connect(self.saveToPNGImage)

        show8bitAction = QtGui.QAction("&View in 8 bit", self)
        show8bitAction.setStatusTip("View in 8 bit")
        show8bitAction.triggered.connect(self.show8bit)
        show16bitAction = QtGui.QAction("&View in 16 bit", self)
        show16bitAction.setStatusTip("View in 16 bit")
        show16bitAction.triggered.connect(self.show16bit)

        histoOfAllLayerAction = QtGui.QAction("&Histogram of all layer" ,self)
        histoOfAllLayerAction.setStatusTip('Histogram of all layer')
        histoOfAllLayerAction.triggered.connect(self.histoOfAllLayer)

        entropyAction = QtGui.QAction("&Entropy",self)
        entropyAction.setStatusTip('Entropy')
        entropyAction.triggered.connect(self.entropy)

        gradientAction = QtGui.QAction("&Gradient",self)
        gradientAction.setStatusTip('Gradient')
        gradientAction.triggered.connect(self.gradient)

        goToLayerWithLargerROIAction = QtGui.QAction("&Go to the layer with larger ROI",self)
        goToLayerWithLargerROIAction.setStatusTip('Go to the layer with larger ROI')
        goToLayerWithLargerROIAction.triggered.connect(self.goToLayerWithLargerROI)

        shellAction = QtGui.QAction("&Launch interactive shell",self)
        shellAction.setStatusTip('Launch interactive shell')
        shellAction.triggered.connect(self.launchShell)
        
        entropyInAllROIAction = QtGui.QAction("&Entropy in a 3D ROI (nrrd)",self)
        entropyInAllROIAction.setStatusTip('Entropy in a 3D ROI (nrrd)"')
        entropyInAllROIAction.triggered.connect(self.entropyInAllROI)
        
        aboutAction = QtGui.QAction("&About this program", self)
        aboutAction.setStatusTip('About this program')
        aboutAction.triggered.connect(self.about)

        CurvatureFlowImageFilterAction = QtGui.QAction("&Apply Curvature Flow Filter",self)
        CurvatureFlowImageFilterAction.setStatusTip("Apply Curvature Flow Filter")
        CurvatureFlowImageFilterAction.triggered.connect(self.CurvatureFlowImageFilter)
#AR
        LaplacianFilterAction = QtGui.QAction("&Apply Gaussian Laplace Filter",self)
        LaplacianFilterAction.setStatusTip("Apply Gaussian Laplace Filter")
        LaplacianFilterAction.triggered.connect(self.GaussianLaplaceFilter)

        MorphologicalWatershedAction = QtGui.QAction("&Apply Morphological Watershed",self)
        MorphologicalWatershedAction.setStatusTip("Apply Morphological Watershed")
        MorphologicalWatershedAction.triggered.connect(self.MorphologicalWatershed)

        WardHierarchicalAction = QtGui.QAction("&Apply Ward Hierarchical Clustering",self)
        WardHierarchicalAction.setStatusTip("Apply Ward Hierarchical Clustering")
        WardHierarchicalAction.triggered.connect(self.WardHierarchical)        

        connectedThresholdAction = QtGui.QAction("&Use Connected Threshold",self)
        connectedThresholdAction.setStatusTip("Use Connected Threshold withouth filtering")
        connectedThresholdAction.triggered.connect(self.ActivateConnectedThreshold)

        connectedThresholdFilteredAction = QtGui.QAction("&Use Connected Threshold Filtered",self)
        connectedThresholdFilteredAction.setStatusTip("Use Connected Threshold with Curvature Flow Filter")
        connectedThresholdFilteredAction.triggered.connect(self.ActivateConnectedThresholdFiltered)

        activateManualRoiDesignerAction = QtGui.QAction("&Use Manual ROI definition",self)
        activateManualRoiDesignerAction.setStatusTip("Use Manual ROI definition")
        activateManualRoiDesignerAction.triggered.connect(self.ActivateManualRoiDesigner)
        
        mainMenu = self.menuBar()
        
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openDicomDirectory)
        fileMenu.addAction(openDicomDirectoryGDCM)
        fileMenu.addAction(openDicomDirectoryBruker)        
        fileMenu.addAction(aboutAction)
        
        ROIfileMenu = mainMenu.addMenu('&ROI')
        # fileMenu.addAction(extractAction)
        ROIfileMenu.addAction(openMyROIFile)
        ROIfileMenu.addAction(openOsirixROIFile)        
        ROIfileMenu.addAction(saveMyROIFile)
        ROIfileMenu.addAction(saveROIonNRRD)
        ROIfileMenu.addAction(highlightDCMROIaction)
        ROIfileMenu.addAction(highlightnrrdROIaction)
        ROIfileMenu.addAction(highlightMyROIaction)        
        
        normMenu = mainMenu.addMenu('&Normalization')
        normMenu.addAction(normalizeHistogramMatching)
        normMenu.addAction(normalizeToROIAction)

        viewMenu = mainMenu.addMenu('&View')
        viewMenu.addAction(switchToZViewAction)
        viewMenu.addAction(switchToXViewAction)
        viewMenu.addAction(switchToYViewAction)

        imageMenu = mainMenu.addMenu('&Image')
        # imageMenu.addAction(adjusteExposureMainImgAction)
        imageMenu.addAction(superimposeSecOnMainAction)
        imageMenu.addAction(colorMainImgAction)
        imageMenu.addAction(saveToTiffAction)
        imageMenu.addAction(saveToPngAction)
        imageMenu.addAction(show8bitAction)
        imageMenu.addAction(show16bitAction)        

        analysisMenu = mainMenu.addMenu('&Analysis')
        analysisMenu.addAction(histoOfAllLayerAction)
        analysisMenu.addAction(entropyAction)        
        analysisMenu.addAction(entropyInAllROIAction)
        analysisMenu.addAction(gradientAction)
        analysisMenu.addAction(goToLayerWithLargerROIAction)
        analysisMenu.addAction(shellAction)        

        filtersMenu = mainMenu.addMenu('&Filters')
        filtersMenu.addAction(CurvatureFlowImageFilterAction)
        filtersMenu.addAction(LaplacianFilterAction) #AR

        segmentationMenu = mainMenu.addMenu('&Segmentation')
        segmentationMenu.addAction(activateManualRoiDesignerAction)
        segmentationMenu.addAction(connectedThresholdAction)
        segmentationMenu.addAction(connectedThresholdFilteredAction)                
        segmentationMenu.addAction(MorphologicalWatershedAction)
        segmentationMenu.addAction(WardHierarchicalAction)

            
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(aboutAction)
        
        # if not args.raw:
        #     thisNormalizer = Normalizer(self.verbose)
        #     thisNormalizer.setRootOutput()
        #     self.dataZ = thisNormalizer.match_all(dataRGB)
        #     thisNormalizer.writeRootOutputOnFile("checkNorm.root")
        # else:

        
        if args.colorRange:
            self.dataZ = highlight_color(dataRGB,args.colorRange,args.verbose)
        
        self.RightButtonsCol = 2
        self.LeftButtonsCol = 0
        self.CentralAreaCol = 1
        
        self.img1a = pg.ImageItem()
        self.arr = None
        self.secondaryImage2D=None        
        self.firsttime = True
        self.colorizeSecondaryImage = False
        self.colorizeSecondaryImageWithROI = False
        self.MainImgExposureMax = -1

        self.button_next = QtGui.QPushButton('Next', self)
        self.button_prev = QtGui.QPushButton('Prev', self)
        self.button_next.clicked.connect(self.nextimg)
        self.button_prev.clicked.connect(self.previmg)
        # layout = QtGui.QVBoxLayout(self)
        # layout = QtGui.QGridLayout(self)
        self.layout = QtGui.QGridLayout(widgetWindow)
        self.layout.addWidget(self.button_next,1,self.RightButtonsCol)
        self.layout.addWidget(self.button_prev,2,self.RightButtonsCol)
        self.button_setroi = QtGui.QPushButton('Set ROI', self)
        self.button_setroi.clicked.connect(self.setROI)
        self.layout.addWidget(self.button_setroi,12,self.RightButtonsCol)
        self.button_delroi = QtGui.QPushButton('Del ROI', self)
        self.button_delroi.clicked.connect(self.delROI)
        self.layout.addWidget(self.button_delroi,13,self.RightButtonsCol)
        
        self.label = QtGui.QLabel("Click on a line segment to add a new handle. Right click on a handle to remove.")        
        # label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label,0,self.CentralAreaCol)
        self.manualROI = True
        self.connectedThreshold = False
        self.filterBeforeSegmentation=False
        
        self.label_layer = QtGui.QLabel("layer: ")
        self.label_shape = QtGui.QLabel("shape: ")
        self.label_size = QtGui.QLabel("size: ")
        self.label_min = QtGui.QLabel("min: ")
        self.label_max = QtGui.QLabel("max: ")
        self.label_mean = QtGui.QLabel("mean: ")
        self.label_sd = QtGui.QLabel("sd: ")
        self.label_sum = QtGui.QLabel("sum: ")
        self.layout.addWidget(self.label_layer,3,self.RightButtonsCol)
        self.layout.addWidget(self.label_shape,4,self.RightButtonsCol)
        self.layout.addWidget(self.label_size,5,self.RightButtonsCol)
        self.layout.addWidget(self.label_min,6,self.RightButtonsCol)
        self.layout.addWidget(self.label_max,7,self.RightButtonsCol)
        self.layout.addWidget(self.label_mean,8,self.RightButtonsCol)
        self.layout.addWidget(self.label_sd,9,self.RightButtonsCol)
        self.layout.addWidget(self.label_sum,10,self.RightButtonsCol)

        self.roisSetted = 0
        self.label2_roisSetted = QtGui.QLabel("ROI setted: 0")
        self.label2_shape = QtGui.QLabel()
        self.label2_size = QtGui.QLabel()
        self.label2_min = QtGui.QLabel()
        self.label2_max = QtGui.QLabel()
        self.label2_mean = QtGui.QLabel()
        self.label2_sd = QtGui.QLabel()
        self.label2_sum = QtGui.QLabel()
        self.layout.addWidget(self.label2_roisSetted,14,self.RightButtonsCol)
        self.layout.addWidget(self.label2_shape,15,self.RightButtonsCol)
        self.layout.addWidget(self.label2_size,16,self.RightButtonsCol)
        self.layout.addWidget(self.label2_min,17,self.RightButtonsCol)
        self.layout.addWidget(self.label2_max,18,self.RightButtonsCol)
        self.layout.addWidget(self.label2_mean,19,self.RightButtonsCol)
        self.layout.addWidget(self.label2_sd,20,self.RightButtonsCol)
        self.layout.addWidget(self.label2_sum,21,self.RightButtonsCol)
                                      
        self.p1 = pg.PlotWidget()
        self.p1.setAspectLocked(True,self.imgScaleFactor)
        self.p1.addItem(self.img1a)
        self.p1ViewBox = self.p1.plotItem.vb
        proxy = pg.SignalProxy(self.p1.scene().sigMouseClicked, rateLimit=60, slot=self.mouseMoved)
        self.p1.scene().sigMouseClicked.connect(self.mouseMoved)

        # imv = pg.ImageView(imageItem=img1a)
        self.layout.addWidget(self.p1,1, self.CentralAreaCol,10,1)

        self.ExposureSliderLabel = QtGui.QLabel("Exposure")
        self.layout.addWidget(self.ExposureSliderLabel,1,self.LeftButtonsCol)
            
        self.ExposureSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.ExposureSlider.setFixedWidth(150);
        self.ExposureSlider.setMinimum(1)
        self.ExposureSlider.setMaximum(10000)
        self.ExposureSlider.setValue(10000-3143)
        self.ExposureSlider.setTickPosition(2)
        self.ExposureSlider.setTickInterval(1000)
        self.ExposureSlider.setSingleStep(1)
        self.ExposureSlider.valueChanged.connect(self.changeMainExposure)
        self.layout.addWidget(self.ExposureSlider,2,self.LeftButtonsCol)

        self.label_spacer      = QtGui.QLabel("                        ")        
        self.label_coordinates = QtGui.QLabel("coordinates: (    ,    )")
        self.label_intensity = QtGui.QLabel("intensity: ")
        self.label_spacer2      = QtGui.QLabel("                        ")                
        self.layout.addWidget(self.label_spacer, 3, self.LeftButtonsCol)
        self.layout.addWidget(self.label_coordinates,4,self.LeftButtonsCol)
        self.layout.addWidget(self.label_intensity,5,self.LeftButtonsCol)        
        self.layout.addWidget(self.label_spacer2, 6, self.LeftButtonsCol)
        
        # self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setValue(self.layer+1)
        self.slider.setSingleStep(1)
        self.slider.setFocus()
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus) 
        # self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        # self.slider.setTickInterval(5)

        # self.slider.sliderMoved.connect(self.slider_jump_to)
        self.slider.valueChanged.connect(self.slider_jump_to)
        self.layout.addWidget(self.slider,11,self.CentralAreaCol)

        self.img1b = pg.ImageItem()
        self.roi = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]], pen=(6,9), closed=True)
        # if self.rois[self.layer]:
        #     self.roi = self.rois[self.layer]
        self.p2 = pg.PlotWidget()
        # self.p2.disableAutoRange('xy')
        self.p2.setAspectLocked(True,self.imgScaleFactor)
        self.p2.addItem(self.img1b)
        self.p1.addItem(self.roi)
        self.p2ViewBox = self.p2.plotItem.vb

        self.roi.sigRegionChanged.connect(self.update)
        self.layout.addWidget(self.p2,12, self.CentralAreaCol,10,1)

        proxy = pg.SignalProxy(self.p2.scene().sigMouseClicked, rateLimit=60, slot=self.mouseMoved2)
        self.p2.scene().sigMouseClicked.connect(self.mouseMoved2)


        if args.inputpath:
            self.read_dicom_in_folder(args.inputpath)

        if args.roipath:
            self.read_roi_dicom_in_folder(args.roipath)

        if args.roifile:
            self.read_nrrd_roi(args.roifile)

        if args.roiosirix:
            self.osirix_roi_file_open(args.roiosirix)
            
        if args.inputbruker:
            self.read_dicom_in_folder(args.inputbruker,useBruker=True)
            
            
    def update(self):
        if self.manualROI:
            thisroi = self.roi.getArrayRegion(self.arr, self.img1a).astype(float)
            convertedROI = myroi2roi(self.roi.saveState(), self.arr[:,:,2].shape, self.verbose)
            toshowvalues = np.ma.masked_array(self.arr[:,:,2],mask=np.logical_not(convertedROI))
        if self.connectedThreshold:
            toshowvalues = thisroi = self.arr[:,:,2]*self.bitmapROI[self.layer]
        self.secondaryImage2D = thisroi    
        self.img1b.setImage(thisroi, levels=(0, thisroi.max()))
        self.setlabel2values(toshowvalues)
        # self.p2.autoRange()

    def setImgToMain(self, img):
        self.arr = img
        self.img1a.setImage(img)
        self.img1a.updateImage() 
        
    def updatemain(self):
        
        if self.verbose:
            print("updating",self.layer)
        if self.xview:
            # dataswappedX = np.swapaxes(self.data,0,1)
            self.arr=self.dataswappedX[self.layer]
        elif self.yview:
            # dataswappedY = np.swapaxes(self.data,0,2)
            self.arr=self.dataswappedY[self.layer]
        else:
            self.arr=self.dataZ[self.layer]
        if self.MainImgExposureMax > 0:
            self.img1a.setImage(self.arr, levels=(0, self.MainImgExposureMax))
        else:
            self.img1a.setImage(self.arr)
            if self.verbose:
                print("levels:", self.img1a.getLevels())
        if self.firsttime:
            self.firsttime = False
        else:
            if self.verbose:
                print(self.rois)
            if self.rois[self.layer]:
                # self.p1.removeItem(self.roi)
                # self.restorePolyLineState(self.roi, self.rois[self.layer])
                self.roi.setState(self.rois[self.layer])
                # self.p1.addItem(self.roi)
                
            self.update()
            self.label_layer.setText("layer: "+str(self.layer)+"/"+str(len(self.data[:,:,:,0])))
            self.label_shape.setText("shape: "+str(self.arr[:,:,2].shape))
            self.label_size.setText("size: "+str(self.arr[:,:,2].size))
            self.label_min.setText("min: "+str(self.arr[:,:,2].min()))
            self.label_max.setText("max: "+str(self.arr[:,:,2].max()))
            self.label_mean.setText("mean: "+str(self.arr[:,:,2].mean()))
            self.label_sd.setText("sd: "+str(ndimage.standard_deviation(self.arr[:,:,2])))
            self.label_sum.setText("sum: "+str(ndimage.sum(self.arr[:,:,2])))
        self.img1a.updateImage()
        if self.secondaryImage3D:
            # self.p2.autoRange()
            self.setlabel2values(self.secondaryImage[self.layer])
            self.secondaryImage2D = self.secondaryImage[self.layer]
            if self.colorizeSecondaryImage and self.colorizeSecondaryImageWithROI:
                self.secondaryImage2D = colorize(self.secondaryImage2D,'jet',self.ROI[self.layer],self.verbose)

            self.img1b.setImage(self.secondaryImage2D)
            self.img1b.updateImage()
        
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
        if self.manualROI:
            # self.rois[self.layer] = self.savePolyLineState(self.roi)
            thisroiswassetted=False
            if self.rois[self.layer]:
                thisroiswassetted=True
            self.rois[self.layer] = self.roi.saveState()
            if thisroiswassetted:
                self.dehighlightROI()
            if self.verbose:
                print(self.rois[self.layer])
            convertedROI = myroi2roi(self.rois[self.layer], self.arr[:,:,2].shape, self.verbose)
            # toshowvalues = np.ma.masked_array(self.arr[:,:,2],mask=np.logical_not(convertedROI))
            # self.label2_min.setText("min: "+str(toshowvalues.min()))
            # self.label2_max.setText("max: "+str(toshowvalues.max()))
            # self.label2_mean.setText("mean: "+str(toshowvalues.mean()))
            # # self.label2_mean.setText("mean: "+str( calculateMeanInROI(self.arr[:,:,2],convertedROI, verbose=True) ))
            # self.label2_sd.setText("sd: "+str( ndimage.standard_deviation(toshowvalues) ))
            # self.label2_sum.setText("sum: "+str( ndimage.sum(toshowvalues) ))        
            self.highlightROI(convertedROI)
        elif self.connectedThreshold:
            self.bitmapROI[self.layer] += self.tmpBitmapROI.astype(dtype=bool)
            image = self.arr[:,:,2] * self.bitmapROI[self.layer] 
            self.img1b.setImage(image, levels=(0, image.max()))
            self.p2.autoRange()
            self.img1b.updateImage()
            
        self.roisSetted = np.count_nonzero(self.rois)
        self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))

    def delROI(self):
        if self.rois[self.layer]:
            self.rois[self.layer] = None
            self.dehighlightROI()
            for thisroi in self.rois:
                if thisroi:
                    self.roisSetted -= 1
            self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))
        self.bitmapROI[self.layer,::,::] = False
        self.update()
        
    def myroi_file_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        writer = roiFileHandler(self.verbose)
        writer.dicomsPath = os.path.abspath(self.inpath)
        if not str(filename).endswith('.myroi'):
            filename = filename+".myroi"
        writer.write(filename, self.rois, self.roisSetted)


    def nrrdroi_file_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        writer = nrrdFileHandler(self.verbose)
        if not str(filename).endswith('.nrrd'):
            filename = filename+".nrrd"
        if self.manualROI:
            ROI = myroi2roi(self.rois, self.data[:,:,:,0].shape, self.verbose)
        if self.connectedThreshold:
            ROI = self.bitmapROI
        writer.write(filename, ROI)

    def updateImageBecauseOfRoi(self):
        self.updatemain()
        self.label2_roisSetted.setText("ROI setted: "+str(self.roisSetted))
        ROI = myroi2roi(self.rois, self.data[:,:,:,0].shape, self.verbose)
        colorchannel = 0
        regiontohighlight = self.dataZ[:,:,:,colorchannel]*ROI                
        referenceValue = self.dataZ[:,:,:,colorchannel].max()/regiontohighlight.max()/2.        
        self.dataZ[:,:,:,colorchannel] = self.dataZ[:,:,:,colorchannel] + regiontohighlight*referenceValue 
        
        
    def myroi_file_open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','ROI files (*.myroi)')
        if int(QtCore.QT_VERSION_STR.split('.')[0])>=5:
            filename = filename[0]
        reader = roiFileHandler()
        originalpath = reader.dicomsPath
        self.rois, self.roisSetted = reader.read(filename)
        self.updateImageBecauseOfRoi()

    def osirix_roi_file_open(self,filename=False):
        if not filename:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','ROI files (*.xml)')
            if int(QtCore.QT_VERSION_STR.split('.')[0])>=5:
                filename = filename[0]
        self.rois, self.roisSetted = read_plist_roi_file(filename)
        self.updateImageBecauseOfRoi()
        
    def slider_jump_to(self):
        self.layer = self.slider.value()-1
        self.updatemain()

    def jump_to(self, layer):
        if layer <0: layer=0
        if layer >= len(self.data[:,:,:,0]):
            print("WARNING: jump_to",layer)
            layer = len(self.data[:,:,:,0])
        self.layer = layer
        self.slider.setValue(self.layer+1)
        self.updatemain()        
        
    def histogram_matching_normalization(self):
        tmpLayer=self.layer
        tmpXview=self.xview
        tmpYview=self.yview
        self.switchToZView()
        thisNormalizer = Normalizer(self.verbose)
        self.data = self.dataZ = thisNormalizer.match_all(self.dataZ)
        if tmpXview:
            self.switchToXView()
        if tmpYview:
            self.switchToYView()
        self.layer=tmpLayer
        self.slider.setValue(self.layer+1)        
        self.updatemain()

    def normalizeToROI(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','ROI files (*.myroi)')
        if int(QtCore.QT_VERSION_STR.split('.')[0])>=5:
            filename = filename[0]        
        reader = roiFileHandler()
        roisForNorm, roisNormSetted = reader.read(filename)
        if len(roisForNorm) != len(self.dataZ[:,:,:,2]):
            print("ERROR: not all the layers have a ROI, I can't normalize.")
        convertedRoi = myroi2roi(roisForNorm, self.dataZ[:,:,:,2].shape, self.verbose)
        for thislayer in xrange(0,len(self.dataZ[:,:,:,2])):
            meaninroi = calculateMeanInROI(self.dataZ[thislayer,:,:,2], convertedRoi[thislayer],self.verbose)
            self.dataZ[thislayer] /= meaninroi
        self.allineateViews()            
        self.updatemain()
        
    def read_dicom_in_folder(self, path, useGDCM=False, useBruker=False):
        freader = FileReader(path, False, self.verbose)
        if useGDCM:
            dataRGB = freader.readUsingGDCM(False)
        elif useBruker:
            tmp = brukerReadFolder(path,True).proc_data
            dataRGB = np.zeros(tuple([tmp.shape[2]])+tmp.shape[0:2]+tuple([3]))
            for i in range(0,tmp.shape[2]):
                dataRGB[i,:,:,0] = dataRGB[i,:,:,1] = dataRGB[i,:,:,2] = tmp[:,:,i]
        else:
            try:
                dataRGB, unusedROI = freader.read(False)
            except NotImplementedError:
                dataRGB = freader.readUsingGDCM(False)                
        if freader.PatientName is not None:
            self.setWindowTitle("DICOM tool - "+str(freader.PatientName))
        self.xview=False
        self.yview=False
        self.zview=True        
        self.scaleFactor = freader.scaleFactor
        self.dataZ = dataRGB
        if self.verbose:
            print("shape:", self.dataZ.shape)
            print("shape of a color channel:", self.dataZ[:,:,:,0].shape)

        self.secondaryImage2D = np.zeros( self.dataZ[0].shape )
        self.imgScaleFactor= 1.
        self.data =  self.dataZ
        self.p1.setAspectLocked(True,self.imgScaleFactor)
        self.p2.setAspectLocked(True,self.imgScaleFactor)
        self.rois = [None]*len(self.data[:,:,:,0])
        self.slider.setMaximum(len(self.data[:,:,:,0]))
        self.layerZ=int(len(self.data[:,:,:,0])/2)
        self.layerX=int(len(self.data[0,:,0,0])/2)
        self.layerY=int(len(self.data[0,0,:,0])/2)
        self.layer = self.layerZ
        self.arr = self.dataZ[self.layerZ]
        self.slider.setValue(self.layer+1)
        self.updatemain()

        if self.verbose:
            print("data len:",len(self.data[:,:,:,0]))

        self.bitmapROI = np.full( self.dataZ[:,:,:,0].shape,False,dtype=bool)
                
    def read_roi_dicom_in_folder(self, path):
        freader = FileReader(path, False, self.verbose)
        self.ROI = freader.readROI()
        self.highlightROI(self.ROI)
        
    def select_dicom_folder(self):
        path =  QtGui.QFileDialog.getExistingDirectory(self, 'Open DICOM Directory',os.path.expanduser("~"),QtGui.QFileDialog.ShowDirsOnly)
        if self.verbose:
            print(path)
        self.read_dicom_in_folder(str(path))

    def select_dicom_folderGDCM(self):
        path =  QtGui.QFileDialog.getExistingDirectory(self, 'Open DICOM Directory',os.path.expanduser("~"),QtGui.QFileDialog.ShowDirsOnly)
        if self.verbose:
            print(path)
        self.read_dicom_in_folder(str(path),useGDCM=True)

    def select_dicom_folderBruker(self):
        path =  QtGui.QFileDialog.getExistingDirectory(self, 'Open DICOM Directory',os.path.expanduser("~"),QtGui.QFileDialog.ShowDirsOnly)
        if self.verbose:
            print(path)
        self.read_dicom_in_folder(str(path),useBruker=True)                

    def switchToXView(self):
        if self.xview:
            return
        if self.zview:
            self.layerZ = self.layer
        elif self.yview:
            self.layerY = self.layer
        self.xview=True
        self.yview=False
        self.zview=False
        self.allineateViews()        
        self.imgScaleFactor= 1./self.scaleFactor
        self.p1.setAspectLocked(True,self.imgScaleFactor)
        self.p2.setAspectLocked(True,self.imgScaleFactor)        
        self.data = self.dataswappedX
        self.rois = [None]*len(self.data[:,:,:,0])
        self.slider.setMaximum(len(self.data[:,:,:,0]))
        self.layer = self.layerX
        self.slider.setValue(self.layer+1)
        self.updatemain()

    def switchToYView(self):
        if self.yview:
            return
        if self.zview:
            self.layerZ = self.layer
        elif self.xview:
            self.layerX = self.layer        
        self.yview=True
        self.xview=False
        self.zview=False
        self.allineateViews()        
        self.imgScaleFactor= 1./self.scaleFactor
        self.p1.setAspectLocked(True,self.imgScaleFactor)
        self.p2.setAspectLocked(True,self.imgScaleFactor)        
        self.data = self.dataswappedY
        self.rois = [None]*len(self.data[:,:,:,0])
        self.slider.setMaximum(len(self.data[:,:,:,0]))
        self.layer=self.layerY
        self.slider.setValue(self.layer+1)
        self.updatemain()

    def switchToZView(self):
        if self.zview:
            return
        if self.yview:
            self.layerY = self.layer
        elif self.xview:
            self.layerX = self.layer                
        self.zview=True
        self.yview=False
        self.xview=False
        self.imgScaleFactor= 1.
        self.p1.setAspectLocked(True,self.imgScaleFactor)
        self.p2.setAspectLocked(True,self.imgScaleFactor)        
        self.data = self.dataZ
        self.rois = [None]*len(self.data[:,:,:,0])
        self.slider.setMaximum(len(self.data[:,:,:,0]))
        self.layer=self.layerZ
        self.slider.setValue(self.layer+1)
        self.updatemain()

    def dehighlightROI(self, colorchannel = 0):
        referencecolorchannel = colorchannel+1
        if referencecolorchannel>2:
            referencecolorchannel = 0
            
        self.dataZ[:,:,:,colorchannel] = self.dataZ[:,:,:,referencecolorchannel]
        self.allineateViews()
        self.updatemain()


    def allineateViews(self):
        self.dataswappedX = np.swapaxes(np.swapaxes(self.dataZ,0,1),1,2)[:,::-1,::-1,:]        
        self.dataswappedY = np.swapaxes(self.dataZ,0,2)[:,:,::-1,:]          

    def highlightROI(self, ROI, colorchannel=0):
        if ROI.ndim == 3:
            regiontohighlight = self.dataZ[:,:,:,colorchannel]*ROI
            regiontohighlightmax = regiontohighlight.max()
            referenceValue = self.dataZ[:,:,:,colorchannel].max()/ regiontohighlightmax/4.
        elif ROI.ndim == 2:
            regiontohighlight = self.dataZ[self.layer,:,:,colorchannel]*ROI
            regiontohighlightmax = regiontohighlight.max()
            referenceValue = self.dataZ[self.layer,:,:,colorchannel].max()/ regiontohighlightmax/4.
        else:
            print("ERROR: ROI.ndim",ROI.ndim)
            return
        changesign = 1
        print("referenceValue",referenceValue)
        print("regiontohighlightmax",regiontohighlightmax)
        if regiontohighlightmax < 1300:
            changesign = -2
        #referenceValue = self.dataZ[:,:,:,colorchannel].max()
        if ROI.ndim == 3:
            self.dataZ[:,:,:,colorchannel] = self.dataZ[:,:,:,colorchannel] - changesign*regiontohighlight*referenceValue
        else:
            self.dataZ[self.layer,:,:,colorchannel] = self.dataZ[self.layer,:,:,colorchannel] - changesign*regiontohighlight*referenceValue            
        self.allineateViews()        
        self.updatemain()

    def highlightnrrdROI(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','ROI files (*.nrrd)')
        if int(QtCore.QT_VERSION_STR.split('.')[0])>=5:
            filename = filename[0]
        self.read_nrrd_roi(filename)
        
    def read_nrrd_roi(self, filename):
        roiFileReader = nrrdFileHandler(self.verbose)
        self.ROI = roiFileReader.read(filename)
        self.highlightROI(self.ROI)

    def highlightDCMROI(self):
        path =  QtGui.QFileDialog.getExistingDirectory(self, 'Open DICOM Directory',os.path.expanduser("~"),QtGui.QFileDialog.ShowDirsOnly)
        if self.verbose:
            print(path)
        self.read_roi_dicom_in_folder(str(path))    

    def highlightMyROI(self, colorchannel=0):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File','ROI','MyROI files (*.myroi)')
        if int(QtCore.QT_VERSION_STR.split('.')[0])>=5:
            filename = filename[0]
        reader = roiFileHandler(self.verbose)
        myroi, roisSetted = reader.read(filename)
        self.ROI = myroi2roi(myroi, self.data[:,:,:,0].shape, self.verbose)
        self.highlightROI(self.ROI)

    def saveToImage(self, extension):
        filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save File'))        
        if not filename.endswith(extension):
            filename = filename+extension
        print(filename)
            
        if self.verbose:
            print(type(self.arr))
            print(self.arr.shape)
        image = self.arr.transpose(1,0,2)[::-1,:,:]
        sides = image.shape
        image = scipy.misc.imresize(image,size=tuple([int(sides[0]/self.imgScaleFactor),sides[1]]))
        scipy.misc.imsave(filename,image)        
        
    def saveToTIFFImage(self):
        self.saveToImage(".tiff")

    def saveToPNGImage(self):
        self.saveToImage(".png")        


    def histoOfAllLayer(self):
        print("to be done")
        # h = np.histogram(self.arr,bins='fd')
        plt.hist(self.arr.ravel(), bins='fd')
        plt.title("Histogram of all the current layer")
        plt.show()

    def about(self):
        dialogTextBrowser = AboutWindow(self)
        dialogTextBrowser.exec_()

    def CurvatureFlowImageFilter(self):
        filtered = curvatureFlowImageFilter(self.arr, self.verbose)
        self.img1b.setImage(filtered)
        self.p2.autoRange()
        self.img1b.updateImage()

    def GaussianLaplaceFilter(self):
        filtered = GaussianLaplaceFilter(self.data[:,:,:,0], 2.5, self.verbose) 
        self.img1b.setImage(filtered[self.layer])
        self.p2.autoRange()
        self.img1b.updateImage()

        print("type: ", type(filtered), "shape", filtered.shape)

    def mouseMoved(self, pos):
        # print(type(pos))
        if self.verbose:        
            print(pos)
        # # print("lastPos",pos.lastPos())
        # print("pos",pos.pos())
        # print("scenePos",pos.scenePos())        
        # print("Image position:", self.img1a.mapFromScene(pos))
        # if self.p1.sceneBoundingRect().contains(pos.pos()):
        # mousePoint = self.p1ViewBox.mapSceneToView(pos.pos())
        # print("mousePoint",mousePoint)
        mousePoint = self.p1ViewBox.mapSceneToView(pos.scenePos())
        if self.verbose:
            print("mousePoint",mousePoint)        
        # # print(self.img1a.mapFromScene(pos.pos()))
        # print(type(mousePoint.x()))
        seedX = int(mousePoint.x()+0.5)
        seedY = int(mousePoint.y()+0.5)
        if seedX <0:
            seedX = 0
        if seedY <0:
            seedY = 0 
        self.lastSeed = (seedX, seedY)        
        thisImage = self.arr[:,:,0]
        # thisImage = self.img1a.getImage()
        # # print(type(thisImage))
        # # print(thisImage.shape)
        value = thisImage[self.lastSeed]
        if self.verbose:                
            print("value",value)
        self.label_coordinates.setText("coordinates: "+str(self.lastSeed))
        self.label_intensity.setText("intensity: "+str(value))

        if self.connectedThreshold:
            self.dehighlightROI(1)
            self.callConnectedThreshold()

    def callConnectedThreshold(self):
        thisImage = self.arr[:,:,0]
        value = thisImage[self.lastSeed]        
        lowThres = value - value* self.LowThresSlider.value()*0.01
        if lowThres<0:
            lowThres = 0
        hiThres = value + value* self.HighThresSlider.value()*0.01
        if hiThres<lowThres:
            hiThres = lowThres *1.001
        if self.verbose:                    
            print("range",lowThres, hiThres)
        self.LowThresLabel.setText("value: "+str(lowThres))
        self.HighThresLabel.setText("value: "+str(hiThres))
        self.LowThresSliderLabel.setText("Lower threshold ["+str(self.LowThresSlider.value())+"%]")        
        self.HighThresSliderLabel.setText("Higher threshold ["+str(self.HighThresSlider.value())+"%]")
        if self.filterBeforeSegmentation:
            thisImage =  curvatureFlowImageFilter(thisImage,self.verbose)
        if self.verbose:                        
            print("seed:", self.lastSeed)
            print("thisImage.shape",thisImage.shape)
        self.tmpBitmapROI = connectedThreshold(thisImage, self.lastSeed, lowThres, hiThres)
        if self.tmpBitmapROI.any():
            self.highlightROI(self.tmpBitmapROI ,1)
        print("number of selected pixel:", np.count_nonzero(self.tmpBitmapROI))

    def mouseMoved2(self, pos):
        print(pos)
        mousePoint = self.p2ViewBox.mapSceneToView(pos.scenePos())
        seedX = int(mousePoint.x()+0.5)
        seedY = int(mousePoint.y()+0.5)
        thisSeed = (seedX, seedY)
        if self.secondaryImage3D:
            self.secondaryImage2D = self.secondaryImage[self.layer]
        elif np.any(self.secondaryImage2D):
            self.secondaryImage2D = self.secondaryImage2D
        value =  self.secondaryImage2D[thisSeed]
        print("value",value)
            
    def MorphologicalWatershed(self):
        thisImage = self.arr[:,:,0]        
        thisImage = self.dataZ[:,:,:,2]
        self.secondaryImage3D = True
        
        self.secondaryImage = morphologicalWatershed(thisImage,level=55,fullyConnected=False)
        self.img1b.setImage(self.secondaryImage[self.layer])
        self.p2.autoRange()
        self.img1b.updateImage()

    def WardHierarchical(self):
        thisImage = self.arr[:,:,0]
        wardHierarchical(thisImage)

    def ActivateConnectedThreshold(self):
        self.label.setText("Click on a region to select its neighborhood.")
        self.manualROI = False
        self.connectedThreshold = True
        self.filterBeforeSegmentation=False
        for aWidget in  self.leftSideTemporaryWidgets:
            aWidget.deleteLater() 

        self.LowThresSliderLabel = QtGui.QLabel("Lower threshold [%]")
        self.layout.addWidget(self.LowThresSliderLabel,7,self.LeftButtonsCol)        
        self.LowThresSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.LowThresSlider.setFixedWidth(150);
        self.LowThresSlider.setMinimum(1)
        self.LowThresSlider.setMaximum(100)
        self.LowThresSlider.setValue(10)
        self.LowThresSlider.setTickPosition(2)
        self.LowThresSlider.setTickInterval(100)
        self.LowThresSlider.setSingleStep(1)
        self.LowThresSlider.valueChanged.connect(self.callConnectedThreshold)
        self.layout.addWidget(self.LowThresSlider,9,self.LeftButtonsCol)
        self.LowThresLabel = QtGui.QLabel("value: ")
        self.layout.addWidget(self.LowThresLabel,8,self.LeftButtonsCol)                

        self.HighThresSliderLabel = QtGui.QLabel("Higher threshold [%]")
        self.layout.addWidget(self.HighThresSliderLabel,10,self.LeftButtonsCol)        
        self.HighThresSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.HighThresSlider.setFixedWidth(150);
        self.HighThresSlider.setMinimum(1)
        self.HighThresSlider.setMaximum(100)
        self.HighThresSlider.setValue(10)
        self.HighThresSlider.setTickPosition(2)
        self.HighThresSlider.setTickInterval(100)
        self.HighThresSlider.setSingleStep(1)
        self.HighThresSlider.valueChanged.connect(self.callConnectedThreshold)
        self.layout.addWidget(self.HighThresSlider,12,self.LeftButtonsCol)
        self.HighThresLabel = QtGui.QLabel("value: ")
        self.layout.addWidget(self.HighThresLabel,11,self.LeftButtonsCol)                        
        self.leftSideTemporaryWidgets.append(self.LowThresSliderLabel)
        self.leftSideTemporaryWidgets.append(self.LowThresSlider)
        self.leftSideTemporaryWidgets.append(self.LowThresLabel)
        self.leftSideTemporaryWidgets.append(self.HighThresSliderLabel)
        self.leftSideTemporaryWidgets.append(self.HighThresSlider)
        self.leftSideTemporaryWidgets.append(self.HighThresLabel)
        
    def ActivateManualRoiDesigner(self):
        self.label.setText("Click on a line segment to add a new handle. Right click on a handle to remove.")
        self.manualROI = True
        self.connectedThreshold = False
        self.filterBeforeSegmentation=False
        for aWidget in  self.leftSideTemporaryWidgets:
            aWidget.deleteLater() 

        
    def ActivateConnectedThresholdFiltered(self):
        self.ActivateConnectedThreshold()
        self.label.setText("Click on a region to select its neighborhood. Applying Curvature Flow Filter.")        
        self.filterBeforeSegmentation=True

    def entropy(self):
        image = self.arr[:,:,2]
        if len(self.ROI)!=0:
            if not np.any(self.ROI[self.layer]): return
            image = image*self.ROI[self.layer]
            # entropyImg = getEntropy(self.arr[:,:,2], ROI=self.ROI[self.layer])
            entropyImg = getEntropyCircleMask(self.arr[:,:,2], ROI=self.ROI[self.layer],circle_radius=7)            
        else:
            entropyImg = getEntropyCircleMask(self.arr[:,:,2],ROI=None,circle_radius=7)
        colimg= colorize(entropyImg*1.)
        
        self.img1b.setImage(colimg)
        self.p2.autoRange()
        self.img1b.updateImage()
        self.setlabel2values(entropyImg)
        return entropyImg
        # h = histFromArray(entropyImg)
        # outfile = ROOT.TFile("prova.root","RECREATE")
        # h.Write()
        # outfile.Close()
        

    def entropyInAllROI(self):
        oldlayer = self.layer
        if len(self.ROI)<1:
            self.highlightnrrdROI()
        # self.secondaryImage = np.zeros( tuple([len(self.data)])+self.data[0,:,:,0].shape+tuple([4]) )
        self.secondaryImage = np.zeros( tuple([len(self.data)])+self.data[0,:,:,0].shape)
        for i in range(0,len(self.data[:,:,:,0])):
            self.jump_to(i)
            self.secondaryImage[i]= self.entropy()
        self.layer=oldlayer
        self.secondaryImage3D = True
        self.colorizeSecondaryImage = True
        self.colorizeSecondaryImageWithROI = True
        self.jump_to(self.layer)


    def gradient(self):
        image = self.arr[:,:,2]
        if len(self.ROI)!=0:
            image = image*self.ROI[self.layer]
        imagemin = np.min(image[np.nonzero(image)])
        imagemax = np.max(image)
        # image = img_as_ubyte(image)
        # image = rescale(image,{-1,1})
        # image = exposure.rescale_intensity(image, in_range='uint16')
        image = rescale8bit(image)
        
        if len(self.ROI)!=0:  
            gradientImg = skim_gradient(image,skim_square(5), mask=self.ROI[self.layer])
        else:
            gradientImg = skim_gradient(image,skim_square(5))
            # gradientImg = self.getLogOfImg(gradientImg+1.)
        minval = np.min( gradientImg[np.nonzero(gradientImg)] )
        self.img1b.setImage(gradientImg*1., levels=( minval, np.max(gradientImg)))
        self.p2.autoRange()
        self.img1b.updateImage()
        self.setlabel2values(gradientImg)
        
    def setlabel2values(self, img):
        imgO = img
        if len(self.ROI)!=0:
            if np.count_nonzero(self.ROI[self.layer]) !=0:
                img = img[np.nonzero(self.ROI[self.layer])]
        
        minval = np.min(img )
        self.label2_shape.setText("shape: "+str(img.shape))
        self.label2_size.setText("size: "+str(img.size))
        self.label2_min.setText("min: "+str(minval))
        self.label2_max.setText("max: "+str( np.max(img)))
        self.label2_mean.setText("mean: "+str(img.mean()))
        self.label2_sd.setText("sd: "+str( ndimage.standard_deviation(img) ))
        self.label2_sum.setText("sum: "+str( ndimage.sum(img) ))

    def colorMainImg(self):
        col = colorize(self.arr[:,:,2])
        self.arr = col
        self.img1a.setImage(col)
        self.img1a.updateImage()

    def show8bit(self):
        image = self.arr[:,:,2]
        # print(type(image),type(image[0][0]))
        if len(self.ROI)!=0:
            if not np.any(self.ROI[self.layer]): return
            image = image*self.ROI[self.layer]
        # rImage = rescale8bit(image)
        # image = exposure.rescale_intensity(image,in_range='uint16')
        # print(type(image),type(image[0][0]))        
        # image = image.astype(np.uint16)
        # image = image/image.max()
        # rImage = img_as_ubyte(image)        
        # print(type(rImage),type(rImage[0][0]))
        rImage = rescale8bit(image)
        rImage = rImage.astype(np.float64)
        self.secondaryImage2D = rImage
        self.setlabel2values(rImage)        
        self.img1b.setImage(rImage)#, levels=(0,1))
        self.p2.autoRange()        
        self.img1b.updateImage()

    def show16bit(self):
        image = self.arr[:,:,2]
        if len(self.ROI)!=0:
            if not np.any(self.ROI[self.layer]): return
            image = image*self.ROI[self.layer]
        # rImage = rescale16bit(image)
        # rImage = exposure.rescale_intensity(image,in_range='uint16')
        # image = exposure.rescale_intensity(image,in_range='uint16')

        # rImage = img_as_uint(image)
        # print(type(rImage),type(rImage[0][0]))
        rImage = rescale16bit(image)        
        rImage = rImage.astype(np.float64)        
        self.secondaryImage2D = rImage        
        self.setlabel2values(rImage)
        self.img1b.setImage(rImage)#, levels=(0,1))
        self.p2.autoRange()        
        self.img1b.updateImage()

    # def showROI8bit(self):
    #     i
    #     oldlayer = self.layer
    #     self.secondaryImage = np .

    # def adjusteExposureMainImg(self):
    #     self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)

    def changeMainExposure(self):
        self.MainImgExposureMax = 10000 - self.ExposureSlider.value()
        if self.verbose:
            print("new max exposure:",self.MainImgExposureMax)
        self.updatemain()

    def superimposeSecondaryToPrimary(self):
        secImg = self.secondaryImage[self.layer]
        primImg = self.arr[:,:,0]
        secImg = colorize(secImg,'jet')
        primImg = colorize(primImg, 'gray')
        
        if self.verbose:
            print("secImg shape",secImg.shape)
            print("primImg shape",primImg.shape)

        primImg[secImg>0] = secImg[secImg>0]

        self.setImgToMain(primImg)

    def goToLayerWithLargerROI(self):
        self.layer = getLayerWithLargerROI(self.ROI)
        self.updatemain()

    def launchShell(self):
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            app.exit()
        
        message="""dicom_tool interactive shell.

The dicom_tool application instance is called 'instance' 
so you can access its data members via 'instance.data'.
If you loaded dicom files the content is stored in 'instance.data', 
the ROI in 'instance.ROI'. 
\n"""
        
        control = RichJupyterWidget(banner=message)
        control.kernel_manager = kernel_manager
        control.kernel_client = kernel_client
        control.exit_requested.connect(stop)
        control.show()
        
if __name__ == '__main__':
    # kernel_manager.start_kernel()
    # kernel = kernel_manager.kernel
    # kernel.gui = 'qt4'
    
    # import sys

    # app = QtGui.QApplication(sys.argv)

    # # app = guisupport.get_app_qt4()
            

    # sys.exit(app.exec_())

    app = guisupport.get_app_qt4()

    kernel_manager = QtInProcessKernelManager()
    kernel_manager.start_kernel()
    kernel = kernel_manager.kernel
    kernel.gui = 'qt'

    instance =  Window_dicom_tool()

    kernel.shell.push({'instance': instance, 'instance.show()': instance.show()})
    


    guisupport.start_event_loop_qt4(app)
