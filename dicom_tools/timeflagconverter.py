

def timeflagconverter_int2string(timeflag):
    timestring=""
    if timeflag == 0:
        timestring = "pre"
    elif timeflag==1:
        timestring = "int"
    elif timeflag == 2:
        timestring = "post"
    else:
        print("ERROR","timestring not recognized:",timestring)
        
    return timestring
        

def timeflagconverter_string2int(timestring):
    timeflag=-1
    if timestring=="pre":
        timeflag = 0
    elif timestring=="int":
        timeflag = 1
    elif timestring=="post":
        timeflag = 2
    else:
        print("ERROR","timestring not recognized:",timeflag)
    
    return timeflag
