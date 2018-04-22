#!/usr/bin/python
from __future__ import print_function
import os
import glob
import argparse
import numpy as np
from dicom_tools.FileReader import FileReader
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.myroi2roi import myroi2roi
from dicom_tools.timeflagconverter import timeflagconverter_string2int
from dicom_tools.getLayerWithLargerROI import getLayerWithLargerROI
from scipy.stats import skew, kurtosis
from dicom_tools.getEntropy import getEntropyCircleMask
from dicom_tools.DynamicArray import DynamicArray

outfname="out.txt"

parser = argparse.ArgumentParser()
parser.add_argument("inputdirecotry", help="path of the input direcotry")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.txt)")
parser.add_argument("-jo", "--justone", help="limit the analisys to one subdirecotry")
parser.add_argument("-ex", "--exclude", help="exclude one subdirecotry from the analisys")
parser.add_argument("-n", "--norm", help="normalize to the mean defined in a myroi file",
                    action="store_true")

args = parser.parse_args()

if args.outfile:
    outfname = args.outfile
# out_file = open(outfname,"w")

inputdir = args.inputdirecotry
# print("patientID/I:timeflag:nVoxel:ypT:mean/F:stdDev:skewness:kurt",file=out_file)

vars = [("patientID",'|S10'),("timeflag",np.uint8),("nVoxel",np.uint8),("ypT",np.uint8),("ypT2",np.uint8)
        ,("mean",np.float16),("stdDev",np.float16),("skewness",np.float16),("kurt",np.float16)]

if args.verbose:
    print("Verbose dicom_make_histo_indir.py \n")

minEntropySide = 3
maxEntropySide = 21

for i in xrange(minEntropySide, maxEntropySide+1, 2):
    vars.append(("thisEntropySide"+str(i), np.uint8))
    vars.append(("meanEntropy"+str(i), np.float16))
    vars.append(("stdDevEntropy"+str(i), np.float16))
    vars.append(("minEntropy"+str(i), np.float16))
    vars.append(("maxEntropy"+str(i), np.float16))    
    vars.append(("skewnessEntropy"+str(i), np.float16))    
    vars.append(("kurtosisEntropy"+str(i), np.float16))

patientdirs= glob.glob(inputdir+"*/")

if args.justone:
    print("Looking for dir",args.justone)
if args.exclude:
    print("Excluding dir",args.exclude)

results = DynamicArray(vars,len(patientdirs)*3)
    
for patientdir in patientdirs:

    print(patientdir)
    if args.justone:
        if not args.justone in patientdir: continue

    if args.exclude:
        if args.exclude in patientdir: continue
    
    analasisysdirs=glob.glob(patientdir+"*/")
    for analasisysdir in analasisysdirs:
        print("\t",analasisysdir)

        pathT2 = analasisysdir + "T2/"
        
        nFette = 0
        if patientdir[-1]=='/':
            patID = patientdir.split('/')[-2].replace('.','')
        else:
            patID = patientdir.split('/')[-1].replace('.','')
        patientID = patID
        print("working on patient: "+patientID)
        print("in the directory: "+pathT2)
        if os.path.isdir(pathT2):
            print("T2 dir found.")
        pathROI = analasisysdir + "ROI/"
        if os.path.isdir(pathROI):
            print("ROI dir found.")

        infos = info_file_parser(analasisysdir + "info2.txt")
        timeflag = timeflagconverter_string2int(infos["time"])
        ypT = int(infos["ypT"])
        ypT2 = int(infos["ypT2"])
        
        #         # data, ROI = read_files(pathT2, pathROI, args.verbose, True)
        freader = FileReader(pathT2, pathROI, args.verbose)
        try:
            data, ROI = freader.read(raw=True)
        except NotImplementedError:
            data = freader.readUsingGDCM(raw=True)
            ROI = freader.readROI()
        except ValueError:
            print("Data not read. Check folders")
            continue
    
        roinorm=False
        
        if args.verbose:
            print("dicom file read")
            
        if args.norm:
            myroifilename = analasisysdir + "roinormmuscle.myroi"
        
            roireader = roiFileHandler(args.verbose)
            myroisnorm, roisnormSetted = roireader.read(myroifilename)
            
            roinorm = myroi2roi(myroisnorm, data.shape, args.verbose)
    
            if args.verbose:
                print("norm file read")
        if args.verbose:                
            print("data mean:",data.mean(),"min:",data.min(),"max:",data.max(),"shape:",data.shape)
            print("ROI mean:",ROI.mean(),"min:",ROI.min(),"max:",ROI.max(),"shape:",ROI.shape)

        if len(ROI) is not len(data):
            print("skipping this analysis len(data)",len(data),"len(ROI)",len(ROI))
            continue

        
        nzdata = data[ROI>0]
        nVoxel = len(nzdata.ravel())
        mean = nzdata.mean()
        stdDev = nzdata.std()
        skewness = skew(nzdata)
        kurt = kurtosis(nzdata)
        this_result = [patientID, timeflag, nVoxel, ypT, ypT2,  mean, stdDev, skewness, kurt]

        layer = getLayerWithLargerROI(ROI)
        
        for i in xrange(minEntropySide, maxEntropySide+1, 2):
            entropy = getEntropyCircleMask(data[layer],ROI[layer], circle_radius=i, verbose=args.verbose)
            nzentropy = entropy[ROI[layer]>0]
            entropymean = nzentropy.mean()
            entropyStdDev = nzentropy.std()
            entropySkewness = skew(nzentropy)
            entropyKurt = kurtosis(nzentropy)
            this_result.extend([i, entropymean, entropyStdDev, min(nzentropy), max(nzentropy), entropySkewness, entropyKurt])
        results.append(tuple(this_result))



results.savetxtROOT(outfname)

#out_file.close()
