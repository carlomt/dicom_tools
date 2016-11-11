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
    
outfile = ROOT.TFile(outfname,"RECREATE")
patientID= bytearray(64)
timeflag = array('i', [0])
nVoxel   = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0])
skewness = array('f', [0])
kurtosis = array('f', [0])


tree = ROOT.TTree("analisi_T2","analisi_T2")
tree.Branch("patientID",patientID,"patientID/C")
tree.Branch("timeflag",timeflag,"timeflag/I")
tree.Branch("mean",mean,"mean/F")
tree.Branch("stdDev",stdDev,"stdDev/F")
tree.Branch("skewness",skewness,"skewness/F")
tree.Branch("kurtosis",kurtosis,"kurtosis/F")
            
if args.verbose:
    print("Reading configuration file: ",inputfile)
            
with open(inputfile,'r') as fin:
    for line in fin:
        lines = line.split()
        patientID = lines[0]
        pathT2 = lines[1]
        pathROI = lines[2]
        timeflag = lines[3]

    data, ROI = read_files(pathT2, pathROI, args.verbose, True)
    his, allhistos = make_histo(data,ROI)
    
    nVoxel   = his.GetEntries()
    mean     = his.GetMean()
    stdDev   = his.GetStdDev()
    skewness = his.GetSkewness()
    kurtosis = his.GetKurtosis()

    tree.Fill()
            
outfile.Write()
outfile.Close()
