#!/usr/bin/python
from __future__ import print_function
import os
import glob
import argparse
import numpy as np
import dicom
import sys
from dicom_tools.make_histo import make_histo
# from dicom_tools.read_files import read_files
from dicom_tools.FileReader import FileReader
import ROOT
from array import array
from dicom_tools.myroi2roi import myroi2roi
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.timeflagconverter import timeflagconverter_string2int
from dicom_tools.getEntropy import getEntropy
from dicom_tools.getLayerWithLargerROI import getLayerWithLargerROI

outfname="out.root"

parser = argparse.ArgumentParser()
parser.add_argument("inputdirecotry", help="path of the input direcotry")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-jo", "--justone", help="limit the analisys to one subdirecotry")
parser.add_argument("-n", "--norm", help="normalize to the mean defined in a myroi file",
                    action="store_true")

args = parser.parse_args()

if args.outfile:
    outfname = args.outfile

inputdir = args.inputdirecotry

if args.verbose:
    print("Verbose dicom_make_histo_indir.py \n")

    
outfile = ROOT.TFile(outfname,"RECREATE")
patientID= bytearray(64)
timeflag = array('i', [0])
nVoxel   = array('i', [0])
ypT      = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0])
skewness = array('f', [0])
kurtosis = array('f', [0])

minEntropySide = 3
maxEntropySide = 13

thisEntropySide   = {}
meanEntropy       = {}
stdDevEntropy     = {}
maxEntropy        = {}
minEntropy        = {}

for i in xrange(minEntropySide, maxEntropySide+1, 2):
    thisEntropySide[i]   = array('i', [0])
    meanEntropy[i]       = array('f', [0])
    stdDevEntropy[i]     = array('f', [0])
    maxEntropy[i]        = array('f', [0])
    minEntropy[i]        = array('f', [0])

# thisEntropySide3   = array('i', [0])
# meanEntropy3       = array('f', [0])
# stdDevEntropy3     = array('f', [0])
# maxEntropy3        = array('f', [0])
# minEntropy3        = array('f', [0])

# thisEntropySide5   = array('i', [0])
# meanEntropy5       = array('f', [0])
# stdDevEntropy5     = array('f', [0])
# maxEntropy5        = array('f', [0])
# minEntropy5        = array('f', [0])

# thisEntropySide7   = array('i', [0])
# meanEntropy7       = array('f', [0])
# stdDevEntropy7     = array('f', [0])
# maxEntropy7        = array('f', [0])
# minEntropy7        = array('f', [0])

# thisEntropySide9   = array('i', [0])
# meanEntropy9       = array('f', [0])
# stdDevEntropy9     = array('f', [0])
# maxEntropy9        = array('f', [0])
# minEntropy9        = array('f', [0])

# thisEntropySide11   = array('i', [0])
# meanEntropy11       = array('f', [0])
# stdDevEntropy11     = array('f', [0])
# maxEntropy11        = array('f', [0])
# minEntropy11        = array('f', [0])

# thisEntropySide13   = array('i', [0])
# meanEntropy13       = array('f', [0])
# stdDevEntropy13     = array('f', [0])
# maxEntropy13        = array('f', [0])
# minEntropy13        = array('f', [0])

nmax = 100
nFette   = array('i', [0])

nVoxelPF   = array('i', nmax*[0])
meanPF     = array('f', nmax*[0])
stdDevPF   = array('f', nmax*[0])
skewnessPF = array('f', nmax*[0])
kurtosisPF = array('f', nmax*[0])

#CV
dissHPF = array('f', nmax*[0])
corrHPF = array('f', nmax*[0])
enerHPF = array('f', nmax*[0])
contHPF = array('f', nmax*[0])
homoHPF = array('f', nmax*[0])
dissVPF = array('f', nmax*[0])
corrVPF = array('f', nmax*[0])
enerVPF = array('f', nmax*[0])
contVPF = array('f', nmax*[0])
homoVPF = array('f', nmax*[0])
dissPQPF = array('f', nmax*[0])
corrPQPF = array('f', nmax*[0])
enerPQPF = array('f', nmax*[0])
contPQPF = array('f', nmax*[0])
homoPQPF = array('f', nmax*[0])
dissMQPF = array('f', nmax*[0])
corrMQPF = array('f', nmax*[0])
enerMQPF = array('f', nmax*[0])
contMQPF = array('f', nmax*[0])
homoMQPF = array('f', nmax*[0])

