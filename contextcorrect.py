from typing import Dict, List, Optional, Set, Tuple
from optparse import OptionParser
import os
import sys
import re
from sastadev import sastatok
from sastadev.cleanCHILDEStokens import cleantext
from sastadev.lexicon import known_word
from collections import defaultdict, Counter
from bertje import getbertjemaskwords, getbertjemaskwordswithscores
from chatfunctions import getbody, getbodystart, getchatdata, getchildage, getcontext2, getexplanationswithspan, getnoncompletionswithspan, \
    getreplacementswithspan, getspeaker, gettargetspeaker, mycleantext, tokenize
from parameters import redthreshold, maxcontextwordsize, minimumwordlength
from relativedistance import relativedistance as red
from collections import Counter
from sastadev.xlsx import mkworkbook
import shutil

reportevery = 10

Method = str
Span = Tuple[int, int]

# defaultchildespath = r'D:\Dropbox\various\Resources\CHILDES'
# defaultchildespath = r'D:\Dropbox\jodijk\myprograms\python\chametadata2\testin'
# defaultchildespath = './data'
# defaultchildespath = r'D:\Dropbox\various\Resources\CHILDES\VanKampen\VanKampen'
# defaultchildespath = r'D:\Dropbox\jodijk\myprograms\python\contextcorrection\data\testdata'
# defaultchildespath = r'D:\Dropbox\jodijk\myprograms\python\contextcorrection\data\testdata2'
# defaultchildespath = r'Y:\research-coco\CHILDES_Dutch_Transcripts\TD\VanKampen'
defaultchildespath = r'Y:\research-coco\CHILDES_Dutch_Transcripts'

space = ' '
dummy = 'dummy'  # not used anymore
maskmask = "MASKMASK"
unlimited = 100000   # maybe: float("inf") ?

bertjemethod = 'bertje'
contextmethod = 'context'
bertjepluscontextmethod = 'b+c'
contextifbertjemethod = 'cib'
historymethod = 'history'

methods = [bertjemethod, contextmethod, bertjepluscontextmethod]

correctpredictioncount = {}
wrongpredictioncount = {}
multiplepredictioncount = {}
nopredictioncount = {}
correctinpredictionscount = {}

countscount = 5 * len(methods)

correctlypredictedwords = {}
wronglypredictedwords = {}
multiplypredictedwords = {}

for method in methods:
    correctpredictioncount[method] = 0
    wrongpredictioncount[method] = 0
    multiplepredictioncount[method] = 0
    nopredictioncount[method] = 0
    correctinpredictionscount[method] = 0

    correctlypredictedwords[method] = Counter()
    wronglypredictedwords[method] = Counter()
    multiplypredictedwords[method] = Counter()

allmethodcounts = [correctpredictioncount, wrongpredictioncount, nopredictioncount , multiplepredictioncount,
                   correctinpredictionscount]

allmethodcounters = [ correctlypredictedwords, wronglypredictedwords, multiplypredictedwords]

resultsfolder = './data/results'
resultstsvfilename = 'contextcorrectionresults.txt'
resultstsvfullname = os.path.join(resultsfolder, resultstsvfilename)

allrecords = []


BERTjeheader = ['BERTjecorrect', 'BERTjewrong', 'BERTjeNO', 'BERTjemult', 'BERTjecorrectinprediction']
Contextheader = ['CONTEXTcorrect', 'CONTEXTwrong', 'CONTEXTNO', 'CONTEXTmult', 'CONTEXTcorrectinprediction']
BelseCheader = ['BelseCcorrect', 'BelseCwrong', 'BelseCNO', 'BelseCmult', 'BelseCcorrectinprediction']
metaheader = ['Childage', 'filename']
header = BERTjeheader + Contextheader + BelseCheader + metaheader

resultstsvfile = open(resultstsvfullname, 'w', encoding='utf8')
print(header, file=resultstsvfile)

counterheaders = ['correctly predicted words', 'wrongly predicted words', 'multiplypredictedwords']

def getnoncum(record, recordlist):
    if recordlist == []:
        result = record
    else:
        previous = recordlist[-1]
        result = [ record[i] - previous[i] for i in range(countscount)] + record[countscount:]
        # print(f'{record}\n{recordlist}\n{result}')
        # junk = input('Continue?')
    return result


