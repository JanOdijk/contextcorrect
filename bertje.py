from typing import Dict, List, Tuple
from transformers import pipeline
import shutil
import os
import json

space = ' '

topkvalue = 5

pipe = pipeline('fill-mask', model='GroNLP/bert-base-dutch-cased', top_k=topkvalue)

bertjememoryfilenamebase = 'bertjememory'
bertjememoryfilenameext = '.json'
bertjememoryfilename = bertjememoryfilenamebase + bertjememoryfilenameext
memoryfolder = './data/memory'
bertjememoryfullname = os.path.join(memoryfolder, bertjememoryfilename)

# see https://huggingface.co/docs/transformers/v4.30.0/en/main_classes/pipelines#transformers.FillMaskPipeline for
# more documentation on the FillMaskPipeline

def getbertjememory(bmfilename: str) -> Dict[str, List[dict]]:
    if os.path.exists(bmfilename):
        with open(bmfilename, 'r', encoding='utf8') as bmfile:
            bmmemory = json.load(bmfile)
        shutil.copy(bmfilename, f'{bmfilename}_previous.txt')
    else:
        bmmemory = {}
    # we immediately store it in the file again
    storebertjememory(bmmemory, bmfilename)
    return bmmemory

def storebertjememory(bm, bmfilename: str):
    with open(bmfilename, 'w', encoding='utf8') as bmfile:
        json.dump(bm, bmfile, indent=4)
        bmfile.flush()

# initialize bertjememory
bertjememory = getbertjememory(bertjememoryfullname)


def getbertjemaskwords(maskedutt: str) -> List[str]:
    """
    :param maskedutt: a string containing a mask
    :return: a list of words as prediced by BERTje, sorted by score (highest to lowest).
    This function uses *getbertjeresults*.
    """
    results = []
    bertjeresults = getbertjeresults(maskedutt)
    for res in bertjeresults:
        newresult = res['token_str']
        results.append(newresult)
    return results


def getbertjemaskwordswithscores(maskedutt: str) -> List[Tuple[str, float]]:
    """

    :param maskedutt: string containing a mask
    :return: a list of typles (predictedword: str, score: float) sorted by score highest to lowest
    This function uses *getbertjeresults*.
    """
    results = []
    bertjeresults = getbertjeresults(maskedutt)
    for res in bertjeresults:
        newresult = (res['token_str'], res['score'])
        results.append(newresult)
    return results



def getscoresfortargetwords(maskedutt: str, targets:List[str]) -> List[Tuple[str, float]]:
    pipe = pipeline('fill-mask', model='GroNLP/bert-base-dutch-cased', top_k=topkvalue, targets=targets)
    results = []
    for res in pipe(maskedutt):
        newresult = (res['token_str'], res['score'])
        results.append(newresult)
    return results

def getbertjeresults(bertjeinput: str) -> List[dict]:
    """
    Note that if the bertjememory file is present it will obtain its results from this bertje memory
    if it contains *bertjenput* as key, and compute it otherwise.
    :param bertjeinput:  string containing the preceding context, the masked target utterance, and the context
    that follows the target utterance
    :return:  List of BERTje results
    """
    if bertjeinput in bertjememory:
        results = bertjememory[bertjeinput]
    else:
        results = pipe(bertjeinput)
        bertjememory[bertjeinput] = results
        storebertjememory(bertjememory, bertjememoryfullname)
    return results

if __name__ == '__main__':
    maskedutt =  'we gaan rijen. ja. uur rije he? wat is er met een flamingo? heb jij een flamingo gezien? ' \
                 'wanneer heb je dan een flamingo gezien? [MASK] nu is de appelsap op. nou krijg je niet meer. ' \
                 'nee. en de taperecorder kan je niet hebben. moet Thomas niet op het potje zitten?'

    for res in pipe(maskedutt):
        print(res['sequence'])
        print(res['token_str'])
