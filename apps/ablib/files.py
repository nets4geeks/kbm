
import os

def files(path):
    return sorted (os.listdir(path))

# extension without dot
# low registry
def filesWithExtension(path,extension):
    return sorted ([fileName for fileName in os.listdir(path) if fileName.endswith("."+extension)])

def get(path):
    fl = files(path)
    docs = []
    for fname in fl:
        with open(path+"/"+fname) as f:
            docs.append(f.read())
    return docs


def get1(path):
    fl = files(path)
    docs = []
    for fname in fl:
        x = open(path+"/"+fname).read().splitlines()
        docs.append(x)
    return docs

# read given list of short filenames
def get2(path,fileNames):
    docs = []
    for fname in fileNames:
        x = open(path+"/"+fname).read().splitlines()
        docs.append(x)
    return docs

