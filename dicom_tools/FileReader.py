
import glob
import numpy as np
import dicom
import nrrd
import os
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
            print("Voxel dimensions: ", self.ConstPixelSpacing)


        # self.xsize = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
        # self.ysize = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
        # self.zsize = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])
        # if verbose:
        #     print("Image dimensions: ",xsize,ysize,zsize)

        self.scaleFactor=dicoms[0].SliceThickness/dicoms[0].PixelSpacing[0]
        if verbose:
            print("scaleFactor",self.scaleFactor)
    
        data=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape)
        dataRGB=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape+tuple([3]))
        if verbose:
            print("dataRGB.shape",dataRGB.shape)
        rawROI=np.full(tuple([len(dicoms)])+dicoms[0].pixel_array.shape,False,dtype=bool)
        ROI=np.full(tuple([len(dicoms)])+dicoms[0].pixel_array.shape,False,dtype=bool)

        if inpathROI:
            if verbose:
                print("ROI requested, path: ",inpathROI)
            infilesROInrrd = glob.glob(inpathROI+"/*.nrrd")
            if verbose:
                print(len(infilesROInrrd),"nrrd files found in ROI path: ")
            if len(infilesROInrrd) ==1 :
                if verbose:
                    print("nrrd ROI file: ",infilesROInrrd)
                nrrdROItmp, nrrdROIoptions = nrrd.read(infilesROInrrd[0])
                # print nrrdROItmp.shape
                nrrdROI = nrrdROItmp.swapaxes(0,1).swapaxes(0,2)
                for i, fetta in enumerate(reversed(nrrdROI)) :
                    rawROI[i] = fetta
                    ROI[i] = fetta
            elif len(infilesROInrrd) >1:
                print ("ERROR: in the directory ",inpathROI," there is more than 1 nrrd file",infilesROInrrd)
            else:
                infilesROI = glob.glob(inpathROI+"/*.dcm")
                if verbose:
                    print(len(infilesROI)," files will be imported for the ROI")
                if len(infilesROI) != len(infiles):
                    print("ERROR: in the directory ",inpath," there are ",len(infiles)," dicom files")
                    print("while in the ROI directory ",inpathROI," there are ",len(infilesROI)," dicom files")
                dicomsROI=[]
                for infileROI in infilesROI:
                    dicomsROI.append(dicom.read_file(infileROI))

                for i, thisROI in enumerate(reversed(dicomsROI)):
                    pix_arr = thisROI.pixel_array
                    ROI[i] = pix_arr.T
                    rawROI[i] = pix_arr.T
        # 
        
        for i, thisdicom in enumerate(reversed(dicoms)):
            pix_arr  = thisdicom.pixel_array
            dataRGB[i,:,:,2] = dataRGB[i,:,:,0] = data[i] = pix_arr.T
            dataRGB[i,:,:,1]  = pix_arr.T - np.multiply(pix_arr.T,ROI[i])

        if raw:
            if verbose:
                print("returning raw data")
            return data[:,:,::-1], rawROI[:,:,::-1]
    

        return dataRGB[:,:,::-1,:], ROI[:,:,::-1]
                
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
        reader = sitk.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(self.inpath)
        reader.SetFileNames(filenamesDICOM)
        imgOriginal = reader.Execute()
        if sitkout:
            return imgOriginal
        data = sitk.GetArrayFromImage(imgOriginal)
        data = data.swapaxes(1,2)
        data = data[::-1,:,::-1]
        self.scaleFactor = imgOriginal.GetSpacing()[2]/imgOriginal.GetSpacing()[0]
        if raw:
            return data
        else:
            dataRGB=np.zeros(data.shape+tuple([3]))
            dataRGB[:,:,:,0] = dataRGB[:,:,:,1] = dataRGB[:,:,:,2] = data
            return dataRGB
