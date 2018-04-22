#!/usr/bin/python
from __future__ import print_function
import os
import glob
import argparse
import numpy as np
import sys
from dicom_tools.make_histo import make_histo
# from dicom_tools.read_files import read_files
from dicom_tools.FileReader import FileReader
import ROOT
from array import array
from dicom_tools.myroi2roi import myroi2roi
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.timeflagconverter import timeflagconverter_string2int
# from dicom_tools.getEntropy import getEntropy
# from dicom_tools.getEntropy import getEntropyCircleMask
from dicom_tools.getLayerWithLargerROI import getLayerWithLargerROI
from dicom_tools.make_histo_entropy import make_histo_entropy
from dicom_tools.getEntropy import getEntropyCircleMask
from dicom_tools.intensity_cut import intensity_cut
from dicom_tools.gaussianlaplace import GaussianLaplaceFilter
from scipy.stats import skew
from scipy.stats import kurtosis as sc_kurt

outfname="out.root"

parser = argparse.ArgumentParser()
parser.add_argument("inputdirecotry", help="path of the input direcotry")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
parser.add_argument("-o", "--outfile", help="define output file name (default out.root)")
parser.add_argument("-jo", "--justone", help="limit the analisys to one subdirecotry")
parser.add_argument("-ex", "--exclude", help="exclude one subdirecotry from the analisys")
parser.add_argument("-n", "--norm", help="normalize to the mean defined in a myroi file",
                    action="store_true")
parser.add_argument("-ic", "--icut", help="cut intensity > Imax*icut",default=0,type=float)
parser.add_argument("-f", "--filter", help="apply gaussian laplace filter sigma=2.5pixels",
                    action="store_true")
