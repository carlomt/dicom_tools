#!/usr/bin/python

import glob
import argparse
import numpy as np
import dicom
import sys
from dicom_tools.make_histo import make_histo
from dicom_tools.read_files import read_files
import ROOT
from array import array

outfname="out.root"

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="input configuration file \n")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")


args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

inputfile = args.inputfile
    
outfile = ROOT.TFile(outfname,"RECREATE")
patientID= bytearray(64)
timeflag = array('i', [0])
nVoxel   = array('i', [0])
ypT      = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0])
skewness = array('f', [0])
kurtosis = array('f', [0])


tree = ROOT.TTree("analisi_T2","analisi_T2")
tree.Branch("patientID",patientID,"patientID/C")
tree.Branch("timeflag",timeflag,"timeflag/I")
tree.Branch("nVoxel",nVoxel,"nVoxel/I")
tree.Branch("ypT",ypT,"ypT/I")
tree.Branch("mean",mean,"mean/F")
tree.Branch("stdDev",stdDev,"stdDev/F")
tree.Branch("skewness",skewness,"skewness/F")
tree.Branch("kurtosis",kurtosis,"kurtosis/F")
            
#if args.verbose:
print("Reading configuration file: ",inputfile)
            
with open(inputfile,'r') as fin:
    for line in fin:
        lines = line.split()
        if args.verbose:
            print(lines)
        patientID[:63] = lines[0]
        print("working on patient: "+patientID)
        pathT2 = lines[1]
        print("in the directory: "+pathT2)
        pathROI = lines[2]
        timeflag[0] = int(lines[3])
        ypT[0] = int(lines[4])

        data, ROI = read_files(pathT2, pathROI, args.verbose, True)
        his, allhistos = make_histo(data,ROI,lines[0])
    
        nVoxel[0]   = int(his.GetEntries())
        mean[0]     = his.GetMean()
        stdDev[0]   = his.GetStdDev()
        skewness[0] = his.GetSkewness()
        kurtosis[0] = his.GetKurtosis()
        if args.verbose:
            print(patientID, timeflag[0], nVoxel[0], ypT[0], mean[0], stdDev[0], skewness[0], kurtosis[0])
        tree.Fill()
tree.Write()            
# outfile.Write()
outfile.Close()
