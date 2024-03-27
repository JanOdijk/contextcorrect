englishfilename = r"D:\Dropbox\jodijk\Utrecht\Projects\SASTA emer\Word Replacement Prediction\english lexicon\words.txt"

englishdict = {}
with open(englishfilename, 'r', encoding='utf8') as englishfile:
    for line in englishfile:
        cleanline = line[:-1] if line[-1] == '\n' else line
        englishdict[cleanline] = 1

unknownwordsfilename = 'unknownwords.txt'
with open(unknownwordsfilename, 'r', encoding='utf8') as unknownwordsfile:
    for line in unknownwordsfile:
        fields = line.split()
        word = fields[0]
        if word in englishdict:
            print(line[:-1])