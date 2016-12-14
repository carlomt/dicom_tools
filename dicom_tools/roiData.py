class roiData:
    
    def __init__(self, roistates, numberOfROIs, dicomsPath=None):
        self.layers = []
        self.roistates = []
        self.dicomsPath=dicomsPath
        self.originalLenght = len(roistates)
        self.numberOfROIs = numberOfROIs
        
        for i, roistate in enumerate(roistates):
            if roistate:
                self.layers.append(i)
                self.roistates.append(roistate)
