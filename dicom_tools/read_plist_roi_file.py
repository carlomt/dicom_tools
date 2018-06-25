import plistlib
import dicom_tools.pyqtgraph as pg

def read_plist_roi_file(fname, nOfRois=0, shape=None, debug=False):
    with open(fname, 'rb') as fp:
        pl = plistlib.load(fp)
        outrois = [None]*len(pl['Images'])
        nRois = 0
        for image in pl['Images']:
            points = image['ROIs'][0]['Point_px']
            outpoints = []
            try:
                imageHeight = image['ImageHeight']
            except KeyError:
                if shape is not None:
                    imageHeight = shape[1]
                else:
                    raise IndexError("The image height is not indicated in the xml file, pass it as input")
            imageIndex = image['ImageIndex']
            for point in points:
                if debug:
                    print(point,type(point))
                px = float(point.split(",")[0][1:])
                py = -float(point.split(",")[1][:-1])
                if debug:
                    print(px,py)
                outpoints.append([px,py])
            if debug:
                print(image['ImageIndex'],outpoints)
            if imageIndex < len(outrois):
                outrois[imageIndex] = pg.PolyLineROI(outpoints, closed=True).saveState()
            else:
                outrois[nRois] = pg.PolyLineROI(outpoints, closed=True).saveState()
            nRois += 1
            if nOfRois and nRois >= nOfRois:
                break

    return outrois, nRois
