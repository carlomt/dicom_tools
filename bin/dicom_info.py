#!/usr/bin/python

import glob
import argparse
import dicom
import ROOT
import os

outfname="out.csv"

inpath="."

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("inputpath", help="path of the DICOM directory (default ./)")
parser.add_argument("-o", "--outfile", help="define output file name (default out.csv)")

args = parser.parse_args()

if args.inputpath:
    inpath = args.inputpath

if args.outfile:
    outfname = args.outfile

dirs = glob.glob(inpath+"/*/")

if args.verbose:
    print "input directory:\n",inpath
    print len(dirs)," directories"

table = []
header = []
    
for thisdir in dirs:
    print "working in dir: ",thisdir
    
    os.chdir(inpath)
    infiles=glob.glob("*")
    
    for filen,thisfile in enumerate(infiles):
        if os.path.isdir(thisfile):
            continue
        thisdicom = dicom.read_file(thisfile)
        line = []
        line.append(thisdir)
        
        if filen <=1 :
            for attr, value in thisdicom.__dict__.iteritems():
                header.append(value)

        for attr, value in thisdicom.__dict__.iteritems():
            line.append(value)

        if line not in table:
            talbe.append(line)
        os.chdir("../")

out_file = open(outfname,"w")
for element in header:
    out_file.write(element+", ")
out_file.write("\n")

for line in table:
    for element in line:
        out_file.write(element+", ")
    out_file.write("\n")

        
out_file.close()
