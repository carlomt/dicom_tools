#!/usr/bin/python
from __future__ import print_function

import glob
import argparse
import numpy as np
try:
    import dicom
except ImportError:
    import pydicom as dicom

import ROOT

outfname="out.root"

inpath="."

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")

args = parser.parse_args()

if args.inputpath:
    inpath = args.inputpath

if args.outfile:
    outfname = args.outfile

infiles=glob.glob(inpath+"/*.dcm")

if args.verbose:
    print "input directory:\n",inpath
    print len(infiles)," files will be imported"

dicoms=[]

for thisfile in infiles:
    dicoms.append(dicom.read_file(thisfile))


# data=np.zeros(tuple([len(dicoms)])+dicoms[0].pixel_array.shape)

# for i, thisdicom in enumerate(dicoms):
#     pix_arr  = thisdicom.pixel_array
#     # np.swapaxes(pix_arr,0,1)
#     data[i] = pix_arr[::-1]

outfile = ROOT.TFile(outfname, "recreate")

hmin = -1000-0.5
hmax = 5000+0.5
nbin = int(hmax-hmin)
if args.verbose:
    print "hmin",hmin,"hmax",hmax,"nbin",nbin
his = ROOT.TH1D("HU-Melanix","HU-Melanix",nbin,hmin,hmax)

for thisdicom in dicoms:
    pix_arr  = thisdicom.pixel_array
    for pix_vec in pix_arr:
        for pix in pix_vec:
            # if args.verbose:
            #     print "filling", pix
            his.Fill(pix)

his.Print()            
# cc = ROOT.TCanvas("cc","cc",800,600)
# his.Draw()            

his.Write()
outfile.Write()
outfile.Close()
