#!/usr/bin/python

#import sys, getopt, os
import dicom
#import dicom.contrib.pydicom_Tkinter as pydicom_Tkinter
import glob
# import msvcrt as m
import ROOT
import argparse

outfname="out.root"
inpath="."

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i","--inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")


args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

if args.inputpath:
    inpath = args.inputpath


infiles=glob.glob(inpath+"/*.dcm")

if args.verbose:
   print "input directory:\n",inpath
   print "output file name:\n",outfname

   print "input files:\n",infiles


RMs=[]

fRM = ROOT.TFile(outfname, "recreate")

for file in infiles:
    RMs.append(dicom.read_file(file))
    
for counter, RM in enumerate(RMs):
    pix_arr  = RM.pixel_array
    col = RM.Columns
    row = RM.Rows
    his = ROOT.TH2D("RM"+str(counter), "RM "+str(counter), col, 0, col, row, 0, row)
    for y in range(0,col):
        for x in range (0,row):
            his.SetBinContent(x, y, pix_arr[y,x])
    # his.Draw("colz")
    his.Write()

fRM.Write()
fRM.Close()

