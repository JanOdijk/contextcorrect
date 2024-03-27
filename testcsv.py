import csv

tab = '\t'
infilename = r"D:\Dropbox\jodijk\myprograms\python\contextcorrection\data\memory\bertjememory.txt"

memory = {}
with open(infilename, 'r',  encoding='utf8') as infile:
    memreader = csv.reader(infile, delimiter=tab)
    for row in memreader:
        lrow = len(row)
        memory[row[0]] = [row[i] for i in range(1, 5)]
        print(row)
