import os

def ifNeededMkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)
