import ROOT

def make_histo(data, mask):
    nbin = 100

    his = ROOT.TH1F("histo","histo",nbin,0,3)
    for fetta,fettaROI in zip(data,mask) :
        if fettaROI.max() > 0 :
            norm = fetta.mean()
            for riga, rigaROI in zip(fetta,fettaROI) :
                for val, inROI in zip(riga, rigaROI) :
                    if inROI>0 :
                        his.Fill(val/norm)
                        # print(val)

    return his