tree = ROOT.TTree("analisi_T2","analisi_T2")
tree.Branch("patientID",patientID,"patientID/C")
tree.Branch("timeflag",timeflag,"timeflag/I")
tree.Branch("nVoxel",nVoxel,"nVoxel/I")
tree.Branch("ypT",ypT,"ypT/I")
tree.Branch("mean",mean,"mean/F")
tree.Branch("stdDev",stdDev,"stdDev/F")
tree.Branch("skewness",skewness,"skewness/F")
tree.Branch("kurtosis",kurtosis,"kurtosis/F")

for i in xrange(minEntropySide, maxEntropySide+1, 2):
    if args.verbose:
        print("creating branch for entropy with side",i)
    tree.Branch("thisEntropySide" +str(i), thisEntropySide[i],  "thisEntropySide" +str(i)+"/I" )
    tree.Branch("meanEntropy"     +str(i), meanEntropy[i],      "meanEntropy"     +str(i)+"/F" )
    tree.Branch("stdDevEntropy"   +str(i), stdDevEntropy[i],    "stdDevEntropy"   +str(i)+"/F" )
    tree.Branch("maxEntropy"      +str(i), maxEntropy[i],       "maxEntropy"      +str(i)+"/F" )
    tree.Branch("minEntropy"      +str(i), minEntropy[i],       "minEntropy"      +str(i)+"/F" )
#     tree.Branch("thisEntropySide" +thisEntropyName[i].title(), thisEntropySide[i],
#                 "thisEntropySide" +thisEntropyName[i].title() +"/I" )
#     tree.Branch("meanEntropy"     +thisEntropyName[i].title(), meanEntropy[i],
#                 "meanEntropy"     +thisEntropyName[i].title() +"/F" )
#     tree.Branch("stdDevEntropy"   +thisEntropyName[i].title(), stdDevEntropy[i],
#                 "stdDevEntropy"   +thisEntropyName[i].title() +"/F" )
#     tree.Branch("maxEntropy"      +thisEntropyName[i].title(), maxEntropy[i],
#                 "maxEntropy"      +thisEntropyName[i].title() +"/F" )
#     tree.Branch("minEntropy"      +thisEntropyName[i].title(), minEntropy[i],
#                 "minEntropy"      +thisEntropyName[i].title() +"/F" )

# tree.Branch("thisEntropySide3", thisEntropySide3,  "thisEntropySide3/I")
# tree.Branch("meanEntropy3",     meanEntropy3,      "meanEntropy3/F")
# tree.Branch("stdDevEntropy3",   stdDevEntropy3,    "stdDevEntropy3/F")
# tree.Branch("maxEntropy3",      maxEntropy3,       "maxEntropy3/F")
# tree.Branch("minEntropy3",      minEntropy3,       "minEntropy3/F")

# tree.Branch("thisEntropySide5", thisEntropySide5,  "thisEntropySide5/I")
# tree.Branch("meanEntropy5",     meanEntropy5,      "meanEntropy5/F")
# tree.Branch("stdDevEntropy5",   stdDevEntropy5,    "stdDevEntropy5/F")
# tree.Branch("maxEntropy5",      maxEntropy5,       "maxEntropy5/F")
# tree.Branch("minEntropy5",      minEntropy5,       "minEntropy5/F")

# tree.Branch("thisEntropySide7", thisEntropySide7,  "thisEntropySide7/I")
# tree.Branch("meanEntropy7",     meanEntropy7,      "meanEntropy7/F")
# tree.Branch("stdDevEntropy7",   stdDevEntropy7,    "stdDevEntropy7/F")
# tree.Branch("maxEntropy7",      maxEntropy7,       "maxEntropy7/F")
# tree.Branch("minEntropy7",      minEntropy7,       "minEntropy7/F")

