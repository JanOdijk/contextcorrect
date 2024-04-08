# The module contextcorrect
Software to predict the correct word for a word wrongly pronounced by a child and accordingly transcribed. It is specifically targeted at dataseta consisting of files in the CHAT format (.cha extension). 
See https://childes.talkbank.org/, esp. https://talkbank.org/manuals/CHAT.pdf.  

Warning: this software was never intended for use by others so has no features to facilitate use by others.

# Dependencies

The following packages are required:
* transformers
* TensorFlow (or PyTorch)
* sastadev

They can be installed in the usual way

```
pip install transformers
pip install tensorflow
pip install sastadev
```

# Basic usage

## What it does
By running the program it will find occurrences of replacements (CHAT code [: ]),
single word explanations (CHAT code [=  ]) and non-completions of words (CHAT code: parentheses), make a prediction (or no prediction) using BERTje and or the context for the word that was replaced, explained or incomplete, and check whether the predictions made are correct.

The predictions are made only for words with a certain mimimal length, which is determined by a parameter. See the section on parameters.

The predictions are made for a word (the target word) in a specific utterance, which we call the target utterance. This target utterance has been pronounced by the target speaker. The predictions are made on the basis of a number of factors.

The *context* is a number of utterances preceding and following  the target utterance. The size of the context is determined by a parameter (see the section on parameters ). Only utterances with a speaker different from the target speaker are part of the context.

Multiple words are predicted by BERTje.  The number of words predicted is determined by a parameter (see the section on parameters),

Words can also be predicted purely on the basis of the context. Each word that occurs in the context is a candidate.

The predicted words are evaluated in terms of their resemblance to the target word. The comparison is done using relative (or normalized) edit distance (*red*).  If the  relative edit distance is too large, the predicted word is discarded. If all predicted words are discarded, the software makes *no* prediction. The allowed deviance is determined by a parameter (see the section on parameters)

## How to run it
One can run the software on a dataset in a folder as follows:

python contextcorrect.py -c <path-to-folder> 

## The output generated

@@to be added@@
## Help
This is the output of:

python contextcorrect.py -h

```
Options:
  -h, --help            show this help message and exit
  -c CHILDESPATH, --childes=CHILDESPATH
                        Path to the folder containing the CHILDES data
```


# Parameters

The software assumes specific values for a number of parameters. If you want different values you have to set them in the module *parameters*. 

The following parameters exist:

* *topk*: number of predictions made by BERTje. Default value = 5
* *maxcontextwordsize*: the minimal number of words that the preceding or following context must contain. Default: 15
* *redthreshold* The computed relative edit distance must be smaller than this value. Default value = .5
* *minimumwordlength*: predictions are made only for words with a length >= this parameter. Default value = 4.

# BERTje Memory

Computers are slow, but we want them to do  lot for us. BERTje in particular is very slow. For this reason we try to minimise the use of BERTje as much as possible. 

The module *bertje* sets up a dictionary *bertjememory*. It does so by reading the file *bertjememory.json* in the folder *data/memory*. If this file does not exist, *bertjememory* will initially be an empty dictionary.

*bertjememory* is a Python dictionary with strinsg as keys and a list of BERTje results as values. The list has maximally *topk* (see parameters) elements. Each BERTje result is  a dictionary with 4 items:

* key = 'score': value represents the score BERTje assigns to this result (type: float). The list of results is sorted by this score from highest to lowest
* key ='token': value is the BERTJe internal token identifier (type: int) 
* key = 'token_str': the predicted word (type: str)
* key = 'sequence': the input string with the mask replaced by the predicted word (type: str)

For each application of *getbertjeresults*, it first looks  whether the input string is  in *bertjememory*. If so, this result is used. If not,  BERTje is used and the  results found are stored in  *bertjememory* and the dictionary is stored in a json file after the program has finished. (actually each time there is a change of *bertjememory* so that we also have this memory if this run would crash or unexpectedly stop for other reasons)

The key of *bertjememory* is the string containing the preceding context, the target utterance and the context following.
The memory wil give wrong results if the *topk* parameter is adapted (especially if it is increased; if it is decreased one will still get 5 results but one can then select the ones one need ). The topk parameter value should be made part of the key (which is not so difficult but still has to be done). 

If one changes the context, the memory will give no results because the results have not been computed for the input string before but *bertjememory* is still valid and will be extended with new results.

We have run *contectcorrect* on all Dutch CHILDES data, and the *bertjememory.json* file contains results for this, but of course only for target words that are replacements, explanations or non-completions of words.

If one uses *getbertjeresults* to obtain results from Bertje, one does not have to worry about *bertjememory*. However, if you want to define new functions to obtain results, the following functions are relevant:

* *getbertjememory*: creates *bertjememory* by reading the *data/memory/bertjememory.json* file
* *storebertjememory*: stores a memory dictionary in a file. It does so immediately (no waiting until the program finished)

# Other usages

The module contextcorrect.py and other modules can also be imported into one's own program.

The relevant modules to import are

* bertje.py
* contextcorrect.py
* chatfunctions.py
* relativedistance.py

Here is a description of some useful functions.

If you want to deal with CHAT files, you have to read them in and parse them correctly. For this one can use the function *getchatdata* in the *chatfunctions* module.

If you have read CHAT data, the header contains metadata. Of specific interest are the target speaker (the  child that is being investigated), which can be obtained by the function *gettargetspeaker*. The child's age can be obtained by the function *getchildage*.

In the chatdata you select a target utterance, e.g. an utterance that contains a word that is not a word of the Dutch language, or a word of the Dutch language that young children are not expected to know. You can use the function *isvalidword* from the module *chatfunctions* for this, but it has limitations (no diminutives, e.g.), so you may want to use other sources.

Once a target utterance is selected, you will want to have a context. This can be obtained using the function *getcontext2* from the module *chatfunctions*.

If you have a target utterance with the target word replaced by a mask and a context, you will want to turn this into a string that BERTje can deal with. This can be done by the function *getfullcontext* in the module *contextcorrect*

Next you may want to obtain the predictions by BERTje. This can be done by the function *getbertjeresults* in the module *bertje*. This will yield a list of BERTJe results, where each BERTje result is a dictionary with 4 elements: *score*, *token*, *token_str*, *sequence*. See the section on BERTje memory.

Two other functions  from the moduke *bertje* may be useful: 

* *getbertjemaskwords*: yields a list of predicted words (from most to least plausibe according to BERTje)
* *getbertjemaskwordswithscores*: yields a list of tuples (predictedword: str, score: float) sorted by score highest to lowest

You may want to compare the results obtained with the target word. For this you can use the function *getclosedmatches* from the module *contextcorrect*. It will return those words for which the relative edit distance is smaller than the *redthreshold* parameter.

A more detailed description of each of these functions can be obtained from the doc string with each function. 