parser.add_argument("-s", "--sigma", help="sigma of image filter",default=2.5,type=float)
parser.add_argument("-sc", "--scala", help="normalize a 0,1",
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
ypT2      = array('i', [0])
mean     = array('f', [0])
stdDev   = array('f', [0])
skewness = array('f', [0])
kurtosis = array('f', [0])

minEntropySide = 3
maxEntropySide = 21

thisEntropySide   = {}
meanEntropy       = {}
stdDevEntropy     = {}
maxEntropy        = {}
minEntropy        = {}
skewnessEntropy = {}
kurtosisEntropy = {}
thisEntropySideFM   = {}
meanEntropyFM       = {}
stdDevEntropyFM     = {}
maxEntropyFM        = {}
minEntropyFM        = {}
skewnessEntropyFM = {}
kurtosisEntropyFM = {}
hEntropies = {}

for i in xrange(minEntropySide, maxEntropySide+1, 2):
    thisEntropySide[i]   = array('i', [0])
    meanEntropy[i]       = array('f', [0])
    stdDevEntropy[i]     = array('f', [0])
    maxEntropy[i]        = array('f', [0])
    minEntropy[i]        = array('f', [0])
    skewnessEntropy[i]        = array('f', [0])
    kurtosisEntropy[i]        = array('f', [0])
    thisEntropySideFM[i]   = array('i', [0])
    meanEntropyFM[i]       = array('f', [0])
    stdDevEntropyFM[i]     = array('f', [0])
    maxEntropyFM[i]        = array('f', [0])
    minEntropyFM[i]        = array('f', [0])
    skewnessEntropyFM[i]        = array('f', [0])
    kurtosisEntropyFM[i]        = array('f', [0])


nmax = 100
nFette   = array('i', [0])

nVoxelPF   = array('i', nmax*[0])
meanPF     = array('f', nmax*[0])
stdDevPF   = array('f', nmax*[0])
skewnessPF = array('f', nmax*[0])
kurtosisPF = array('f', nmax*[0])

#CV AR
fractalPF = array('f', nmax*[0])
fractalCPF = array('f', nmax*[0])
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
tree.Branch("ypT2",ypT2,"ypT2/I")
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
    tree.Branch("thisEntropySideFM" +str(i), thisEntropySideFM[i],  "thisEntropySideFM" +str(i)+"/I" )
    tree.Branch("meanEntropyFM"     +str(i), meanEntropyFM[i],      "meanEntropyFM"     +str(i)+"/F" )
    tree.Branch("stdDevEntropyFM"   +str(i), stdDevEntropyFM[i],    "stdDevEntropyFM"   +str(i)+"/F" )
    tree.Branch("maxEntropyFM"      +str(i), maxEntropyFM[i],       "maxEntropyFM"      +str(i)+"/F" )
    tree.Branch("minEntropyFM"      +str(i), minEntropyFM[i],       "minEntropyFM"      +str(i)+"/F" )    
    

tree.Branch("nFette",nFette,"nFette/I")

tree.Branch("nVoxelPF",nVoxelPF,"nVoxelPF[nFette]/I")
tree.Branch("meanPF",meanPF,"meanPF[nFette]/F")
tree.Branch("stdDevPF",stdDevPF,"stdDevPF[nFette]/F")
tree.Branch("skewnessPF",skewnessPF,"skewnessPF[nFette]/F")
tree.Branch("kurtosisPF",kurtosisPF,"kurtosisPF[nFette]/F")

#CV AR
tree.Branch("fractalPF",fractalPF,"fractalPF[nFette]/F")
tree.Branch("fractalCPF",fractalCPF,"fractalCPF[nFette]/F")

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
if args.exclude:
    print("Excluding dir",args.exclude)

for patientdir in patientdirs:

    print(patientdir)
    if args.justone:
        if not args.justone in patientdir: continue

    if args.exclude:
        if args.exclude in patientdir: continue

    for i in xrange(minEntropySide, maxEntropySide+1, 2):
        hEntropies[i] = ROOT.TH1F("hEntropies"+str(i)+patientdir,"Entropies"+str(i)+patientdir,100,-0.5,5.5)
        
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

        infos = info_file_parser(analasisysdir + "info2.txt")
        timeflag[0] = timeflagconverter_string2int(infos["time"])
        ypT[0] = int(infos["ypT"])
        ypT2[0] = int(infos["ypT2"])        
        
        #         # data, ROI = read_files(pathT2, pathROI, args.verbose, True)
        freader = FileReader(pathT2, pathROI, args.verbose)
        try:
            data, ROI = freader.read(raw=True)
        except NotImplementedError:
            # data = freader.readUsingGDCM(raw=True)
            dataTMP = freader.readUsingGDCM(raw=False)
            data = dataTMP[:,:,:,0]
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
        
        if args.icut:
            print("appliyng an intensity cut",str(args.icut))
            data = intensity_cut(data, ROI, args.icut, args.verbose)

        if args.filter:
            print("applying a Gaussian Laplace filter with a sigma of:",args.sigma)
            data = GaussianLaplaceFilter(data, args.sigma, args.verbose)
            
            
        patientsuffix = patID + infos["time"]
        his, allhistos, histogiafatti, histogclm  = make_histo(data,ROI,patientsuffix,args.verbose,roinorm,args.norm,args.scala)
    
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
                #CV AR
                fettaMax=nFette[0]
                scale=0
                for n in range(0,nlayer):
                    if n<(firstL) or n>(firstL+fettaMax-1):
                        continue
                    if 'hfra' in thishisto.GetName() or 'hCfra' in thishisto.GetName():
                        if thishisto.GetBinContent(n)==0:
                            fettaMax = fettaMax + 1
                            scale = scale + 1
                            continue
                        if 'hfra' in thishisto.GetName() : fractalPF[n-firstL-scale] = thishisto.GetBinContent(n)
                        if 'hCfra' in thishisto.GetName() : fractalCPF[n-firstL-scale] = thishisto.GetBinContent(n)
        if args.verbose:
            print(patientID, nFette[0])

        # layerMaxROI = getLayerWithLargerROI(ROI, args.verbose)            
        # for i in xrange(minEntropySide, maxEntropySide+1, 2):            
        #     hisEntropy, allHisEntropy = make_histo_entropy(data, ROI, patientsuffix, i, None, args.verbose, roinorm, args.norm)
        #     thisEntropySide[i][0]  = i
        #     meanEntropy[i][0]      = hisEntropy.GetMean()
        #     stdDevEntropy[i][0]    = hisEntropy.GetStdDev()
        #     maxEntropy[i][0]       = hisEntropy.GetMaximum()
        #     minEntropy[i][0]       = hisEntropy.GetMinimum()
        #     skewnessEntropy[i][0]       = hisEntropy.GetSkewness()
        #     kurtosisEntropy[i][0]       = hisEntropy.GetKurtosis()

        #     hisEntropy, allHisEntropy = make_histo_entropy(data, ROI, patientsuffix, i, layerMaxROI, args.verbose, roinorm, args.norm)
        #     thisEntropySideFM[i][0]  = i
        #     meanEntropyFM[i][0]      = hisEntropy.GetMean()
        #     stdDevEntropyFM[i][0]    = hisEntropy.GetStdDev()
        #     maxEntropyFM[i][0]       = hisEntropy.GetMaximum()
        #     minEntropyFM[i][0]       = hisEntropy.GetMinimum()
        #     skewnessEntropyFM[i][0]       = hisEntropy.GetSkewness()
        #     kurtosisEntropyFM[i][0]       = hisEntropy.GetKurtosis()            
            
            
        for layer in xrange(0, len(data)):
            if args.verbose:
                print("working on entropies from",minEntropySide,"to",maxEntropySide, "layer", layer)
            for i in xrange(minEntropySide, maxEntropySide+1, 2):
                entropyImg = getEntropyCircleMask(data[layer], ROI[layer], i)                
                nonZeroEntropy= entropyImg[np.nonzero( ROI[layer] )]
                for val in nonZeroEntropy:
                    hEntropies[i].Fill(val)
                outfile.cd()
                hEntropies[i].Write()
                if args.verbose:
                    print("hEntropies["+str(i)+"].Write()")
                thisEntropySide[i]  = i                
                if nonZeroEntropy.any():
                    meanEntropy[i][0]      = np.mean(nonZeroEntropy)
                    stdDevEntropy[i][0]    = np.std(nonZeroEntropy)
                    maxEntropy[i][0]       = np.max(nonZeroEntropy)
                    minEntropy[i][0]       = np.min(nonZeroEntropy[np.nonzero(nonZeroEntropy)])
                    skewnessEntropy[i][0]  = skew(nonZeroEntropy)
                    kurtosisEntropy[i][0]  = sc_kurt(nonZeroEntropy)                   
                    if args.verbose:
                        print("entropy results:",np.mean(nonZeroEntropy),np.std(nonZeroEntropy),np.max(nonZeroEntropy),np.min(nonZeroEntropy))
                        print("data stored:",meanEntropy[i][0],stdDevEntropy[i][0],maxEntropy[i][0],minEntropy[i][0])
                else:
                    meanEntropyFM[i][0]      = -1
                    stdDevEntropyFM[i][0]    = -1
                    maxEntropyFM[i][0]       = -1
                    minEntropyFM[i][0]       = -1
                    skewnessEntropy[i][0]  = -1                    
                    kurtosisEntropy[i][0]  = -1
            
        layerMaxROI = getLayerWithLargerROI(ROI, args.verbose)
        if args.verbose:
            print("working on entropies from",minEntropySide,"to",maxEntropySide)
        for i in xrange(minEntropySide, maxEntropySide+1, 2):
            entropyImg = getEntropyCircleMask(data[layerMaxROI], ROI[layerMaxROI], i)                        
            nonZeroEntropy= entropyImg[np.nonzero( ROI[layerMaxROI] )]
            thisEntropySide[i]  = i                
            if nonZeroEntropy.any():
                meanEntropyFM[i][0]      = np.mean(nonZeroEntropy)
                stdDevEntropyFM[i][0]    = np.std(nonZeroEntropy)
                maxEntropyFM[i][0]       = np.max(nonZeroEntropy)
                minEntropyFM[i][0]       = np.min(nonZeroEntropy[np.nonzero(nonZeroEntropy)])
                skewnessEntropyFM[i][0]  = skew(nonZeroEntropy)
                kurtosisEntropyFM[i][0]  = sc_kurt(nonZeroEntropy)                                   
                if args.verbose:
                    print("entropy results:",np.mean(nonZeroEntropy),np.std(nonZeroEntropy),np.max(nonZeroEntropy),np.min(nonZeroEntropy))
                    print("data stored:",meanEntropyFM[i][0],stdDevEntropyFM[i][0],maxEntropyFM[i][0],minEntropyFM[i][0])
            else:
                meanEntropyFM[i][0]      = -1
                stdDevEntropyFM[i][0]    = -1
                maxEntropyFM[i][0]       = -1
                minEntropyFM[i][0]       = -1
                skewnessEntropyFM[i][0]  = -1                    
                kurtosisEntropyFM[i][0]  = -1                
            

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
            
                    
            
        if args.verbose:
            print("Filling the TTree")
        tree.Fill()

if args.verbose:
    print("Writing the TTree")                
tree.Write()            
# outfile.Write()
outfile.Close()
