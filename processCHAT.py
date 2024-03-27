from sastadev.cleanCHILDEStokens import cleantext
from sastadev.chatundo import chatundo
from sastadev.correcttreebank import isvalidword
from sastadev.basicreplacements import basicreplacements


utterances = [
             "<dan gaat ie [: hij]> [/] dan gaat ie [: hij] huilen.",
    "dan komt ie [: hij] <een ri(dder)> [/] een ridder tegen.",
     "omdat [/] omdat de bal in het water ligt.",
      "de gieter &eh vult ze vol (.) met water."]

cleanedutterances = [(utt, chatundo(utt), cleantext(utt, repkeep=False)) for utt in utterances]

for utt, undoutt, cleanuttmd in cleanedutterances:
    print(f'{utt}\n{undoutt}\n{cleanuttmd}\n')

for utt, undoutt, cleanuttmd in cleanedutterances:
    cleanutt = cleanuttmd[0]
    metadata = cleanuttmd[1]
    print(f'{utt}\n{cleanutt}')
    for meta in metadata:
        print(meta)

rawwords = ['apparaatje', 'ehm', 'heu', 'ri', 'zn', 'één', 'één', 'één', 'hé', 'drvan', 'ko', 'indiaan', 'indiaan', 'indiaan']

for rawword in rawwords:
    if not isvalidword(rawword):
        print(f'NO: {rawword}')

wrongwords = ['as', 'hie', 'nie', 'amaal']
for w in wrongwords:
    cw = basicreplacements[w]
    print(w, cw)


