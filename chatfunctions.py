'''
The module *chatfunctions* provides functions for  data in CHAT format

The module requires the package sastadev, which can be installed in the usual way:

pip install sastadev

It also requires some other packages, but these are packages that come with any Python installation.

there are functions for three types of corrections indicated by means of CHAT annotation:

 * Noncompletion of a word, e.g. the child says *goen*, intends *groen*, notated as *g(r)oen*
 * Replacement, e.g. the child says *kossie*, intends *koffie*, notated as *kossie [: koffie]*
 * Explanation, e.g the child says *poolood*, intends *potlood*, notated as *poolood [= potlood]

 We call in these cases *groen*, *koffie*, and *potlood* the corrections for the actual words uttered.

 Explanations can contain multiple words and can also contain non-Dutch words.
The functions only searches for  explanations by a single word that is also an existing word of Dutch.
 In order to determine whether a word is word of Dutch it uses the function *isvalidword*, which uses the function
   *known_word* from *sastadev.lexicon*


'''
from typing import Dict, List, Optional,Tuple
from optparse import OptionParser
import os
import sys
import re
import sastadev.sastatok
from sastadev.lexicon import known_word
from sastadev.cleanCHILDEStokens import cleantext
from collections import defaultdict, Counter
# from namepartlexicon import namepart_isa_namepart, namepart_isa_namepart_uc
# import celexlexicon
#
#
# # the CHAT codes xxx and yyy must be recognised as valid codes and as valid words in some cases
# chatspecials = ['xxx', 'yyy']
#
# lexicon = 'celex'

tab = '\t'
colon = ':'

interpunctpattern = r'([\w\)])([?!.<>,])'
interpunctre = re.compile(interpunctpattern)

prevcontextsize = -3
postcontextsize = +3

noncompletiontype, replacementtype, explanationtype = 0, 1, 2
allcorrtypes = [noncompletiontype, replacementtype, explanationtype]

name = {}
name[noncompletiontype] = 'noncompletiontype'
name[replacementtype] = 'replacementtype'
name[explanationtype] = 'explanationtype'

space = ' '
# defaultchildespath = r'D:\Dropbox\various\Resources\CHILDES'
# defaultchildespath = r'D:\Dropbox\jodijk\myprograms\python\chametadata2\testin'
defaultchildespath = '.'



# regular expressions used to obtain the wrong words and their corrections
noncompletionpattern = r'(.*)\((\w*)\)(.*)'
noncompletionre = re.compile(noncompletionpattern)

uttnoncompletionpattern = r'[\w\(\)]*\(\w+\)[\w\(\)]*'
uttnoncompletionre = re.compile(uttnoncompletionpattern)


replacementpattern = r'(\w+)\s*\[:\s*(\w+)\s*\]'
replacementre = re.compile(replacementpattern)

multiwordreplacementpattern = r'(\w+)\s*\[:([\s\w]*)\]'
multiwordreplacementre = re.compile(multiwordreplacementpattern)

explanationpattern = r'(\w+)\s*\[=\s+(\w+)\s*\]'
explanationre = re.compile(explanationpattern)

# officially [= must be followed by a space. But this is often not done, and does not lead to ambiguity in some cases
# for these we are robust and allow the absence of space
robustexplanationpattern = r'(\[=)([^!? ])'
robustexplanationre = re.compile(robustexplanationpattern)

# these words are not considered valid words by the function *known_word* but we count them as correct
validwords = {"z'n", 'dees', 'cool'}
punctuationsymbols = """.,?!:;"'"""


correctionprevcounter = 0
correctionpostcounter = 0
correctionnoprevcounter = 0
correctionnopostcounter = 0


lengthfreqdict = Counter()

correctionprevdict = {}
correctionpostdict = {}
correctiondict= {}
for corrtype in allcorrtypes:
    correctionprevdict[corrtype] = defaultdict(int)
    correctionpostdict[corrtype] = defaultdict(int)
    correctiondict[corrtype] = defaultdict(int)

correctioncontexts = []
lengthfreqdict = Counter()

def mycleantext(utt: str, repkeep=False):
    newutt = utt
    newutt = newutt.replace('\u201C', '"')
    newutt = newutt.replace('\u201D', '"')
    newutt, meta = cleantext(newutt, repkeep=repkeep)
    return newutt, meta



def getexplanations(rawutt):
    '''
    function to obtain the explanations from an utterance
    :param rawutt: str
    :return: List of (wrongword, correction) pairs
    '''
    results = []
    utt = robustexplanationre.sub(r'\1 \2', rawutt)
    matches = explanationre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        correct = match.group(2)
        if isvalidword(correct):
            results.append((wrong, correct))
    return results