def getuttforbertje(utt:str, span: Tuple[int,int]) -> Tuple[bool, str]:
    part1 = utt[:span[0]]
    part2 = utt[span[1]:]
    roughutt = f'{part1} {maskmask} {part2}'
    cleanutt, meta1 = mycleantext(roughutt, repkeep=False)
    if maskmask in cleanutt:
        result = True, cleanutt.replace(maskmask, '[MASK]')
    else:
        result = False, cleanutt
    return result


def getfullcontext(prevcontext: List[str], cleantargetutt:str, postcontext: List[str]):
    resultlist: List[str] = []
    for line in prevcontext:
        body = getbody(line)
        resultlist.append(body)
    resultlist.append(cleantargetutt)
    for line in postcontext:
        body = getbody(line)
        resultlist.append(body)
    result = space.join(resultlist)
    return result

def getclosestmatches(wrong: str, bertjepredictions: List[str]) -> List[str]:
    results = []
    mindiff = 1
    for bertjeprediction  in bertjepredictions:
        thered = red(wrong, bertjeprediction)
        if thered < redthreshold:
            if thered < mindiff:
                results = [bertjeprediction]
                mindiff = thered
            elif thered == mindiff:
                results.append(bertjeprediction)
    return results

def updateresults(predictions: List[str], wrong:str, correct:str, scores: dict,  method: Method) -> None:
    if predictions == []:
        nopredictioncount[method] += 1
    elif len(predictions) > 1:
        multiplepredictioncount[method] += 1
        thescore = scores[predictions[0]] if predictions[0] in scores else -1
        multiplypredictedwords[method].update([(wrong, predictions[0], correct, thescore)])
        # we take the first one as the prediction
        if predictions[0] == correct:
            correctpredictioncount[method] += 1
            thescore = scores[predictions[0]] if predictions[0] in scores else -1
            correctlypredictedwords[method].update([(wrong, predictions[0], correct, thescore)])
        else:
            wrongpredictioncount[method] += 1
            thescore = scores[predictions[0]] if predictions[0] in scores else -1
            wronglypredictedwords[method].update([(wrong, predictions[0], correct, thescore)])
            if correct in predictions:
                correctinpredictionscount[method] += 1
    elif len(predictions) == 1:
        if predictions[0] == correct:
            correctpredictioncount[method] += 1
            thescore = scores[predictions[0]] if predictions[0] in scores else -1
            correctlypredictedwords[method].update([(wrong, predictions[0], correct, thescore)])
        else:
            wrongpredictioncount[method] += 1
            thescore = scores[predictions[0]] if predictions[0] in scores else -1
            wronglypredictedwords[method].update([(wrong, predictions[0], correct, thescore)])

def getwords(context: List[str]) -> Set[str]:
    result = set()
    for utt in context:
        tokens = tokenize(utt)
        for token in tokens:
            result.add(token)
    return result

def getcontextpredictions(wrong: str, context: List[str]) -> list[str]:
    words = getwords(context)
    rawpredictions = [ word for word in words if red(wrong, word) < redthreshold ]
    mindiff = 1.0
    predictions = []
    for rawprediction in rawpredictions:
        thered = red(wrong, rawprediction)
        if thered < mindiff:
            predictions = [rawprediction]
            mindiff = thered
        elif thered == mindiff:
            predictions.append(rawprediction)
    return predictions

