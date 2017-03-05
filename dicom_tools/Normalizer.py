import ROOT
import numpy as np
from dicom_tools.FileReader import FileReader

class Normalizer:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.RootOutput = False
        self.layer=-1
        self.NormLayer=-1
        if self.verbose:
            print("Normalizer: init verbose\n")

        self.externalTemplateSetted = False
        self.externalTemplate = None

    def setExternalTemplate(self, dcmfile):
        freader = FileReader(dcmfile, False, self.verbose)
        dataRGB, unusedROI = freader.read(False)
        self.externalTemplateSetted = True
        self.externalTemplate = dataRGB[:,:,0]
        self.NormLayer = -1
        
    def setNormLayer(self, layer=-1):
        self.NormLayer=layer
        self.externalTemplateSetted = False
        self.externalTemplate = None
            
    def setRootOutput(self, prefix=""):
        self.RootOutput = True
        self.allHistos = []
        self.RootPrefix = prefix

    def writeRootOutputOnFile(self, outfname="out.root"):
        outfile= ROOT.TFile(outfname,"RECREATE")
        for histo in self.allHistos:
            histo.Write()

        outfile.Write()
        outfile.Close()
        
        
    def hist_match(self, source, template):
        """
        Adjust the pixel values of a grayscale image such that its histogram
        matches that of a target image
        
        Arguments:
        -----------
        source: np.ndarray
        Image to transform; the histogram is computed over the flattened array
        template: np.ndarray
        Template image; can have different dimensions to source
        Returns:
        -----------
        matched: np.ndarray
        The transformed output image
        """

        oldshape = source.shape
        # contiguous flattened array
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.ravel.html
        source = source.ravel()
        template = template.ravel()
        
        # get the set of unique pixel values and their corresponding indices and
        # counts
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.unique.html
        s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                                return_counts=True)
        t_values, t_counts = np.unique(template, return_counts=True)
        
        # take the cumsum of the counts and normalize by the number of pixels to
        # get the empirical cumulative distribution functions for the source and
        # template images (maps pixel value --> quantile)
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.cumsum.html?highlight=sum
        s_quantiles = np.cumsum(s_counts).astype(np.float64)
        s_quantiles /= s_quantiles[-1]
        t_quantiles = np.cumsum(t_counts).astype(np.float64)
        t_quantiles /= t_quantiles[-1]
        
        # interpolate linearly to find the pixel values in the template image
        # that correspond most closely to the quantiles in the source image
        interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)
        
        if self.RootOutput:
            suffix=str(self.layer)
            prefix=self.RootPrefix
            nBin = 500
            cumsumOrig = ROOT.TH1F(prefix+"cumsumOrig"+suffix,prefix+"cumsumOrig"+suffix,nBin,s_values.min(),s_values.max())
            cumsumTemplate = ROOT.TH1F(prefix+"cumsumTemplate"+suffix,prefix+"cumsumTemplate"+suffix,nBin,t_values.min(),t_values.max())
            cumsumInterp = ROOT.TH1F(prefix+"cumsumInterp"+suffix,prefix+"cumsumInterp"+suffix,nBin,interp_t_values.min(),interp_t_values.max())
            for s_value in s_values:
                cumsumOrig.Fill(s_value)
            for t_value in t_values:
                cumsumTemplate.Fill(s_value)
            for interp_t_value in interp_t_values:
                cumsumInterp.Fill(interp_t_value)
                
            self.allHistos.append(cumsumTemplate)        
            self.allHistos.append(cumsumOrig)            
            self.allHistos.append(cumsumInterp)

        return interp_t_values[bin_idx].reshape(oldshape)


    
    def match_all(self, data):
        norm_layer=self.NormLayer
        
        matched=np.zeros(data.shape)
        if len(data.shape)==4:
            layers = len(data[:,:,:,0])
            if not self.externalTemplateSetted:
                if norm_layer <0:
                    norm_layer = int(layers/2+0.5)
                matched[norm_layer,:,:,0]=matched[norm_layer,:,:,1]=matched[norm_layer,:,:,2] = data[norm_layer,:,:,0]
                template = data[norm_layer,:,:,0]
            else:
                template = self.externalTemplate
                
            for self.layer in xrange(0,layers):
                if self.layer == norm_layer:
                    continue
                matched[self.layer,:,:,0]=matched[self.layer,:,:,1]=matched[self.layer,:,:,2]= self.hist_match(data[self.layer,:,:,0], template)
        elif len(data.shape)==3:
            layers = len(data)
            if norm_layer <0:
                norm_layer = int(layers/2+0.5)
            matched[norm_layer] = data[norm_layer]
            for self.layer in xrange(0,layers):
                if self.layer == norm_layer:
                    continue
                matched[self.layer] = self.hist_match(data[self.layer], data[norm_layer])

        else:
            print("ERROR hist_match data has not 4 axis nor 3")
            
        return matched
