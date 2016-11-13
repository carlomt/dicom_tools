class roiData:
    
    def __init__(self, roistates, dicomsPath=None):
        self.layers = []
        self.roistates = []
        self.dicomsPath=dicomsPath
        self.originalLenght = len(roistates)

        for i, roistate in enumerate(roistates):
            if roistate:
                self.layers.append(i)
                self.roistates.append(roistate)
