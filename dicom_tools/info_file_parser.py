
def info_file_parser(filename, verbose=False):

    results = {}
    infile = open(filename,'r')
    for iline, line in enumerate(infile):
        if line[0]=='#': continue
        lines = line.split()
        if len(lines)<2 : continue
        if lines[0][0]=='#': continue
        infotype = lines[0]
        infotype=infotype.replace(':','')
        info = lines[1]
        results[infotype]=info

    return results
