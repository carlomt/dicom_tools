import ROOT
import numpy as np
# from tabulate import tabulate
from dicom_tools.calculateMeanInROI import calculateMeanInROI

def make_histo(data, mask, suffix="", verbose=False, ROInorm=False, normalize=False):
    nbin = 10000
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    # meannorm = 1
    # if ROInorm:
    #     binmin=0.
    #     binmax=1.
    # table = []
    if normalize:
        dataN = data*mask
        layerOfMax = np.where(dataN == dataN.max())[0][0]
        normformaxbin = calculateMeanInROI(data[layerOfMax], ROInorm[layerOfMax],verbose)
        # if normformaxbin >0:
        binmax = dataN.max()/normformaxbin
        # else:
        #     print("make_histo WARNING: patient",suffix,"has at least a layer without normalization ROI")
        #     binmax = int(data.max())
        # layerOfMin = np.where(data == data.min())[0][0]
        # try:
        #     binmin = int(data.min()/calculateMeanInROI(data[layerOfMin], ROInorm[layerOfMin]))
        # except ValueError:
        #     binmin = 0
        binmin = 0
        nbin = int(dataN.max()-binmin)
        bindim = (binmax-binmin)/nbin
        nbin += int(nbin*0.3)
        binmax *= 1.3
        if verbose:
            print("make_histo: layerOfMax",layerOfMax,"dataN.max()",dataN.max(),"binmax",binmax,"nbin",nbin)

    #     perCalcolareMedia = ROInorm*data
    #     meannorm = perCalcolareMedia.mean()
    # binmin=data.min() *0.8
    # binmax=data.max() *1.2
    if verbose:
        print("make_histo: bin min:",binmin,"bin max:",binmax,"nbin:",nbin)        
        
    nFette = len(data)
    
    his = ROOT.TH1F("histo"+suffix,"histo",nbin,binmin,binmax)

    hEntries = ROOT.TH1F("hEntries"+suffix,"Entries",nFette,-0.5,nFette+0.5)
    hMean = ROOT.TH1F("hMean"+suffix,"Mean",nFette,-0.5,nFette+0.5)
    hStdDev = ROOT.TH1F("hStdDev"+suffix,"StdDev",nFette,-0.5,nFette+0.5)
    hSkewness = ROOT.TH1F("hSkewness"+suffix,"Skewness",nFette,-0.5,nFette+0.5)
    hKurtosis = ROOT.TH1F("hKurtosis"+suffix,"Kurtosis",nFette,-0.5,nFette+0.5)
    allhistos = []
    histogiafatti = []
    # nfetta=0
    
    # for fetta,fettaROI in zip(data,mask) :
    for layer in xrange(0,nFette):
        fetta = data[layer]
        fettaROI = mask[layer]
        # res = []
        thishisto = ROOT.TH1F("h"+str(layer)+suffix,"h"+str(layer),nbin,binmin,binmax)
        meaninroi = 1
        if fettaROI.any():
            if normalize:
                meaninroi = calculateMeanInROI(fetta, ROInorm[layer],verbose)
                if verbose:
                    print("make_histo: layer",layer,"meaninroi",meaninroi)
            for val, inROI in zip(np.nditer(fetta),np.nditer(fettaROI)):
                if inROI>0 :
                    if normalize:
                            # val = val/meaninroi*0.01 #per avere valori dello stesso ordine di grandezza dell'originale
                        val = val/meaninroi#*meannorm #per avere valori dello stesso ordine di grandezza dell'originale
                        # his.Fill(val)
                        # thishisto.Fill(val)
                        # else:
                        #     print("make_histo WARNING: patient",suffix,"layer",layer,"is in ROI but doesn't have a normalization")
                    # else:
                    if val >  binmax:
                        print("make_histo: Warning in layer",layer,"there is a value in overflow:",val,"normalization",meaninroi)
                    his.Fill(val)
                    thishisto.Fill(val)

                    
            hEntries.SetBinContent(layer,thishisto.GetEntries())
            hMean.SetBinContent(layer,thishisto.GetMean())
            hStdDev.SetBinContent(layer,thishisto.GetStdDev())
            hSkewness.SetBinContent(layer,thishisto.GetSkewness())
            hKurtosis.SetBinContent(layer,thishisto.GetKurtosis())
        if verbose:
            print layer, thishisto.GetEntries()
        # layer+=1
        allhistos.append(thishisto)

    #         norm = fetta.mean()
    #         for riga, rigaROI in zip(fetta,fettaROI) :
    #             for val, inROI in zip(riga, rigaROI) :
    #                 if inROI>0 :
    #                     his.Fill(val/norm)
    #                     # print(val)




    # for val, inROI in zip(np.nditer(data),np.nditer(mask)):
    #     if inROI>0 :
    #         his.Fill(val)
            #            print val

    histogiafatti.append(hEntries)
    histogiafatti.append(hMean)
    histogiafatti.append(hStdDev)
    histogiafatti.append(hSkewness)
    histogiafatti.append(hKurtosis)
    return his, allhistos, histogiafatti
