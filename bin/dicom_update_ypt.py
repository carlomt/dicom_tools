#!/usr/bin/python
from __future__ import print_function
import argparse
import os
import glob
from dicom_tools.xlsReader import xlsReader
from dicom_tools.info_file_parser import info_file_parser
from tabulate import tabulate

sheets = xlsReader('responders.xls')
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
    if val == "CR 0":
        ypt = 0
    elif val == "CR 1":
        ypt = 1
    elif val == "PR DA 3 A 2":
        ypt = 2
    elif val == "PR DA 4 A 2":
        ypt = 3
    elif val == "PR DA 4 A 3":        
        ypt = 4
    elif val == "NR":
        ypt = 5

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
