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
# header = []

os.chdir(inpath)

names = []
methods = []

names.append("AcquisitionDate")
methods.append(lambda x: x.AcquisitionDate)

names.append("AcquisitionNumber")
methods.append(lambda x: x.AcquisitionNumber)

names.append("AcquisitionTime")
methods.append(lambda x: x.AcquisitionTime)

names.append("ContentDate")
methods.append(lambda x: x.ContentDate)

names.append("ContentTime")
methods.append(lambda x: x.ContentTime)

names.append("EchoTime")
methods.append(lambda x: x.EchoTime)

names.append("FlipAngle")
methods.append(lambda x: x.FlipAngle)

names.append("MRAcquisitionType")
methods.append(lambda x: x.MRAcquisitionType)

names.append("PatientName")
methods.append(lambda x: x.PatientName)

names.append("PerformedProcedureStepStartDate")
methods.append(lambda x: x.PerformedProcedureStepStartDate)

names.append("PerformedProcedureStepStartTime")
methods.append(lambda x: x.PerformedProcedureStepStartTime)

names.append("PixelRepresentation")
methods.append(lambda x: x.PixelRepresentation)

names.append("SAR")
methods.append(lambda x: x.SAR)

names.append("SeriesDate")
methods.append(lambda x: x.SeriesDate)

names.append("SeriesDescription")
methods.append(lambda x: x.SeriesDescription)

names.append("SeriesInstanceUID")
methods.append(lambda x: x.SeriesInstanceUID)

names.append("StudyDate")
methods.append(lambda x: x.StudyDate)

names.append("StudyID")
methods.append(lambda x: x.StudyID)

names.append("StudyInstanceUID")
methods.append(lambda x: x.StudyInstanceUID)


out_file = open(outfname,"w")

out_file.write("dir, ")
for name in names:
    out_file.write(name+", ")
out_file.write("\n")


for thisdir in dirs:
    os.chdir(thisdir)
    print "working in dir: ",os.getcwd()
    
    infiles=glob.glob("*")
    
    for filen,thisfile in enumerate(infiles):
        if os.path.isdir(thisfile):
            continue
        try:
            thisdicom = dicom.read_file(thisfile)
        except:
            print thisfile," is not a DICOM"
            continue
            pass
        line = []
        line.append(thisdir)

        for method in methods:
            result="none"
            try:
                result = method(thisdicom)
            except:
                pass
            line.append(result)
        
        if line not in table:
            table.append(line)

    os.chdir("../")

if args.verbose:
    print "end loop"
    print "printing results on ",outfname
    # print header
    # for line in table:
    #     print line
        

# for element in header:
#     out_file.write(element+", ")
# out_file.write("\n")

for line in table:
    for i, element in enumerate(line):
        selement = "???"
        try:
            selement = str(element)
        except:
            print names[i], " in dir ",line[0], " is not convertible to string "
            pass
        out_file.write(selement+", ")
    out_file.write("\n")

        
out_file.close()