def getexplanationswithspan(rawutt):
    '''
    function to obtain the explanations from an utterance with their span (tuple of begin and end position)
    :param rawutt: str
    :return: List of (wrongword, correction, span ) triples
    '''
    results = []
    utt = robustexplanationre.sub(r'\1 \2', rawutt)
    matches = explanationre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        correct = match.group(2)
        span = match.span()
        if isvalidword(correct):
            results.append((wrong, correct, span))
    return results



def getreplacements(utt):
    '''
    function to obtain the replacements from an utterance
    :param utt: str
    :return: List of (wrongword, correction) pairs
    '''
    results = []
    matches = replacementre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        correct= match.group(2)
        results.append((wrong, correct))
    return results

def getreplacementswithspan(utt):
    '''
    function to obtain the replacements from an utterance
    :param utt: str
    :return: List of (wrongword, correction, span) triples
    '''
    results = []
    matches = replacementre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        correct= match.group(2)
        span = match.span()
        results.append((wrong, correct, span))
    return results

def getmultiwordreplacementswithspan(utt):
    '''
    function to obtain the replacements from an utterance
    :param utt: str
    :return: List of (wrongword, correction, span) triples
    '''
    results = []
    matches = multiwordreplacementre.finditer(utt)
    for match in matches:
        wrong = match.group(1)
        correct= match.group(2)
        span = match.span()
        results.append((wrong, correct, span))
    return results


def isvalidword(w: str) -> bool:
    '''
    function to determine whether a word is a valid Dutch word
    :param w:
    :return: bool
    '''
    if known_word(w):
        return True
    elif w in punctuationsymbols:
        return True
    elif w in validwords:
        return True
    else:
        return False

# functions to determine the nature of a line in a CHAT file
def ismetadata(line):
    result = line != "" and line[0] == '@'
    return result

def isutterance(line):
    result = line != '' and line[0] == '*'
    return result

def iscontinuation(line):
    result = line != '' and line[0] == '\t'
    return result

def isdependenttier(line):
    result = line != '' and line[0] == '%'
    return result

def isend(line):
    result = line.lower().startswith('@end')
    return result

def getchatdata(infilename):
    headerdata, utterances, ends = getallchatdata(infilename, exclude=isdependenttier)
    return headerdata, utterances

def getallchatdata(infilename, exclude=None):
    '''
    Function to parse a CHAT (.cha) file and return a tuple consisting of the headerdata and a list of utterances
    All lines other than headerdata or utterances are left out
    :param infilename:
    :return: Tuple[headerdata:List[str], utterances:List[str]]
    '''
    headerdata = []
    utterances = []
    ends = []
    previousisutt, previousismeta, previousisdeptier, noprevious, previousisend, previousisother = 0, 1, 2, 3, 4, 5
    state = noprevious
    with open(infilename, 'r', encoding='utf8') as infile:
        for line in infile:
            if exclude is None or (exclude is not None and not exclude(line)):
                if state == previousisend:
                    print(f'Line(s) after @End: {line}')
                    break
                if isend(line):
                    state = previousisend
                    ends.append(line)
                elif ismetadata(line):
                    headerdata.append(line)
                    state = previousismeta
                elif isutterance(line):
                    utterances.append(line)
                    state = previousisutt
                elif isdependenttier(line):
                    utterances.append(line)
                    state = previousisdeptier
                elif iscontinuation(line):
                    if state == previousisutt:
                        newlast = utterances[-1][:-1] + space + line
                        utterances = utterances[:-1] + [newlast]
                    elif state == previousismeta:
                        newlast = headerdata[-1][:-1] + space + line
                        headerdata = headerdata[:-1] + [newlast]
                    elif state == previousisdeptier:
                        newlast = utterances[-1][:-1] + space + line
                        utterances = utterances[:-1] + [newlast]

                    elif state == previousisother:
                        pass
                    else:
                        print('Unexpected configuration')
                        print(line)
                else:
                    state = previousisother
        return headerdata, utterances, ends

def gettargetspeaker(metadata):
    '''
    function to obtain the target speaker as specified in the metadata
    :param metadata: List[str]
    :return: speakercode: str
    '''
    for line in metadata:
        if line.lower().startswith('@participants:'):
            participantstr = line[len('@participants:'):]
            participants = participantstr.split(',')
            for participant in participants:
                partprops = participant.split()
                if 'child' in participant.lower():
                    result = partprops[0]
                    return result
    result = 'CHI'
    return result

def getchildage(targetspeaker: str, metadata):
    for line in metadata:
        if line.startswith('@ID'):
            linebody = getbody(line)
            lineparts = linebody.split('|')
            if lineparts[2] == targetspeaker:
                return lineparts[3]
    return 'notfound'


