from __future__ import print_function
from openpyxl import load_workbook
from tabulate import tabulate

def xlsReader(filename, verbose=True):
    if(verbose):
        print("xlsReader")
    wb = load_workbook(filename = 'responders.xlsx')
    sheet_names = wb.get_sheet_names()
    if(verbose):
        print("sheet names:",sheet_names)
    results = []
    
    for sheet_name in sheet_names:
        if(verbose):
            print("sheet name: ",sheet_name)
        sheet = wb.get_sheet_by_name(sheet_name)

        converted_sheet = []

        for row in sheet.rows:
            converted_row = []
            for cell in row:
                converted_row.append(cell.value)
            converted_sheet.append(converted_row)


        results.append(converted_sheet)

    return results
