#!/usr/bin/python
from __future__ import print_function
import argparse
import os
import glob
from dicom_tools.xlsReader import xlsReader
from dicom_tools.info_file_parser import info_file_parser
from tabulate import tabulate

infile = 'responders.xls'

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-i", "--inputfile", help="path of the xls input filey (default ./responders.xls)")

args = parser.parse_args()

if args.inputfile:
    infile = args.inputfile

if args.verbose:
    print("Reading file: ",infile)
sheets = xlsReader(infile)
sheet = sheets[0]    

for irow, row in enumerate(sheet[2:]):
    if len(row) < 3: continue
    cognome = row[1]
    nome = row[2]
    val = row[3]
    try:
        anoname = cognome[0:2]+nome[0:2]
    except TypeError:
        print("line: ",irow," cognome: ",cognome," nome: ",nome)
        continue
        
    ypt = -1
    # if val == "CR 0":
    if "cr 0" in val.lower() or "cr0" in val.lower():
        ypt = 0
    # elif val == "CR 1":
    elif "cr 1" in val.lower():
        ypt = 1        
    # elif val == "PR DA 3 A 2":
    elif "pr da 3 a 2" in val.lower():
        ypt = 2
    # elif val == "PR DA 4 A 2":
    elif "pr da 4 a 2" in val.lower():
        ypt = 3
    # elif val == "PR DA 4 A 3":
    elif "pr da 4 a 3" in val.lower():
        ypt = 4
    # elif val == "NR":
    elif "nr" in val.lower():
        ypt = 5
    else:
        print("WARNING line: ",irow," cognome: ",cognome," nome: ",nome," identifier: ",anoname, "cold D: \"",val,"\" not identified, setting ypt2 to -1")
    print(anoname,ypt)

    patientdir = "/data/dicoms/retti_test_anon/"+anoname+"/"
    analasisysdirs=glob.glob(patientdir+"*/")
    for analasisysdir in analasisysdirs:
        if os.path.isdir(analasisysdir):
            print(analasisysdir, " dir found.")
            infos = info_file_parser(analasisysdir + "info.txt")
            out_file = open(analasisysdir +"info2.txt","w")
            for key, value in infos.iteritems():
                out_file.write(key+":\t"+value+"\n")
            
            out_file.write("ypT2:\t"+str(ypt)+"\n")                
            out_file.close()
        else:
            print(analasisysdir, " dir NOT found.")                
