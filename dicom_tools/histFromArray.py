import numpy as np
import ROOT

def histFromArray(array, nbin=100, name="h", verbose=False):
    if len(array[np.nonzero(array)]) == 0: return
    minval = np.min(array[np.nonzero(array)])
    maxval = np.max(array)
    # if not nbin:
    #     nph = np.histogram(array, bins='auto')
    #     nbin = len(nph)

    # nbin = int(nbin)
    if verbose:
        print("histFromArray creating histogram",name,"with",nbin,"bin")
        
    h = ROOT.TH1F(name,name,nbin,minval*.9,maxval*1.1)
    for val in array.ravel():
        h.Fill(val)

    return h
