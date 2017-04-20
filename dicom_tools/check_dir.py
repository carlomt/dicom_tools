import os
import glob
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.nrrdFileHandler import nrrdFileHandler

def check_dir(inputdir, verbose=False):
    if verbose:
        print("inputdir",inputdir)
    table = []

    patientdirs= glob.glob(inputdir+"*/")
    for patientdir in patientdirs:

        
        if verbose:
            print(patientdir)
        if patientdir[-1]=='/':
            patID = patientdir.split('/')[-2].replace('.','')
        else:
            patID = patientdir.split('/')[-1].replace('.','')
        if verbose:
            print("id:",patID)

        analasisysdirs=glob.glob(patientdir+"*/")
        for analasisysdir in analasisysdirs:
            patient = []
            patient.append(patID)
            
            if verbose:
                print("\t",analasisysdir)

            pathT2 = analasisysdir + "T2/"
            pathROI = analasisysdir + "ROI/"
                # freader = FileReader(pathT2, pathROI, args.verbose)
            if verbose:
                print("reading on patient: "+patID)
                print("T2 directory: "+pathT2)
            if os.path.isdir(pathT2):
                dicomfiles = glob.glob(pathT2+"/*.dcm")
                allfiles = glob.glob(pathT2+"/*")
                patient.append(len(dicomfiles))
                patient.append(len(allfiles)-len(dicomfiles))                
            else:
                patient.append(0)
                patient.append(0)                
            
            pathROI = analasisysdir + "ROI/"
            if os.path.isdir(pathROI):
                nrrdfiles = glob.glob(pathROI+"/*.nrrd")
                if len(nrrdfiles) > 0 :
                    fr = nrrdFileHandler(False)
                    nrrdROI = fr.read(nrrdfiles[0])
                    dicomfiles = glob.glob(pathROI+"/*.dcm")
                    allfiles = glob.glob(pathROI+"/*")
                    # patient.append(len(nrrdfiles))
                    patient.append(len(nrrdROI))
                    patient.append(len(dicomfiles))
                    patient.append(len(allfiles)-len(dicomfiles)-len(nrrdfiles))
                else:
                    patient.append(0)
                    patient.append(0)
                    patient.append(0)
            else:
                patient.append(0)
                patient.append(0)
                patient.append(0)

            infofilename = analasisysdir + "info.txt"
            if os.path.isfile(infofilename):
                infos = info_file_parser(infofilename)
                patient.append(infos["time"])
                patient.append(infos["ypT"])                         
                patient.append(infos["name"])

            else:
                patient.append("None")
                patient.append("None")                         
                patient.append("None")


            table.append(patient)
    return table

