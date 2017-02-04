import ROOT
import numpy as np
# from tabulate import tabulate

def make_histo_ofallpixels(data, suffix="", verbose=False, ROInorm=False, normalize=False):
    nbin = 1000
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    nFette = len(data)

    allhistos = []
    
    for layer in xrange(0,nFette):
        fetta = data[layer]
        
        thishisto = ROOT.TH1F("h"+str(layer)+suffix,"h"+str(layer),nbin,binmin,binmax)

        for val in np.nditer(fetta):
            thishisto.Fill(val)
        allhistos.append(thishisto)

    return allhistos
