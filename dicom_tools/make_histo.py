from __future__ import print_function
import ROOT
import numpy as np
from skimage.feature import greycomatrix, greycoprops #CV
from skimage import exposure #CV
from dicom_tools.rescale import rescale8bit #CV
# from tabulate import tabulate
from dicom_tools.calculateMeanInROI import calculateMeanInROI
from dicom_tools.fractal import fractal #AR
from scipy import ndimage #AR
from dicom_tools.gaussianlaplace import GaussianLaplaceFilter #AR

def make_histo(data, mask, suffix="", verbose=False, ROInorm=False, normalize=False, scala = False, filtered=False):
    nbin = 10000
    binmin=data.min() *0.8
    binmax=data.max() *1.2
    #CV resize bin if Intensity cut is required
    #if(ICut>0): binmax = binmax*ICut
    #CV AR filter
    if scala:
       binmin = -5
       binmax = 5

    # if filtered:
    #    binmin=-binmax/10.
    #    binmax=binmax/10.

    # meannorm = 1
    # if ROInorm:
    #     binmin=0.
    #     binmax=1.
    # table = []
    if normalize:
        layerOfMax = np.where(data == data.max())[0][0]
        normformaxbin = calculateMeanInROI(data[layerOfMax], ROInorm[layerOfMax],verbose)
        # if normformaxbin >0:
        binmax = data.max()/normformaxbin
        # else:
        #     print("make_histo WARNING: patient",suffix,"has at least a layer without normalization ROI")
        #     binmax = int(data.max())
        # layerOfMin = np.where(data == data.min())[0][0]
        # try:
        #     binmin = int(data.min()/calculateMeanInROI(data[layerOfMin], ROInorm[layerOfMin]))
        # except ValueError:
        #     binmin = 0
        binmin = 0
        nbin = int(data.max()-binmin)
        bindim = (binmax-binmin)/nbin
        # nbin += int(nbin*0.3)
        # binmax *= 1.3
        if verbose:
            print("make_histo: layerOfMax",layerOfMax,"data.max()",data.max(),"binmax",binmax,"nbin",nbin)

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
    hfra = ROOT.TH1F("hfra"+suffix,"fra",nFette,-0.5,nFette+0.5) #AR
    hCfra = ROOT.TH1F("hCfra"+suffix,"hCfra",nFette,-0.5,nFette+0.5) #AR
    #CV II order histo
    # Horizontal
    hdissH = ROOT.TH1F("hdissH"+suffix,"Horizontal dissimilarity",nFette,-0.5,nFette+0.5)
    hcorrH = ROOT.TH1F("hcorrH"+suffix,"Horizontal correlation",nFette,-0.5,nFette+0.5)
    henerH = ROOT.TH1F("henerH"+suffix,"Horizontal energy",nFette,-0.5,nFette+0.5)
    hcontH = ROOT.TH1F("hcontH"+suffix,"Horizontal contrast",nFette,-0.5,nFette+0.5)
    hhomoH = ROOT.TH1F("hhomoH"+suffix,"Horizontal homogeneity",nFette,-0.5,nFette+0.5)
    # Vertical
    hdissV = ROOT.TH1F("hdissV"+suffix,"Vertical dissimilarity",nFette,-0.5,nFette+0.5)
    hcorrV = ROOT.TH1F("hcorrV"+suffix,"Vertical correlation",nFette,-0.5,nFette+0.5)
    henerV = ROOT.TH1F("henerV"+suffix,"Vertical energy",nFette,-0.5,nFette+0.5)
    hcontV = ROOT.TH1F("hcontV"+suffix,"Vertical contrast",nFette,-0.5,nFette+0.5)
    hhomoV = ROOT.TH1F("hhomoV"+suffix,"Vertical homogeneity",nFette,-0.5,nFette+0.5)
    # + 45
    hdissPQ = ROOT.TH1F("hdissPQ"+suffix,"+45 degree dissimilarity",nFette,-0.5,nFette+0.5)
    hcorrPQ = ROOT.TH1F("hcorrPQ"+suffix,"+45 degree correlation",nFette,-0.5,nFette+0.5)
    henerPQ = ROOT.TH1F("henerPQ"+suffix,"+45 degree energy",nFette,-0.5,nFette+0.5)
    hcontPQ = ROOT.TH1F("hcontPQ"+suffix,"+45 degree contrast",nFette,-0.5,nFette+0.5)
    hhomoPQ = ROOT.TH1F("hhomoPQ"+suffix,"+45 degree homogeneity",nFette,-0.5,nFette+0.5)
    # -45
    hdissMQ = ROOT.TH1F("hdissMQ"+suffix,"-45 degree dissimilarity",nFette,-0.5,nFette+0.5)
    hcorrMQ = ROOT.TH1F("hcorrMQ"+suffix,"-45 degree correlation",nFette,-0.5,nFette+0.5)
    henerMQ = ROOT.TH1F("henerMQ"+suffix,"-45 degree energy",nFette,-0.5,nFette+0.5)
    hcontMQ = ROOT.TH1F("hcontMQ"+suffix,"-45 degree contrast",nFette,-0.5,nFette+0.5)
    hhomoMQ = ROOT.TH1F("hhomoMQ"+suffix,"-45 degree homogeneity",nFette,-0.5,nFette+0.5)
    
    allhistos = []
    histogiafatti = []
    histogclm = [] #CV
    # nfetta=0

    # for fetta,fettaROI in zip(data,mask) :
    for layer in xrange(0,nFette):
    
        fetta = data[layer]
        #fetta8bit = rescale8bit(fetta)
        if scala:
            media = np.mean(fetta)
            rms = np.std(fetta)
            fetta = (fetta - media)/rms
        fetta8bit = (rescale8bit(fetta))
        
        # fettaROI = mask[layer].astype(np.bool)
        fettaROI = mask[layer]
        glcmdata = mask[layer]*fetta8bit     
        #CV gclm
        #glcmdata = fetta8bit[fettaROI]
        # if verbose:
        #print("fetta.max():",fetta.max(),"type:",type(fetta[0][0]))
        #if fettaROI.any():
        #    print("fetta.min():",fetta.min(),"type:",type(fetta[0][0]))            
        #    print("fetta.max():",fetta.max(),"type:",type(fetta[0][0]))
        #    print("fettaROI2.max():",fettaROI2.max(),"type:",type(fettaROI2[0][0]))
        #    print("fetta8bit.max():",fetta8bit.max(),"type:",type(fetta8bit[0][0]))
        #    print("fetta8bit.minx():",fetta8bit.min(),"type:",type(fetta8bit[0][0]))
        #    print("glcmdata.max():",glcmdata.max(),"type:",type(glcmdata[0][0]))            
        glcm1 = greycomatrix(glcmdata, [1], [0], 256, symmetric=True, normed=True)
        glcm2 = greycomatrix(glcmdata, [1], [np.pi/2], 256, symmetric=True, normed=True)
        glcm3 = greycomatrix(glcmdata, [1], [np.radians(45)], 256, symmetric=True, normed=True)
        glcm4 = greycomatrix(glcmdata, [1], [np.radians(-45)], 256, symmetric=True, normed=True)
        #0
        hdissH.SetBinContent(layer,greycoprops(glcm1, 'dissimilarity')[0, 0])
        hcorrH.SetBinContent(layer,greycoprops(glcm1, 'correlation')[0, 0])
        henerH.SetBinContent(layer,greycoprops(glcm1, 'energy')[0, 0])
        hcontH.SetBinContent(layer,greycoprops(glcm1,'contrast')[0, 0])
        hhomoH.SetBinContent(layer,greycoprops(glcm1,'homogeneity')[0, 0])
        #90
        hdissV.SetBinContent(layer,greycoprops(glcm2, 'dissimilarity')[0, 0])
        hcorrV.SetBinContent(layer,greycoprops(glcm2, 'correlation')[0, 0])
        henerV.SetBinContent(layer,greycoprops(glcm2, 'energy')[0, 0])
        hcontV.SetBinContent(layer,greycoprops(glcm2,'contrast')[0, 0])
        hhomoV.SetBinContent(layer,greycoprops(glcm2,'homogeneity')[0, 0])
        #45
        hdissPQ.SetBinContent(layer,greycoprops(glcm3, 'dissimilarity')[0, 0])
        hcorrPQ.SetBinContent(layer,greycoprops(glcm3, 'correlation')[0, 0])
        henerPQ.SetBinContent(layer,greycoprops(glcm3, 'energy')[0, 0])
        hcontPQ.SetBinContent(layer,greycoprops(glcm3,'contrast')[0, 0])
        hhomoPQ.SetBinContent(layer,greycoprops(glcm3,'homogeneity')[0, 0])
        #-45
        hdissMQ.SetBinContent(layer,greycoprops(glcm4, 'dissimilarity')[0, 0])
        hcorrMQ.SetBinContent(layer,greycoprops(glcm4, 'correlation')[0, 0])
        henerMQ.SetBinContent(layer,greycoprops(glcm4, 'energy')[0, 0])
        hcontMQ.SetBinContent(layer,greycoprops(glcm4,'contrast')[0, 0])
        hhomoMQ.SetBinContent(layer,greycoprops(glcm4,'homogeneity')[0, 0])
                                                
        # res = []
        thishisto = ROOT.TH1F("h"+str(layer)+suffix,"h"+str(layer),nbin,binmin,binmax)
        meaninroi = 1
        #AR
        frattale=0
        frattalecont=0
        if fettaROI.max() > 0:
            frattale=fractal().frattali(fettaROI)
            frattalecont=fractal().frattali(fetta*np.subtract(fettaROI,ndimage.binary_erosion(fettaROI).astype(fettaROI.dtype)))
            #        print("FRATTALE",frattale)
            #        print("FRATTALECONT",frattalecont)
            #end AR
        if fettaROI.any():
            if normalize:
                meaninroi = calculateMeanInROI(fetta, ROInorm[layer],verbose)
                if verbose:
                    print("make_histo: layer",layer,"meaninroi",meaninroi)
            # for val, inROI in zip(np.nditer(fetta),np.nditer(fettaROI)):

            if fettaROI.any() and verbose:                
                print("non zero pixels:",np.count_nonzero(fetta))

            
            for val, inROI in zip(fetta.ravel(),fettaROI.ravel()):
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
                    if val > 0:    
                        his.Fill(val)
                        thishisto.Fill(val)

                    
            hEntries.SetBinContent(layer,thishisto.GetEntries())
            hMean.SetBinContent(layer,thishisto.GetMean())
            hStdDev.SetBinContent(layer,thishisto.GetStdDev())
            hSkewness.SetBinContent(layer,thishisto.GetSkewness())
            hKurtosis.SetBinContent(layer,thishisto.GetKurtosis())
            hfra.SetBinContent(layer,frattale) #AR
            hCfra.SetBinContent(layer,frattalecont) #AR

        if verbose:
            print("make_histo","layer",layer, "entries",thishisto.GetEntries())
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
    histogiafatti.append(hfra) #AR
    histogiafatti.append(hCfra) #AR


    #CV
    histogclm.append(hdissH)
    histogclm.append(hcorrH)
    histogclm.append(henerH)
    histogclm.append(hcontH)
    histogclm.append(hhomoH)
    histogclm.append(hdissV)
    histogclm.append(hcorrV)
    histogclm.append(henerV)
    histogclm.append(hcontV)
    histogclm.append(hhomoV)
    histogclm.append(hdissPQ)
    histogclm.append(hcorrPQ)
    histogclm.append(henerPQ)
    histogclm.append(hcontPQ)
    histogclm.append(hhomoPQ)
    histogclm.append(hdissMQ)
    histogclm.append(hcorrMQ)
    histogclm.append(henerMQ)
    histogclm.append(hcontMQ)
    histogclm.append(hhomoMQ)
                       
    
    return his, allhistos, histogiafatti, histogclm
