import ROOT
import numpy as np
from dicom_tools.getEntropy import getEntropyCircleMask

def make_histo_entropy(data, ROI, suffix="", maskRadius=7, onlyOneLayer=None, verbose=False, ROInorm=False, normalize=False):

    nbin = 10000
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    
    if normalize:
        layerOfMax = np.where(data == data.max())[0][0]
        normformaxbin = calculateMeanInROI(data[layerOfMax], ROInorm[layerOfMax],verbose)
        binmax = data.max()/normformaxbin
        binmin = 0
        nbin = int(data.max()-binmin)
        bindim = (binmax-binmin)/nbin
        if verbose:
            print("make_histo_entropy: layerOfMax",layerOfMax,"data.max()",data.max(),"binmax",binmax,"nbin",nbin)
    nFette = len(data)

    if onlyOneLayer is not None:
        hEntropyis = ROOT.TH1F("hEntropyisto"+str(maskRadius)+suffix,"hEntropyisto",nbin,binmin,binmax)
        hEntropyEntries = ROOT.TH1F("hEntropyEntries"+str(maskRadius)+suffix,"Entries",nFette,-0.5,nFette+0.5)
        hEntropyMean = ROOT.TH1F("hEntropyMean"+str(maskRadius)+suffix,"Mean",nFette,-0.5,nFette+0.5)
        hEntropyMax = ROOT.TH1F("hEntropyMax"+str(maskRadius)+suffix,"Max",nFette,-0.5,nFette+0.5)
        hEntropyMin = ROOT.TH1F("hEntropyMin"+str(maskRadius)+suffix,"Min",nFette,-0.5,nFette+0.5)
        hEntropyStdDev = ROOT.TH1F("hEntropyStdDev"+str(maskRadius)+suffix,"StdDev",nFette,-0.5,nFette+0.5)
        hEntropySkewness = ROOT.TH1F("hEntropySkewness"+str(maskRadius)+suffix,"Skewness",nFette,-0.5,nFette+0.5)
        hEntropyKurtosis = ROOT.TH1F("hEntropyKurtosis"+str(maskRadius)+suffix,"Kurtosis",nFette,-0.5,nFette+0.5)
    else:
        hEntropyis = ROOT.TH1F("hEntropyisto"+"FM"+str(maskRadius)+suffix,"hEntropyisto",nbin,binmin,binmax)
        hEntropyEntries = ROOT.TH1F("hEntropyEntries"+"FM"+str(maskRadius)+suffix,"Entries",nFette,-0.5,nFette+0.5)
        hEntropyMean = ROOT.TH1F("hEntropyMean"+"FM"+str(maskRadius)+suffix,"Mean",nFette,-0.5,nFette+0.5)
        hEntropyMax = ROOT.TH1F("hEntropyMax"+"FM"+str(maskRadius)+suffix,"Max",nFette,-0.5,nFette+0.5)
        hEntropyMin = ROOT.TH1F("hEntropyMin"+"FM"+str(maskRadius)+suffix,"Min",nFette,-0.5,nFette+0.5)
        hEntropyStdDev = ROOT.TH1F("hEntropyStdDev"+"FM"+str(maskRadius)+suffix,"StdDev",nFette,-0.5,nFette+0.5)
        hEntropySkewness = ROOT.TH1F("hEntropySkewness"+"FM"+str(maskRadius)+suffix,"Skewness",nFette,-0.5,nFette+0.5)
        hEntropyKurtosis = ROOT.TH1F("hEntropyKurtosis"+"FM"+str(maskRadius)+suffix,"Kurtosis",nFette,-0.5,nFette+0.5)        
        
    allhistos = []
    histogiafatti = []


    for layer in xrange(0,nFette):
        if onlyOneLayer is not None:
            if layer is not onlyOneLayer:
                continue
        
        fetta = data[layer]
        fettaROI = ROI[layer]
        if onlyOneLayer is not None: 
            thishEntropy = ROOT.TH1F("hEntropy"+str(layer)+suffix,"hEntropy"+str(layer),nbin,binmin,binmax)
        else:
            thishEntropy = ROOT.TH1F("hEntropyFM"+str(layer)+suffix,"hEntropyFM"+str(layer),nbin,binmin,binmax)
            
        entropyImg = getEntropyCircleMask(fetta, fettaROI, maskRadius)
        nonZeroEntropy= entropyImg[np.nonzero(entropyImg)]
        if nonZeroEntropy.any():
            for val in nonZeroEntropy.ravel():
                thishEntropy.Fill(val)
                hEntropyis.Fill(val)

            hEntropyEntries.SetBinContent(layer,thishEntropy.GetEntries())
            hEntropyMean.SetBinContent(layer,thishEntropy.GetMean())
            hEntropyMax.SetBinContent(layer,thishEntropy.GetMaximum())
            hEntropyMin.SetBinContent(layer,thishEntropy.GetMinimum())            
            hEntropyStdDev.SetBinContent(layer,thishEntropy.GetStdDev())
            hEntropySkewness.SetBinContent(layer,thishEntropy.GetSkewness())
            hEntropyKurtosis.SetBinContent(layer,thishEntropy.GetKurtosis())
        allhistos.append(thishEntropy)
        
    histogiafatti.append(hEntropyEntries)
    histogiafatti.append(hEntropyMean)
    histogiafatti.append(hEntropyStdDev)
    histogiafatti.append(hEntropySkewness)
    histogiafatti.append(hEntropyKurtosis)                

    return hEntropyis, allhistos
