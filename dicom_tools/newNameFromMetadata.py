from __future__ import print_function
import os
try:
    import dicom
except ImportError:
    import pydicom as dicom

def newNameFromMetadata(in_dir, verbose=False):
    filenames = os.listdir(in_dir)
    if verbose:
        print("newNameFromMetadata: input directory", in_dir)
        print("newNameFromMetadata: files in the direcotry", filenames)        
    filename = filenames[0]
    # Load the current dicom file to 'anonymize'
    dataset = dicom.read_file(in_dir+"/"+filename)
    
    oldname = dataset.PatientsName.split('^')
    if len(oldname)<2:
        oldname = dataset.PatientsName.replace(',','')
        oldname = oldname.split()
    # if len(oldname)!=2:
    print("WARNING:",dataset.PatientsName)

    new_person_name = oldname[0][0]+oldname[0][1]+oldname[1][0]+oldname[1][1]
    return new_person_name