def getspeaker(utt):
    '''
    function to obtain the speaker of an utterance
    :param utt: str
    :return: speakercode: str
    '''
    endspk = utt.find(':')
    result = utt[1:endspk]
    return result

def getnoncompletions(line):
    '''
    function to obtain a list of tuples (wrongword, correction) for the noncompletions in a line
    :param line: str
    :return: List[Tuple[wrongword:str, correction;str]]
    '''
    words = tokenize(line)
    noncompletions = [(undononcompletion(w), applynoncompletion(w)) for w in words if noncompletionre.search(w)]
    return noncompletions

def getnoncompletionswithspan(line):
    '''
    function to obtain a list of tuples (wrongword, correction, span) for the noncompletions in a line
    :param line: str
    :return: List[Tuple[wrongword:str, correction;str]]
    '''
    results = []
    matches = uttnoncompletionre.finditer(line)
    for match in matches:
        wrong = undononcompletion(match.group())
        correct= applynoncompletion(match.group())
        span = match.span()
        results.append((wrong, correct, span))
    return results





def getcontext(utterances, uttno, contextsize, targetspeaker, cond):
    '''
    function to obtain the context of the utterance at index *uttno* in the list of *utterances*,
    given a *contextsize* and a targetspeaker.

    :param utterances: list of utterances
    :param uttno: index of the utterance in *utterances* for which the context is determined
    :param contextsize: integer: the number of utterances before (if negative) or after (if positive) that must be in the context
    :param targetspeaker: speaker code: str,
    :param cond: function that takes 2 parameters: utterance (str), and targetspeaker(str) and yields bool
    :return: context: List[str]

    The cond parameter can be used for a function that imposes restrictions on a context utterance, e.g.,
    that the context utterance must be an utterance for speakers other than the target speaker.
    '''
    lutterances = len(utterances)
    newcontext = []
    if contextsize < 0:
        base = -1
    else:
        base = +1
    counter = base
    candid = uttno + counter
    while len(newcontext) < abs(contextsize) and candid < lutterances and candid >= 0:
        candid = uttno + counter
        if candid >= 0 and candid < lutterances:
            cand = utterances[candid]
            if cond(cand, targetspeaker):
                newcontext.append(cand)
        counter += base

    return newcontext

def getbodystart(line: str) -> int:
    start = line.find(tab)
    if start == -1:
        start = line.find(colon)
    result = start + 1
    return result

def getbody(line: str) -> str:
    bodystart = getbodystart(line)
    result = line[bodystart:]
    return result

def countwords(utt):
    tokens = tokenize(utt)
    result = len(tokens)
    return result


def getcontext2(utterances: List[str], uttno: int, contextsize: int, targetspeaker: str, cond, maxcount: int) -> List[str]:
    '''
    function to obtain the context of the utterance at index *uttno* in the list of *utterances*,

    The cond parameter can be used for a function that imposes restrictions on a context utterance, e.g.,
    that the context utterance must be an utterance for speakers other than the target speaker.
    '''
    lutterances = len(utterances)
    newcontext = []
    wordcount = 0
    if contextsize < 0:
        base = -1
    else:
        base = +1
    counter = base
    candid = uttno + counter
    while len(newcontext) < abs(contextsize) and candid < lutterances and candid >= 0 and wordcount < maxcount:
        candid = uttno + counter
        if candid >= 0 and candid < lutterances:
            cand = utterances[candid]
            candbody = getbody(cand)
            cleancand, _ = mycleantext(candbody, repkeep=False)
            cleancandwc = countwords(cleancand)
            if cond(cand, targetspeaker) and wordcount <= maxcount:
                newcontext.append(cleancand)
                wordcount += cleancandwc
        counter += base

    return newcontext


def excludetargetspeaker(utt, targetspeaker) -> bool:
    candspeaker = getspeaker(utt)
    return candspeaker != targetspeaker

def tokenizecontext(context):
    '''
    function to tokenize the context, i.e. to tokenize each utterance in the context, and add each tokenized utterance to the result list.

    :param context: List[str]
    :return: List[List[str]]
    '''
    result = []
    for el in context:
        uttstart = el.find('\t') + 1
        tokenizedel = tokenize(el[uttstart:])
        result.append(tokenizedel)
    return result

def tokenize(rawutt):
    '''
    Very primitive tokenization function. Interpunction symbols are split of from words by space
    and then tokenization is simply done on the basis of whitespace

    :param rawutt: str
    :return: List[str]
    '''
    utt = interpunctre.sub(r'\1  \2', rawutt)
    words = utt.split()
    return words


def undononcompletion(word):
    '''
    function to undo a noncompletion, e.g. *(s)laap* is turned into *laap*.

    :param word: str
    :return: str
    '''
    inword = word
    outword = ''
    while True:
        outword = noncompletionre.sub(r'\1\3', inword)     #  iterate for there may be # multiple occurrences
        if outword == inword:
            return outword
        else:
            inword = outword
    return outword

