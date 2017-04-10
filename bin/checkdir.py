import os
import glob
from dicom_tools.info_file_parser import info_file_parser
from dicom_tools.nrrdFileHandler import nrrdFileHandler
from tabulate import tabulate

def checkdir(inputdir, verbose=False):
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
            infos = info_file_parser(analasisysdir + "info.txt")
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
                
            infos = info_file_parser(analasisysdir + "info.txt")
            patient.append(infos["time"])
            patient.append(infos["ypT"])                         
            patient.append(infos["name"])

            table.append(patient)
    return table

if __name__ == '__main__':

    table = checkdir("/data/dicoms/retti_test_anon/")
    print tabulate(table, headers=["ID","n T2 dcm files","n T2 other files","nrrd ROI layers","n dcm ROI files","n other ROI files","Timing","ypT", "ID (check)"],tablefmt="fancy_grid")