# tree.Branch("thisEntropySide9", thisEntropySide9,  "thisEntropySide9/I")
# tree.Branch("meanEntropy9",     meanEntropy9,      "meanEntropy9/F")
# tree.Branch("stdDevEntropy9",   stdDevEntropy9,    "stdDevEntropy9/F")
# tree.Branch("maxEntropy9",      maxEntropy9,       "maxEntropy9/F")
# tree.Branch("minEntropy9",      minEntropy9,       "minEntropy9/F")

# tree.Branch("thisEntropySide11", thisEntropySide11,  "thisEntropySide11/I")
# tree.Branch("meanEntropy11",     meanEntropy11,      "meanEntropy11/F")
# tree.Branch("stdDevEntropy11",   stdDevEntropy11,    "stdDevEntropy11/F")
# tree.Branch("maxEntropy11",      maxEntropy11,       "maxEntropy11/F")
# tree.Branch("minEntropy11",      minEntropy11,       "minEntropy11/F")

# tree.Branch("thisEntropySide13", thisEntropySide13,  "thisEntropySide13/I")
# tree.Branch("meanEntropy13",     meanEntropy13,      "meanEntropy13/F")
# tree.Branch("stdDevEntropy13",   stdDevEntropy13,    "stdDevEntropy13/F")
# tree.Branch("maxEntropy13",      maxEntropy13,       "maxEntropy13/F")
# tree.Branch("minEntropy13",      minEntropy13,       "minEntropy13/F")

    

tree.Branch("nFette",nFette,"nFette/I")

tree.Branch("nVoxelPF",nVoxelPF,"nVoxelPF[nFette]/I")
tree.Branch("meanPF",meanPF,"meanPF[nFette]/F")
tree.Branch("stdDevPF",stdDevPF,"stdDevPF[nFette]/F")
tree.Branch("skewnessPF",skewnessPF,"skewnessPF[nFette]/F")
tree.Branch("kurtosisPF",kurtosisPF,"kurtosisPF[nFette]/F")

#CV
tree.Branch("dissHPF",dissHPF,"dissHPF[nFette]/F")
tree.Branch("corrHPF",corrHPF,"corrHPF[nFette]/F")
tree.Branch("enerHPF",enerHPF,"enerHPF[nFette]/F")
tree.Branch("contHPF",contHPF,"contHPF[nFette]/F")
tree.Branch("homoHPF",homoHPF,"homoHPF[nFette]/F")
tree.Branch("dissVPF",dissVPF,"dissVPF[nFette]/F")
tree.Branch("corrVPF",corrVPF,"corrVPF[nFette]/F")
tree.Branch("enerVPF",enerVPF,"enerVPF[nFette]/F")
tree.Branch("contVPF",contVPF,"contVPF[nFette]/F")
tree.Branch("homoVPF",homoVPF,"homoVPF[nFette]/F")
tree.Branch("dissPQPF",dissPQPF,"dissPQPF[nFette]/F")
tree.Branch("corrPQPF",corrPQPF,"corrPQPF[nFette]/F")
tree.Branch("enerPQPF",enerPQPF,"enerPQPF[nFette]/F")
tree.Branch("contPQPF",contPQPF,"contPQPF[nFette]/F")
tree.Branch("homoPQPF",homoPQPF,"homoPQPF[nFette]/F")
tree.Branch("dissMQPF",dissMQPF,"dissMQPF[nFette]/F")
tree.Branch("corrMQPF",corrMQPF,"corrMQPF[nFette]/F")
tree.Branch("enerMQPF",enerMQPF,"enerMQPF[nFette]/F")
tree.Branch("contMQPF",contMQPF,"contMQPF[nFette]/F")
tree.Branch("homoMQPF",homoMQPF,"homoMQPF[nFette]/F")

patientdirs= glob.glob(inputdir+"*/")

if args.justone:
    print("Looking for dir",args.justone)