def applynoncompletion(word):
    '''
    function to apply a noncompletion, e.g. *(s)laap* is turned into *slaap*.

    :param word:
    :return:
    '''
    inword = word
    outword = ''
    while True:
        outword = noncompletionre.sub(r'\1\2\3', inword)     #  iterate for there may be # multiple occurrences
        if outword == inword:
            return outword
        else:
            inword = outword
    return outword

def occursin(wrd, tokenizedcontext):
    '''
    function to check whether *wrd* occurs in *tokenizedcontext*.

    :param wrd: str
    :param tokenizedcontext: List[List[str]]
    :return: bool
    '''
    for utt in tokenizedcontext:
        if wrd in utt:
            return True
    return False

def undocorrection(word, correction, correctiontype):
    '''
    Function to undo a *correction* for a *word*, given a *correctiontype*.
    For noncompletiontype the correction can still contain roundbrackets (), so the function undononcompletion is applied.
    For the other two types, the function is trivial.

    :param word: str
    :param correction: str
    :param correctiontype: CorrectionType (int)
    :return: str
    '''
    if correctiontype == noncompletiontype:
        result = undononcompletion(correction)
    elif correctiontype == replacementtype:
        result = word
    elif correctiontype == explanationtype:
        result = word
    return result

def applycorrection(word, correction, correctiontype):
    '''
    Function to undo a *correction* for a *word*, given a *correctiontype*.
    For noncompletiontype the correction can still contain roundbrackets (), so the function applynoncompletion is applied.
    For the other two types, the function is trivial.

    :param word: str
    :param correction: str
    :param correctiontype: CorrectionType (int)
    :return: str
    '''
    if correctiontype == noncompletiontype:
        result = applynoncompletion(correction)
    elif correctiontype == replacementtype:
        result = correction
    elif correctiontype == explanationtype:
        result = correction
    return result


def treatcorrections(correctionpairs, utterances, utterance, uttno, targetspeaker, correctiontype, infullname):
    '''

    :param correctionpairs: List[Tuple[str,str]]
    :param utterances: List[str]
    :param utterance: str
    :param uttno: int
    :param targetspeaker: SpeakerCode (str)
    :param correctiontype: CorrectionType (int)
    :param infullname: FileName (str)
    :return: None

    The function *treatcorrections* deals with the correctionpairs that gave been found in *utterance*,
    which is the *uttno* th utterance in *utterances*.
    For this utterance it determines the preceding context and the context following, and tokenizes these.
    It updates a frequencydictionary for each correctiontype of (wrongword, correction) pairs (*correctiondict*),
    and does so too for corrections in the preceding context (*correctionprevdict*) and for corrections in the context
    following (*correctionpostdict*).

    It updates the variable *correctioncontexts*, which consists of tuples (infullname, correctword, correctioncontext),
    where correctioncontext is the utterance being dealt with together with its preceding or following context
    (in the right order) where the correction occurs in the context.

    It also updates the frequency dictionary of wordlengths (*lengthfreqdict*)
    '''
    global correctionprevcounter, correctionpostcounter, correctionnoprevcounter, correctionnopostcounter
    # cond = excludetargetspeaker
    cond = lambda x, y:  True
    if correctionpairs != []:
        prevcontext = getcontext(utterances, uttno, prevcontextsize, targetspeaker, cond)

        tokenizedprevcontext = tokenizecontext(prevcontext)
        postcontext = getcontext(utterances, uttno, postcontextsize, targetspeaker, cond)
        tokenizedpostcontext = tokenizecontext(postcontext)
        for correctionpair in correctionpairs:
            wrongword, correctword = correctionpair
            if not isvalidword(wrongword):
                correctiondict[correctiontype][(wrongword, correctword)] += 1
                if occursin(correctword, tokenizedprevcontext):
                    correctionprevcounter += 1
                    correctionprevdict[correctiontype][(wrongword, correctword)] += 1
                    correctioncontext = list(reversed(prevcontext)) + [utterance]
                    correctioncontexts.append((infullname, correctword, correctioncontext))
                else:
                    correctionnoprevcounter += 1
                if occursin(correctword, tokenizedpostcontext):
                    correctionpostcounter += 1
                    correctionpostdict[correctiontype][(wrongword, correctword)] += 1
                    correctioncontext = [utterance] + postcontext
                    correctioncontexts.append((infullname, correctword, correctioncontext))
                else:
                    correctionnopostcounter += 1
                lengthfreqdict[len(correctword)] += 1


def gettiername(line):
    index = line.find(tab)
    if index != -1:
        tiername = line[:index+1]
    else:
        tiername = ''
    return tiername
