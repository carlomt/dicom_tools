#!/usr/bin/python

import glob
import argparse
import numpy as np
import sys
from dicom_tools.make_histo import make_histo
# from dicom_tools.read_files import read_files
from dicom_tools.FileReader import FileReader
import ROOT
from array import array
from dicom_tools.roiFileHandler import roiFileHandler
from dicom_tools.myroi2roi import myroi2roi

outfname="out.root"

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="input configuration file \n")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-n", "--norm", help="normalize to the mean defined in a myroi file",
                    action="store_true")
parser.add_argument("-ic", "--icut", help="cut intensity > Imax*icut",default=0,type=float)
parser.add_argument("-f", "--filter", help="apply gaussian laplace filter sigma=2.5pixels",
                    action="store_true")

args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

inputfile = args.inputfile

if args.verbose:
    print("Verbose\n")

outfile = ROOT.TFile(outfname,"RECREATE")
patientID= bytearray(64)
timeflag = array('i', [0])
nVoxel   = array('i', [0])
ypT      = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0])
skewness = array('f', [0])
kurtosis = array('f', [0])

nmax = 100
nFette   = array('i', [0])

nVoxelPF   = array('i', nmax*[0])
meanPF     = array('f', nmax*[0])
stdDevPF   = array('f', nmax*[0])
skewnessPF = array('f', nmax*[0])
kurtosisPF = array('f', nmax*[0])

tree = ROOT.TTree("analisi_T2","analisi_T2")
tree.Branch("patientID",patientID,"patientID/C")
tree.Branch("timeflag",timeflag,"timeflag/I")
tree.Branch("nVoxel",nVoxel,"nVoxel/I")
tree.Branch("ypT",ypT,"ypT/I")
tree.Branch("mean",mean,"mean/F")
tree.Branch("stdDev",stdDev,"stdDev/F")
tree.Branch("skewness",skewness,"skewness/F")
tree.Branch("kurtosis",kurtosis,"kurtosis/F")

tree.Branch("nFette",nFette,"nFette/I")

tree.Branch("nVoxelPF",nVoxelPF,"nVoxelPF[nFette]/I")
tree.Branch("meanPF",meanPF,"meanPF[nFette]/F")
tree.Branch("stdDevPF",stdDevPF,"stdDevPF[nFette]/F")
tree.Branch("skewnessPF",skewnessPF,"skewnessPF[nFette]/F")
tree.Branch("kurtosisPF",kurtosisPF,"kurtosisPF[nFette]/F")

#if args.verbose:
print("Reading configuration file: ",inputfile)
            
with open(inputfile,'r') as fin:
    for linenumber, line in enumerate(fin):
        nFette[0] = 0
        if line[0] == '#':
            continue
        lines = line.split()
        if len(lines) == 0:
            continue
        if args.norm:
            if len(lines) !=6:
                print("ERROR line "+str(linenumber)+ " length is not 6 (because you requested normalization), check it!")
                for wordnum, word in enumerate(lines):
                    print(wordnum, word)
        else:
            if len(lines) !=5:
                print("ERROR line "+str(linenumber)+ " length is not 5, check it!")
                for wordnum, word in enumerate(lines):
                    print(wordnum, word)
        if args.verbose:
            print(lines)
        if lines[0][0] == '#':
            continue
        patientID[:63] = lines[0]
        print("working on patient: "+patientID)
        pathT2 = lines[1]
        print("in the directory: "+pathT2)
        pathROI = lines[2]
        timeflag[0] = int(lines[3])
        ypT[0] = int(lines[4])

        # data, ROI = read_files(pathT2, pathROI, args.verbose, True)
        freader = FileReader(pathT2, pathROI, args.verbose)
        data, ROI = freader.read(True)

        roinorm=False
        
        if args.verbose:
            print("dicom file read")
            
        if args.norm:
            myroifilename = lines[5]
        
            roireader = roiFileHandler(args.verbose)
            myroisnorm, roisnormSetted = roireader.read(myroifilename)
            
            roinorm = myroi2roi(myroisnorm, data.shape, args.verbose)
    
            if args.verbose:
                print("norm file read")
        if args.verbose:                
            print("data mean:",data.mean(),"min:",data.min(),"max:",data.max(),"shape:",data.shape)
            print("ROI mean:",ROI.mean(),"min:",ROI.min(),"max:",ROI.max(),"shape:",ROI.shape)                        
        patientsuffix=lines[0]+str(timeflag[0])
        if timeflag[0] != 0 and timeflag[0] != 1 and timeflag[0] != 2:
            print("ERROR: timeflag (0 for pre, 1 for int and 2 for post) of patient "+lines[0]+ "is: "+timeflag[0])
            raise NameError('OutOfRange')
        his, allhistos, histogiafatti,histogclm = make_histo(data,ROI,patientsuffix,args.verbose,roinorm,args.norm,args.icut,args.filter)
    
        nVoxel[0]   = int(his.GetEntries())
        mean[0]     = his.GetMean()
        stdDev[0]   = his.GetStdDev()
        skewness[0] = his.GetSkewness()
        kurtosis[0] = his.GetKurtosis()
        if args.verbose:
            print(patientID, timeflag[0], nVoxel[0], ypT[0], mean[0], stdDev[0], skewness[0], kurtosis[0])
        his.Write()
        for thishisto in allhistos:
            if thishisto.GetEntries() >0:
                nVoxelPF[nFette[0]]   = int(thishisto.GetEntries())
                meanPF[nFette[0]]     = thishisto.GetMean()
                stdDevPF[nFette[0]]   = thishisto.GetStdDev()  
                skewnessPF[nFette[0]] = thishisto.GetSkewness()
                kurtosisPF[nFette[0]] = thishisto.GetKurtosis()
                
                nFette[0] +=1
                thishisto.Write()
        for thishisto in histogiafatti:
                thishisto.Write()
        if args.verbose:
            print(patientID, nFette[0])
        tree.Fill()
                
tree.Write()            
# outfile.Write()
outfile.Close()
