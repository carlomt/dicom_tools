import ROOT
import numpy as np
from dicom_tools.hist_match import match_all
# from tabulate import tabulate

def make_histo_ofallpixels(data, suffix="", verbose=False, normalize=False):
    nbin = 1000
    if normalize:
        datan = match_all(data)
    else:
        datan = data
    
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    nFette = len(data)

    allhistos = []
    
    for layer in xrange(0,nFette):
        fetta = data[layer]
        
        thishisto = ROOT.TH1F("h"+str(layer)+suffix,"h"+str(layer),nbin,binmin,binmax)

        for val in fetta.ravel():
            thishisto.Fill(val)
        allhistos.append(thishisto)

    return allhistos
