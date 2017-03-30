#!/usr/bin/python
import glob
import argparse
from dicom_tools.anonymize import anonymize
from dicom_tools.ifNeededMkdir import ifNeededMkdir
from dicom_tools.newNameFromMetadata import newNameFromMetadata
import dicom, os, shutil

usage = """
Usage:
anonymize_all.py filelist path/to/outputdirecotry

Note: Use at your own risk. Does not fully de-identify the DICOM data as per
the DICOM standard, e.g in Annex E of PS3.15-2011.
"""

if __name__ == "__main__":
    #     import sys
    #     if len(sys.argv) != 3:
    #         print(usage)
    #         sys.exit()
    #     arg1, arg2 = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="inputfile")
    parser.add_argument("outpath", help="path of the output directory (default ../anonymized/)")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args = parser.parse_args()
    inputfile = args.inputfile
    outpath = args.outpath
    verbose = args.verbose

    print("Reading configuration file: ",inputfile)

    with open(inputfile,'r') as fin:
        for linenumber, line in enumerate(fin):
            if line[0] == '#':
                continue
            lines = line.split()
            if len(lines) == 0:
                continue
            if lines[0][0] == '#':
                continue
            if len(lines) !=6:
                print("ERROR line "+str(linenumber)+ " length is not 6, check it!")
                for wordnum, word in enumerate(lines):
                    print(wordnum, word)
            patientID = lines[0]
            print("working on patient: "+patientID)
            pathT2 = lines[1]
            print("in the directory: "+pathT2)
            pathROI = lines[2]
            timeflag = int(lines[3])
            ypT = lines[4]
            roinorm = lines[5]

            newname = newNameFromMetadata(pathT2)
            timestring=""
            if timeflag == 0:
                timestring = "pre"
            elif timeflag==1:
                timestring = "int"
            elif timeflag == 2:
                timestring = "post"
            else:
                print("ERROR","timestring not recognized:",timestring,"line:",linenumber)
            
            newdir = outpath+"/"+newname+"/"+timestring+"/"
            anonymize(pathT2,newdir+"T2/",newname)

            if len(glob.glob(pathROI+"/*.dicom")) >1 :
                if verbose:
                    print("anonynizing",pathROI,"into:",newdir+"/ROI/")
                anonymize(pathROI,newdir+"/ROI/",newname)
            else:
                files = glob.glob(pathROI+"/*.nrrd")
                for ifile, thisfile in enumerate(files):
                    ifNeededMkdir(newdir+"/ROI/")
                    if verbose:
                        print("copying",thisfile,newdir+"/ROI/roi"+str(ifile)+".nrrd")
                    shutil.copyfile(thisfile,newdir+"/ROI/roi"+str(ifile)+".nrrd")

            if verbose:
                print("copying",roinorm,newdir+"roinormmuscle.myroi")
            shutil.copyfile(roinorm,newdir+"roinormmuscle.myroi")

            infofile = open(newdir+"info.txt",'a')
            infofile.write("name: \t"+newname)
            infofile.write("time: \t"+timestring)
            infofile.write("ypT:  \t"+ypT)



