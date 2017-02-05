#!/usr/bin/python


import glob
import argparse
import numpy as np
import dicom
import sys
from dicom_tools.make_histo import make_histo
from dicom_tools.make_histo_ofallpixels import make_histo_ofallpixels
from dicom_tools.read_files import read_files
import ROOT

outfname="out.root"
inpath="./"

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i", "--inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-f", "--filterROI", help="filter the image with a ROI (path)")
parser.add_argument("-n", "--normalize", help="normalize the intensities using Histogram Matching",
                    action="store_true")

group = parser.add_mutually_exclusive_group()
group.add_argument("-y", "--yview", help="swap axes",
                    action="store_true")
group.add_argument("-x", "--xview", help="swap axes",
                    action="store_true")


args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

if args.inputpath:
    inpath = args.inputpath


# infiles = glob.glob(inpath+"/*.dcm")

# if args.verbose:
#     print("input directory:\n",inpath)
#     print("output file name:\n",outfname)

#     print(len(infiles)," files will be imported")

# dicoms=[]

# for thisfile in infiles:
#     dicoms.append(dicom.read_file(thisfile))


# data=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape)
# ROI=np.full(tuple([len(dicoms)])+dicoms[0].pixel_array.shape,False,dtype=bool)

# if args.filterROI:
#     inpathROI = args.filterROI
#     if args.verbose:
#         print("ROI requested, path: ",inpathROI)
#     infilesROI = glob.glob(inpathROI+"/*.dcm")
#     if args.verbose:
#         print(len(infilesROI)," files will be imported for the ROI")
#     if len(infilesROI) != len(infiles):
#         print("ERROR: in the directory ",inpath," there are ",len(infiles)," dicom files")
#         print("while in the ROI directory ",inpathROI," there are ",len(infilesROI)," dicom files")
#     dicomsROI=[]
#     for infileROI in infilesROI:
#         dicomsROI.append(dicom.read_file(infileROI))

#     for i, thisROI in enumerate(dicomsROI):
#         pix_arr = thisROI.pixel_array
#         ROI[i] = pix_arr.T

# for i, thisdicom in enumerate(dicoms):
#     pix_arr  = thisdicom.pixel_array
#     data[i] = pix_arr.T

data, ROI = read_files(inpath,args.filterROI, args.verbose, True)
    
outfile= ROOT.TFile(outfname,"RECREATE")

if args.filterROI:
    his, allhistos = make_histo(data,ROI)
    his.Write()

else:
    allhistos = make_histo_ofallpixels(data,"",args.verbose,args.normalize)
    

for thishisto in allhistos:
    thishisto.Write()

# histograms = []
# for i, fetta, fettaROI in enumerate(zip(data,ROI)):
#     if fettaROI.max() > 0 :
#         histogram = make_histo(fetta, fettaROI)
#         histogram.SetName("h"+str(i))
#         histogram.SetTitle("h"+str(i))
#         histogram.Write()


outfile.Write()
outfile.Close()
    
# canvas = ROOT.TCanvas("c","c",800,600)
# his.Draw()


