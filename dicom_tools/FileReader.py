from __future__ import print_function

import glob
import numpy as np
try:
    import dicom
except ImportError:
    import pydicom as dicom
import nrrd
import os
#from dicom_tools.roiFileHandler import roiFileHandler
from dicom_tools.nrrdFileHandler import nrrdFileHandler
import SimpleITK as sitk

# se raw=True torna un tensore con esattamente le dimensioni dei dicom, altrimenti replica le fette per riprodurre l'aspect ratio (ovvero tenere conto del fatto che i voxel sono molto piu' profondi delle dimensioni su X e Y)

class FileReader:

    def __init__(self, inpath, inpathROI=False, verbose=False):
        self.inpath = inpath
        self.inpathROI = inpathROI
        self.verbose = verbose
        self.scaleFactor = None
        if self.verbose:
            print("FileReader: init verbose\n")
        self.infiles = []
        self.infilesROI = []        
        self.data = []
        self.dataRGB = []
        self.ROI = []
        self.PatientName = None
            
    def loadDCMfiles(self):
        if self.verbose:
            print("FileReader: init verbose\n")
        inpath = self.inpath
        verbose = self.verbose

        if os.path.isdir(inpath):
            self.infiles = glob.glob(inpath+"/*.dcm")
            if len(self.infiles)==0:
                print("FileReader WARNING: there are no .dcm files in dir",inpath,"trying to open files without extension")
                allfiles = glob.glob(inpath+"/*")
                if verbose:
                    print("len(allfiles):",len(allfiles))
                for thisfile in allfiles:
                    fname = thisfile.split('/')[-1]
                    if verbose:
                        print(fname)
                    if not '.' in fname:
                        self.infiles.append(thisfile)
                if verbose:
                    print("len(self.infiles):",len(self.infiles))                        
        else:
            self.infiles = inpath

        if verbose:
            print("funciont read file V 1.1")
            print("input directory:\n",inpath)
            print(len(self.infiles)," files will be imported")



    def read(self,  raw=False):
        if self.verbose:
            print("FileReader::read\n")
        verbose = self.verbose
        inpathROI = self.inpathROI
        
        self.loadDCMfiles()
        
        dicoms = []

        for thisfile in self.infiles:
            dicoms.append(dicom.read_file(thisfile))

        dicoms.sort(key=lambda x: float(x.ImagePositionPatient[2]))

        # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
        self.ConstPixelDims = (int(dicoms[0].Rows), int(dicoms[0].Columns), len(dicoms))

        # Load spacing values (in mm)
        self.ConstPixelSpacing = (float(dicoms[0].PixelSpacing[0]), float(dicoms[0].PixelSpacing[1]), float(dicoms[0].SliceThickness))
        if verbose:
            print("n dicom files:",len(dicoms))
            print("Voxel dimensions: ", self.ConstPixelSpacing)


        # self.xsize = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
        # self.ysize = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
        # self.zsize = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])
        # if verbose:
        #     print("Image dimensions: ",xsize,ysize,zsize)

        self.scaleFactor=dicoms[0].SliceThickness/dicoms[0].PixelSpacing[0]
        if verbose:
            print("scaleFactor",self.scaleFactor)

        self.data=np.zeros(tuple([len(dicoms)])
                           +tuple([dicoms[0].pixel_array.shape[1],dicoms[0].pixel_array.shape[0]]) )
            
        self.dataRGB=np.zeros(tuple([len(dicoms)])
                              +tuple([dicoms[0].pixel_array.shape[1],dicoms[0].pixel_array.shape[0]])
                              +tuple([3]))
        if verbose:
            print("data.shape",self.data.shape)            
            print("dataRGB.shape",self.dataRGB.shape)

        if inpathROI:
            self.readROI()
        else:
            self.ROI=np.full(self.data.shape,False,dtype=bool)

            # 
        if len(self.ROI) is not len(self.data):
            print("FileReader ERROR: ROI and data have different length")
            raise ValueError('ROI and data have different length',len(self.data),len(self.ROI),
                             self.inpath, self.inpathROI)

        for i, thisdicom in enumerate(reversed(dicoms)):
            pix_arr  = thisdicom.pixel_array
            self.dataRGB[i,:,:,2] = self.dataRGB[i,:,:,0] = self.data[i] = pix_arr.T
            self.dataRGB[i,:,:,1]  = pix_arr.T - np.multiply(pix_arr.T, self.ROI[i])
        self.PatientName = dicoms[0].PatientName

        if self.verbose:
            print("FileReader::read type(self.data): ", type(self.data)," type(self.data[0,0,0]): ",type(self.data[0,0,0])," \n")            
        
        if raw:
            if self.verbose:
                print("FileReader::read returning raw\n")                
            return self.data[:,:,::-1], self.ROI[:,:,:]
        if inpathROI:
            ROI = ROI.astype(np.bool)            
        return self.dataRGB[:,:,::-1,:], self.ROI[:,:,:]
                
        # dataRGB[i*scaleFactorInt-2,:,:,1] = (dataRGB[i*scaleFactorInt-3,:,:,1] + dataRGB[i*scaleFactorInt-1,:,:,1])/2
        # dataRGB[i,:,:,2] = pix_arr.T - np.multiply(pix_arr.T,ROI[i])

        # size=[]
        # for dim in data.shape :
        #     size.append(np.linspace(0,dim-1,dim))
        
        # my_interpolating_function = interpolate.RegularGridInterpolator((size[0], size[1], size[2]), data)
        
        # for k in xrange(0,data.shape[0]*scaleFactorInt):
        #     print "fetta ",k
        #     for j in xrange(0,data.shape[1]):
        #         print "colonna ",j
        #         for i in xrange(0,data.shape[2]):
        #             dataRGB[k,i,j] = my_interpolating_function([float(k)/5,j,i])


    def readUsingGDCM(self, raw=False, sitkout=False):
        if self.verbose:
            print("FileReader::readUsingGDCM\n")
        reader = sitk.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(self.inpath)
        reader.SetFileNames(filenamesDICOM)
        imgOriginal = reader.Execute()
        if sitkout:
            return imgOriginal
        self.data = sitk.GetArrayFromImage(imgOriginal)
        self.data = self.data.swapaxes(1,2)
        self.data = self.data[::-1,:,::-1]
        if self.verbose:
            print("FileReader::readUsingGDCM type(self.data): ", type(self.data)," type(self.data[0,0,0]): ",type(self.data[0,0,0])," \n")            
        self.scaleFactor = imgOriginal.GetSpacing()[2]/imgOriginal.GetSpacing()[0]
        if raw:
            if self.verbose:
                print("FileReader::readUsingGDCM returning raw\n")            
            return self.data
        else:
            self.dataRGB=np.zeros(self.data.shape+tuple([3]))
            self.dataRGB[:,:,:,0] = self.dataRGB[:,:,:,1] = self.dataRGB[:,:,:,2] = self.data
            if self.verbose:
                print("FileReader::readUsingGDCM returning RGB\n")            
            return self.dataRGB


    def readROI(self):
        verbose = self.verbose
        inpathROI = self.inpathROI
        inpath = self.inpath
        
        self.ROI=np.full(self.data.shape,False,dtype=bool)

        if verbose:
            print("ROI requested, path: ",inpathROI)
        infilesROInrrd = glob.glob(inpathROI+"/*.nrrd")
        if verbose:
            print(len(infilesROInrrd),"nrrd files found in ROI path: ")
        if len(infilesROInrrd) ==1 :
            if verbose:
                print("nrrd ROI file: ",infilesROInrrd)
            # nrrdROItmp, nrrdROIoptions = nrrd.read(infilesROInrrd[0])
            # # print nrrdROItmp.shape
            # nrrdROI = nrrdROItmp.swapaxes(0,1).swapaxes(0,2)
            # for i, fetta in enumerate(reversed(nrrdROI)) :
            #     self.rawROI[i] = fetta
            #     self.ROI[i] = fetta
            roiFileReader = nrrdFileHandler(self.verbose)
            self.ROI = roiFileReader.read(infilesROInrrd[0])
            if verbose:
                print("FileRader.readROI non zero elements",np.count_nonzero(self.ROI))
            return self.ROI
                
        elif len(infilesROInrrd) >1:
            print ("ERROR: in the directory ",inpathROI," there is more than 1 nrrd file",infilesROInrrd)
            roiFileReader = nrrdFileHandler(self.verbose)
            return roiFileReader.read(infilesROInrrd[0])
        else:
            self.infilesROI = glob.glob(inpathROI+"/*.dcm")
            if verbose:
                print(len(self.infilesROI)," files will be imported for the ROI")
            if len(self.infilesROI) != len(self.infiles):
                print("ERROR: in the directory ",inpath," there are ",len(self.infiles)," dicom files")
                print("while in the ROI directory ",inpathROI," there are ",len(self.infilesROI)," dicom files")
            dicomsROI=[]
            for infileROI in self.infilesROI:
                dicomsROI.append(dicom.read_file(infileROI))

            for i, thisROI in enumerate(reversed(dicomsROI)):
                pix_arr = thisROI.pixel_array
                self.ROI[i] = pix_arr.T
        
        ROI = ROI.astype(np.bool)            
        return self.ROI[:,:,::-1]
