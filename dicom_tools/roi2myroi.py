from __future__ import print_function
import numpy as np
from scipy.spatial import ConvexHull
import dicom_tools.pyqtgraph as pg

def roi2myroi(ROI, verbose=False):
    rois = [None]*len(ROI)
    firsttime = True
    
    for layer in xrange(0, len(ROI)):
        fetta = ROI[layer]
        apoints = []
        if fetta.max() > 0 :
            for j, riga in enumerate(fetta):
                for i, elemento in enumerate(riga):
                    if elemento:
                        thispoint = [i,j]
                        apoints.append(thispoint)
            points = np.array(apoints)
            if firsttime:
                firsttime = False
                for point in points:
                    print(point)
                        
            hull = ConvexHull(points)
            rois[layer] = pg.PolyLineROI(hull.simplices.tolist(), pen=(6,9), closed=True).saveState()
    return rois
            # print "hull.simplices", hull.simplices
