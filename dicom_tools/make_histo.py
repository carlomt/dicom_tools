import ROOT
import numpy as np
# from tabulate import tabulate

def make_histo(data, mask, suffix="", verbose=False, ROInorm=False, normalize=False):
    nbin = 200
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    # if ROInorm:
    #     binmin=0.
    #     binmax=1.
    # table = []
    
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
        meaninroi = 0
        if fettaROI.max() > 0 :
            # res.append(layer)
            for val, inROI in zip(np.nditer(fetta),np.nditer(fettaROI)):
                if inROI>0 :
                    if normalize:
                        if ROInorm.any():
                            normarea = ROInorm[layer]*data[layer]
                            meaninroi = normarea.mean()
                            val = val/meaninroi*0.01 #per avere valori dello stesso ordine di grandezza dell'originale
                    his.Fill(val)
                    thishisto.Fill(val)

            if verbose:
                print("make_histo: layer",layer,"meaninroi",meaninroi)
                    
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
