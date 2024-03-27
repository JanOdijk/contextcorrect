from optparse import OptionParser
import os
import sys
from collections import Counter
from getcontextcorrections import getchatdata, getspeaker, tokenize
from sastadev.chatundo import chatundo
from validwords import isvalidword

defaultchildespath = r'Y:\research-coco\CHILDES_Dutch_Transcripts'

space = ' '

def getutt(utt:str) -> str:
    colonpos = utt.find(':\t')
    result = utt[colonpos+2:]
    return result

def main():

    parser = OptionParser()
    parser.add_option("-c", "--childes", dest="childespath",
                      help="Path to the folder containing the CHILDES data")

    (options, args) = parser.parse_args()


    if options.childespath is None:
        childespath = defaultchildespath
    else:
        childespath = options.childespath

    #  process all files in all folders and subfolders
    unknowns = Counter()
    for root, dirs, thefiles in os.walk(childespath):
        print('Processing {}...'.format(root), file=sys.stderr)

        # we only want the filenames with extension *cha*
        chafiles = [f for f in thefiles if f[-3:] == 'cha']
        junk = 0
        for infilename in chafiles:
            # print(f'Processing {infilename}...', file=sys.stderr)
            testing = False
            if testing:
                infullname = r"D:\Dropbox\various\Resources\CHILDES\VanKampen\VanKampen\laura09.cha"
            else:
                infullname = os.path.join(root, infilename)
            headerdata, utterances = getchatdata(infullname)
            for i, utterance in enumerate(utterances):
                utterancespeaker = getspeaker(utterance)
                bareutterance = getutt(utterance)
                tokens = tokenize(bareutterance)
                cleanbareutt = space.join(tokens)
                rawcleanbareutt = chatundo(cleanbareutt)
                rawtokens = tokenize(rawcleanbareutt)
                for token in rawtokens:
                    if not isvalidword(token):
                        unknowns.update([token])

    unknownfilename = 'unknownwords.txt'
    with open(unknownfilename, 'w', encoding='utf8') as unknownfile:
        for el, i in unknowns.most_common():
            print(el, i, file=unknownfile)



if __name__ == '__main__':
    main()