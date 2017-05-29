from dicom_tools.check_dir import check_dir
from tabulate import tabulate
#from dicom_tools.myTabulate import myTabulate

if __name__ == '__main__':

    table = check_dir("/data/dicoms/retti_test_anon/", True)
    print tabulate(table, headers=["ID","n T2 dcm files","n T2 other files","nrrd ROI layers","n dcm ROI files","n other ROI files","Timing","ypT", "ID (check)"],tablefmt="fancy_grid")

