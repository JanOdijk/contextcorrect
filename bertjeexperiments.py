from transformers import pipeline
space = ' '

pipe = pipeline('fill-mask', model='GroNLP/bert-base-dutch-cased', top_k=5)

def shorten(long:str, i:int):
    longlist = long.split()
    shortlist = longlist[i:len(longlist)-i]
    shortstr = space.join(shortlist)
    return shortstr

# see https://huggingface.co/docs/transformers/v4.30.0/en/main_classes/pipelines#transformers.FillMaskPipeline for
# more documentation on the FillMaskPipeline

maskedutt =  'we gaan rijen. ja. uur rije he? wat is er met een flamingo? heb jij een flamingo gezien? ' \
             'wanneer heb je dan een flamingo gezien? [MASK] nu is de appelsap op. nou krijg je niet meer. ' \
             'nee. en de taperecorder kan je niet hebben. moet Thomas niet op het potje zitten?'

for res in pipe(maskedutt):
    print(res['sequence'])
    print(res['token_str'])


for res in pipe('Ik wou dat ik een [MASK] was.'):
    print(res['sequence'])

for res in pipe('deze gaan we [MASK] .'):
    print(res['sequence'])

for res in pipe('deze gaan we [MASK] . die gaan we ook gebruiken , ja . ja . oh , dat zijn nieuwe .'):
    print(res['sequence'])

for res in pipe('moet rij [MASK] kraan'):
    print(res['sequence'])

instr = 'bamme  . jouw bal is dat , ja. 	hier. [MASK]  uit. rajo  uit! de radio is uit ja. en wat voor verhaaltjes heb je nog meer te vertellen?'
for res in pipe(instr):
    print(res['sequence'])
for res in pipe(instr):
    print(res['token_str'])

instr = 'bal mij . jouw bal is dat , ja. 	hier. [MASK]  uit. radio uit! de radio is uit ja. en wat voor verhaaltjes heb je nog meer te vertellen?'
for res in pipe(instr):
    print(res['sequence'])
for res in pipe(instr):
    print(res['token_str'])


instr = 'hier. [MASK]  uit. rajo  uit! '
for res in pipe(instr):
    print(res['sequence'])
for res in pipe(instr):
    print(res['token_str'])

instr = 'hier. [MASK]  uit. radio uit! '
for res in pipe(instr):
    print(res['sequence'])
for res in pipe(instr):
    print(res['token_str'])

longcontextutt = 'ja , die is een beetje te moeilijk voor jou , Saar. deze dan. zullen we deze doen? deze ga jij mij [MASK]. ja , die vind ik een beetje te moeilijk voor jou. deze? nee?'
fulllongresult = ''
for res in pipe(longcontextutt):
    fulllongresult += res['sequence']
    # print(res['token_str'])
    print(res['sequence'])

# shorten the context and see what the results are
shortening = False
if shortening:
    for i in range(10):
        shortercontextutt = shorten(longcontextutt, i)
        fullshorterresult = ''
        for res in pipe(shortercontextutt):
            fullshorterresult += res['sequence']
            print(res['sequence'])
        print('******************')

