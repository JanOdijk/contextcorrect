from sastadev.xlsx import getxlsxdata, mkworkbook
import os

backslash = '\\'

def getcollection(filename):
    path, file = os.path.split(filename)
    pathels = path.split(backslash)
    lpathels = len(pathels)
    subcollection = pathels[-1]
    collection = pathels[-2]
    return collection, subcollection

def getclintd(filename):
    lcfilename = filename.lower()
    if '\\clinical\\' in lcfilename:
        result = 'CLINICAL'
    elif '\\td\\' in lcfilename:
        result = 'TD'
    else:
        result = 'UNKNOWN'
    return result


infilename= 'resultsxlslx.xlsx'
outfilename = 'resultsxlslx-extended.xlsx'
inpath = r'D:\Dropbox\jodijk\myprograms\python\contextcorrection\data\results'

infullname = os.path.join(inpath, infilename)
outfullname = os.path.join(inpath, outfilename)

header, data = getxlsxdata(infullname)
newdata = []
newheader = header + ['DEVSTATUS', 'Collection', 'Subcollection']
for row in data:
    filename = row[16]
    collection, subcollection = getcollection(filename)
    clintd = getclintd(filename)
    newcols = [clintd, collection, subcollection]
    newrow = row + newcols
    newdata.append(newrow)

wb = mkworkbook(outfullname, [newheader], newdata,  freeze_panes= (1,0) )
wb.close()