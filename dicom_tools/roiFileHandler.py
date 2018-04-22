from __future__ import print_function

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
from dicom_tools.roiData import roiData

class roiFileHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.dicomsPath = None

        
    def write(self, filename, roistates, numberOfROIs):
        tobesaved = roiData(roistates, numberOfROIs, self.dicomsPath)
        with open(filename,'w') as file:
            pickle.dump(tobesaved, file)
            # if self.dicomsPath:
            #     pickle.dump(True, file)
            #     pickle.dump(self.dicomsPath, file)
            # else:
            #     pickle.dump(False, file)                
            # for i, roistate in enumerate(roistates):
            #     if roistate:
            #         if self.verbose:
            #             print("saving ",i)
            #         pickle.dump(i, file)
            #         pickle.dump(roistate, file)
        file.close()

    def read(self, filename):
        if self.verbose:
            print("roiFileHandler: reading file "+filename+"\n")
        with open(filename,'r') as file:
            buffer = pickle.load(file)
            file.close()
        self.dicomsPath = buffer.dicomsPath
        roistates = [None]* buffer.originalLenght

        for i, roistate in zip(buffer.layers, buffer.roistates):
            roistates[i] = roistate
        if self.verbose:
            print("roiFileHandler: returning \n")
        return roistates, buffer.numberOfROIs

