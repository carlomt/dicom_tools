import glob
import dicom


infiles = glob.glob("*.dcm")

for thisfile in infiles:
    a = dicom.read_file(thisfile)
    print(thisfile, a.InStackPositionNumber, a.SliceLocation, a.InstanceNumber, a.MagneticFieldStrength, a.ImagingFrequency)
