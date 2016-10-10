import ROOT
import numpy as np
# from tabulate import tabulate

def make_histo(data, mask):
    nbin = 200
    binmin=0
    binmax=1400

    # table = []
    
    nFette = len(data)
    
    his = ROOT.TH1F("histo","histo",nbin,binmin,binmax)

    hEntries = ROOT.TH1F("hEntries","Entries",nFette,-0.5,nFette+0.5)
    hMean = ROOT.TH1F("hMean","Mean",nFette,-0.5,nFette+0.5)
    hStdDev = ROOT.TH1F("hStdDev","StdDev",nFette,-0.5,nFette+0.5)
    hSkewness = ROOT.TH1F("hSkewness","Skewness",nFette,-0.5,nFette+0.5)
    hKurtosis = ROOT.TH1F("hKurtosis","Kurtosis",nFette,-0.5,nFette+0.5)
    allhistos = []
    nfetta=0
    
    for fetta,fettaROI in zip(data,mask) :
        # res = []
        thishisto = ROOT.TH1F("h"+str(nfetta),"h"+str(nfetta),nbin,binmin,binmax)
        if fettaROI.max() > 0 :
            # res.append(nfetta)
            for val, inROI in zip(np.nditer(fetta),np.nditer(fettaROI)):
                if inROI>0 :
                    his.Fill(val)
                    thishisto.Fill(val)
            hEntries.SetBinContent(nfetta,thishisto.GetEntries())
            hMean.SetBinContent(nfetta,thishisto.GetMean())
            hStdDev.SetBinContent(nfetta,thishisto.GetStdDev())
            hSkewness.SetBinContent(nfetta,thishisto.GetSkewness())
            hKurtosis.SetBinContent(nfetta,thishisto.GetKurtosis())
        nfetta+=1
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
    allhistos.append(hEntries)
    allhistos.append(hMean)
    allhistos.append(hStdDev)
    allhistos.append(hSkewness)
    allhistos.append(hKurtosis)
    return his, allhistos
