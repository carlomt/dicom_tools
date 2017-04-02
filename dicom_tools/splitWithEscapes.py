

def splitWithEscapes(theString,splittingChar=' ',escapeChar='\\',verbose=False):
    words = theString.split(splittingChar)
    iword = 0
    while iword < (len(words)-1):
        if verbose:
            print("splitWithEscapes",iword,words[iword])
        if len(words[iword])>2:
            if words[iword][-1]==escapeChar:
                words[iword]=words[iword][:-1]+splittingChar+words[iword+1]
                words.remove(words[iword+1])
                iword-=2
        iword+=1
    for word in words:
        if word=='':
            words.remove(word)
        if word=='\n':
            words.remove(word)            
    if verbose:
        print("splitWithEscapes",words)
    return words
