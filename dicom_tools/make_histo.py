import ROOT

def make_histo(data, mask):
    nbin = 101

    his = ROOT.TH1F("histo","histo",nbin,-0.5,2000.5)
    for fetta,fettaROI in zip(data,mask) :
        if fettaROI.max() > 0 :
            for riga, rigaROI in zip(fetta,fettaROI) :
                for val, inROI in zip(riga, rigaROI) :
                    if inROI>0 :
                        his.Fill(val)
                        # print(val)

    return his
