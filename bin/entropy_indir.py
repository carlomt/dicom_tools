#!/usr/bin/python
from __future__ import print_function
import os
import glob
import argparse
import numpy as np
import sys
from dicom_tools.getEntropy import make_histo_entropy
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.timeflagconverter import timeflagconverter_string2int
from dicom_tools.FileReader import FileReader
from dicom_tools.getEntropy import getEntropy
import math
import ROOT
from array import array

outfname="out.root"

parser = argparse.ArgumentParser()
parser.add_argument("inputdirecotry", help="path of the input direcotry")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-jo", "--justone", help="limit the analisys to one subdirecotry")

args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

out_file = open(outfname,"w")
    
inputdir = args.inputdirecotry

if args.verbose:
    print("Verbose\n")

patientdirs= glob.glob(inputdir+"*/")

if args.justone:
    print("Looking for dir",args.justone)


outfile = ROOT.TFile(outfname,"RECREATE")
patientID= bytearray(64)
timeflag = array('i', [0])
ypT      = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0]) 

tree = ROOT.TTree("analisi_T2","analisi_T2")
tree.Branch("patientID",patientID,"patientID/C")
tree.Branch("timeflag",timeflag,"timeflag/I")
tree.Branch("ypT",ypT,"ypT/I")
tree.Branch("mean",mean,"mean/F")
tree.Branch("stdDev",stdDev,"stdDev/F")

for patientdir in patientdirs:

    print(patientdir)
    if args.justone:
        if not args.justone in patientdir: continue
    if "DIIV" in patientdir: continue
    
    analasisysdirs=glob.glob(patientdir+"*/")
    for analasisysdir in analasisysdirs:
        print("\t",analasisysdir)

        pathT2 = analasisysdir + "T2/"
        
        if patientdir[-1]=='/':
            patID = patientdir.split('/')[-2].replace('.','')
        else:
            patID = patientdir.split('/')[-1].replace('.','')

        print("working on patient: "+patID)
        print("in the directory: "+pathT2)
        if not os.path.isdir(pathT2):
            continue
        else:
            print("T2 dir found.")
            
        pathROI = analasisysdir + "ROI/"
        if not os.path.isdir(pathROI):
            continue
        else:
            print("ROI dir found.")

        infos = info_file_parser(analasisysdir + "info.txt")
        
        freader = FileReader(pathT2, pathROI, args.verbose)
        try:
            data, ROI = freader.read(raw=True)
        except NotImplementedError:
            data = freader.readUsingGDCM(raw=True)
            ROI = freader.readROI()
        if len(ROI) is not len(data):
            print("ERROR len(ROI) is not len(data)",len(ROI), len(data))
            continue
        patientsuffix = patID + infos["time"]


        for i in range(0,len(data)):
            entropy = getEntropy(data[i],ROI[i])

            nonZeroEntropy= entropy[np.nonzero(entropy)]
            cmean= np.mean(nonZeroEntropy)
            std= np.std(nonZeroEntropy)
            # if not math.isnan(cmean):
            timeflag[0] = timeflagconverter_string2int(infos["time"])
            ypT[0] = int(infos["ypT"])
            patientID[:63] = patID
            mean[0] = cmean
            stdDev[0] = std
            
            tree.Fill()

tree.Write()
outfile.Close()