for patientdir in patientdirs:

    print(patientdir)
    if args.justone:
        if not args.justone in patientdir: continue
    
    analasisysdirs=glob.glob(patientdir+"*/")
    for analasisysdir in analasisysdirs:
        print("\t",analasisysdir)

        pathT2 = analasisysdir + "T2/"
        
        nFette[0] = 0
        if patientdir[-1]=='/':
            patID = patientdir.split('/')[-2].replace('.','')
        else:
            patID = patientdir.split('/')[-1].replace('.','')
        patientID[:63] = patID
        print("working on patient: "+patientID)
        print("in the directory: "+pathT2)
        if os.path.isdir(pathT2):
            print("T2 dir found.")
        pathROI = analasisysdir + "ROI/"
        if os.path.isdir(pathROI):
            print("ROI dir found.")

        infos = info_file_parser(analasisysdir + "info.txt")
        timeflag[0] = timeflagconverter_string2int(infos["time"])
        ypT[0] = int(infos["ypT"])
        
        #         # data, ROI = read_files(pathT2, pathROI, args.verbose, True)
        freader = FileReader(pathT2, pathROI, args.verbose)
        try:
            data, ROI = freader.read(raw=True)
        except NotImplementedError:
            data = freader.readUsingGDCM(raw=True)
            ROI = freader.readROI()
        except ValueError:
            continue
    
        roinorm=False
        
        if args.verbose:
            print("dicom file read")
            
        if args.norm:
            myroifilename = analasisysdir + "roinormmuscle.myroi"
        
            roireader = roiFileHandler(args.verbose)
            myroisnorm, roisnormSetted = roireader.read(myroifilename)
            
            roinorm = myroi2roi(myroisnorm, data.shape, args.verbose)
    
            if args.verbose:
                print("norm file read")
        if args.verbose:                
            print("data mean:",data.mean(),"min:",data.min(),"max:",data.max(),"shape:",data.shape)
            print("ROI mean:",ROI.mean(),"min:",ROI.min(),"max:",ROI.max(),"shape:",ROI.shape)

        if len(ROI) is not len(data):
            print("skipping this analysis len(data)",len(data),"len(ROI)",len(ROI))
            continue
        
        patientsuffix = patID + infos["time"]
        his, allhistos, histogiafatti, histogclm  = make_histo(data,ROI,patientsuffix,args.verbose,roinorm,args.norm)
    
        nVoxel[0]   = int(his.GetEntries())
        mean[0]     = his.GetMean()
        stdDev[0]   = his.GetStdDev()
        skewness[0] = his.GetSkewness()
        kurtosis[0] = his.GetKurtosis()
        if args.verbose:
            print(patientID, timeflag[0], nVoxel[0], ypT[0], mean[0], stdDev[0], skewness[0], kurtosis[0])
        his.Write()
        nlayer=0 #CV
        firstL=0 #CV
        count=0 #CV 
        for thishisto in allhistos:
            nlayer=nlayer+1
            if thishisto.GetEntries() >0:
                if count==0:
                   firstL=nlayer-1
                   count=1
                nVoxelPF[nFette[0]]   = int(thishisto.GetEntries())
                meanPF[nFette[0]]     = thishisto.GetMean()
                stdDevPF[nFette[0]]   = thishisto.GetStdDev()  
                skewnessPF[nFette[0]] = thishisto.GetSkewness()
                kurtosisPF[nFette[0]] = thishisto.GetKurtosis()
                
                nFette[0] +=1
                thishisto.Write()
        for thishisto in histogiafatti:
                thishisto.Write()
        if args.verbose:
            print(patientID, nFette[0])

        #CV gclm parameters
        for k in range(0,len(histogclm)):
            thishisto = histogclm[k]
            thishisto.Write()
            for n in range(0,nlayer):
                if n<(firstL) or n>(firstL+nFette[0]-1):
                    continue
                if 'dissH' in thishisto.GetName(): dissHPF[n-firstL] = thishisto.GetBinContent(n)
                if 'corrH' in thishisto.GetName(): corrHPF[n-firstL] = thishisto.GetBinContent(n)
                if 'enerH' in thishisto.GetName(): enerHPF[n-firstL] = thishisto.GetBinContent(n)
                if 'contH' in thishisto.GetName(): contHPF[n-firstL] = thishisto.GetBinContent(n)
                if 'homoH' in thishisto.GetName(): homoHPF[n-firstL] = thishisto.GetBinContent(n)

                if 'dissV' in thishisto.GetName(): dissVPF[n-firstL] = thishisto.GetBinContent(n)
                if 'corrV' in thishisto.GetName(): corrVPF[n-firstL] = thishisto.GetBinContent(n)
                if 'enerV' in thishisto.GetName(): enerVPF[n-firstL] = thishisto.GetBinContent(n)
                if 'contV' in thishisto.GetName(): contVPF[n-firstL] = thishisto.GetBinContent(n)
                if 'homoV' in thishisto.GetName(): homoVPF[n-firstL] = thishisto.GetBinContent(n)

                if 'dissPQ' in thishisto.GetName(): dissPQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'corrPQ' in thishisto.GetName(): corrPQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'enerPQ' in thishisto.GetName(): enerPQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'contPQ' in thishisto.GetName(): contPQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'homoPQ' in thishisto.GetName(): homoPQPF[n-firstL] = thishisto.GetBinContent(n)

                if 'dissMQ' in thishisto.GetName(): dissMQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'corrMQ' in thishisto.GetName(): corrMQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'enerMQ' in thishisto.GetName(): enerMQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'contMQ' in thishisto.GetName(): contMQPF[n-firstL] = thishisto.GetBinContent(n)
                if 'homoMQ' in thishisto.GetName(): homoMQPF[n-firstL] = thishisto.GetBinContent(n)
            
        # for layer in xrange(0, len(data)):
        layerMaxROI = getLayerWithLargerROI(ROI, args.verbose)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 3)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy3      = np.mean(nonZeroEntropy)
        # stdDevEntropy3    = np.std(nonZeroEntropy)
        # maxEntropy3       = np.max(nonZeroEntropy)
        # minEntropy3       = np.min(nonZeroEntropy)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 5)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy5      = np.mean(nonZeroEntropy)
        # stdDevEntropy5    = np.std(nonZeroEntropy)
        # maxEntropy5       = np.max(nonZeroEntropy)
        # minEntropy5       = np.min(nonZeroEntropy)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 7)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy7      = np.mean(nonZeroEntropy)
        # stdDevEntropy7    = np.std(nonZeroEntropy)
        # maxEntropy7       = np.max(nonZeroEntropy)
        # minEntropy7       = np.min(nonZeroEntropy)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 9)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy9      = np.mean(nonZeroEntropy)
        # stdDevEntropy9    = np.std(nonZeroEntropy)
        # maxEntropy9       = np.max(nonZeroEntropy)
        # minEntropy9       = np.min(nonZeroEntropy)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 11)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy11      = np.mean(nonZeroEntropy)
        # stdDevEntropy11    = np.std(nonZeroEntropy)
        # maxEntropy11       = np.max(nonZeroEntropy)
        # minEntropy11       = np.min(nonZeroEntropy)

        # entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], 13)            
        # nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        # meanEntropy13      = np.mean(nonZeroEntropy)
        # stdDevEntropy13    = np.std(nonZeroEntropy)
        # maxEntropy13       = np.max(nonZeroEntropy)
        # minEntropy13       = np.min(nonZeroEntropy)        
        
        if args.verbose:
            print("working on entropies from",minEntropySide,"to",maxEntropySide)
        for i in xrange(minEntropySide, maxEntropySide+1, 2):
            # entropyImg = getEntropy(data[layer], ROI[layer], i)
            entropyImg = getEntropy(data[layerMaxROI], ROI[layerMaxROI], i)            
            nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
            # thisEntropySide[i]  = i                
            if nonZeroEntropy.any():
                meanEntropy[i][0]      = np.mean(nonZeroEntropy)
                stdDevEntropy[i][0]    = np.std(nonZeroEntropy)
                maxEntropy[i][0]       = np.max(nonZeroEntropy)
                minEntropy[i][0]       = np.min(nonZeroEntropy)
                if args.verbose:
                    print("entropy results:",np.mean(nonZeroEntropy),np.std(nonZeroEntropy),np.max(nonZeroEntropy),np.min(nonZeroEntropy))
                    print("data stored:",meanEntropy[i][0],stdDevEntropy[i][0],maxEntropy[i][0],minEntropy[i][0])
            else:
                meanEntropy[i][0]      = -1
                stdDevEntropy[i][0]    = -1
                maxEntropy[i][0]       = -1
                minEntropy[i][0]       = -1
                    
                    
            
        if args.verbose:
            print("Filling the TTree")
        tree.Fill()

if args.verbose:
    print("Writing the TTree")                
tree.Write()            
# outfile.Write()
outfile.Close()