def dealwith(correctiontuples: List[Tuple[str, str, Span]], utterances: List[str], i: int, targetspeaker: str):


    theutterance = utterances[i]
    printcases = False
    if printcases:
        for correctiontuple in correctiontuples:
            print(f'{correctiontuple} in: {i}:{theutterance}')
    bodystart = getbodystart(theutterance)
    thebody = getbody(theutterance)
    for correctiontuple in correctiontuples:
        (wrong, correct, span) = correctiontuple
        # adapt the span to the body
        span = span[0] - bodystart, span[1] - bodystart
        if len(wrong) < minimumwordlength:
            return None

        # get the masked utterance, cleaned
        ok, cleantargetbody = getuttforbertje(thebody, span)
        if not ok:
            continue

        # get the context, until maxwords has been reached
        cond = lambda utt, tsp: getspeaker(utt) != tsp
        prevcontext = getcontext2(utterances, i, -unlimited, targetspeaker, cond, maxcontextwordsize)
        postcontext = getcontext2(utterances, i, unlimited, targetspeaker, cond, maxcontextwordsize)
        bertjeinput = getfullcontext(prevcontext, cleantargetbody, postcontext)

        # apply bertje, record the results, mk frq list of wrongly predicted words
        rawbertjepredictionswithscores = getbertjemaskwordswithscores(bertjeinput)

        rawbertjepredictions= [prediction for prediction, score in rawbertjepredictionswithscores]
        scores = {prediction: score for prediction, score in rawbertjepredictionswithscores}


        # find the closest match(es) to wrong, if any
        bertjepredictions = getclosestmatches(wrong, rawbertjepredictions)
        updateresults(bertjepredictions, wrong, correct, scores, bertjemethod)

        # apply context search, record the results
        context = prevcontext + postcontext
        contextpredictions = getcontextpredictions(wrong, context)
        contextscores = {}
        updateresults(contextpredictions, wrong, correct, contextscores, contextmethod)

        # compute the results of a combined bertje = context search
        bertjepluscontextpredictions = contextpredictions if bertjepredictions == [] else bertjepredictions
        updateresults(bertjepluscontextpredictions, wrong, correct, scores, bertjepluscontextmethod)


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
    for root, dirs, thefiles in os.walk(childespath):
        print('Processing {}...'.format(root), file=sys.stderr)

        # we only want the filenames with extension *cha*
        chafiles = [f for f in thefiles if f[-3:] == 'cha']
        junk = 0
        filectr = 0
        for infilename in chafiles:
            filectr += 1
            if filectr % reportevery == 0:
                print(filectr, file=sys.stderr)
            print(f'Processing {infilename}...', file=sys.stderr)
            testing = False
            if testing:
                infullname = r"D:\Dropbox\various\Resources\CHILDES\VanKampen\VanKampen\laura09.cha"
            else:
                infullname = os.path.join(root, infilename)

            # we want counts per file so we have to reset the couners upon a new file
            for method in methods:
                correctpredictioncount[method] = 0
                wrongpredictioncount[method] = 0
                multiplepredictioncount[method] = 0
                nopredictioncount[method] = 0
                correctinpredictionscount[method] = 0

            headerdata, utterances = getchatdata(infullname)
            targetspeaker = gettargetspeaker(headerdata)
            childage = getchildage(targetspeaker, headerdata)
            for i, utterance in enumerate(utterances):
                utterancespeaker = getspeaker(utterance)
                if utterancespeaker == targetspeaker:
                    noncompletiontuples = getnoncompletionswithspan(utterance)
                    dealwith(noncompletiontuples, utterances, i, targetspeaker)
                    replacementtuples = getreplacementswithspan(utterance)
                    dealwith(replacementtuples, utterances, i, targetspeaker)
                    explanationtuples = getexplanationswithspan(utterance)
                    dealwith(explanationtuples, utterances, i, targetspeaker)

            # store in a datastructure the results to a file

            metadata = [ childage, infullname]
            countcols = []
            for method in methods:
                for countdict in allmethodcounts:
                    if method in countdict:
                        countcols.append(countdict[method])
                    else:
                        countcols.append(0)
            fullrecord = countcols + metadata  # this is a cumulative count not easy to repair
            allrecords.append(fullrecord)
            print(fullrecord, file=resultstsvfile)
            resultstsvfile.flush()
    for method in methods:
        for label, counterdict in zip(counterheaders, allmethodcounters):
            # print(label)
            if method in counterdict:
                # print(f'Method = {method}')
                frqfilename = f'{label}_{method}_frq.txt'
                frqfullname = os.path.join(resultsfolder, frqfilename)
                with open(frqfullname, 'w', encoding='utf8') as frqfile:
                    for tpl, cnt in counterdict[method].most_common():
                        wrong, pred, correct, score = tpl
                        print(f'{wrong}\t{pred}\t{correct}\t{score}\n{cnt}', file=frqfile)
    resultsxlsxfilename = 'resultsxlslx.xlsx'
    resultxlslxfullname = os.path.join(resultsfolder, resultsxlsxfilename)
    wb = mkworkbook(resultxlslxfullname, [header], allrecords)
    wb.close()
    resultstsvfile.close()

if __name__ == '__main__':
    main()