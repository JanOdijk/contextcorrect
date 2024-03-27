from sastadev import sastatok
from sastadev.cleanCHILDEStokens import cleantext

from getcontextcorrections import getexplanationswithspan, getreplacementswithspan, getnoncompletionswithspan


def getuttforbertje(utt, span):
    part1 = utt[:span[0]]
    part2 = utt[span[1]:]
    cleanpart1, meta1 = cleantext(part1, repkeep=False)
    cleanpart2, meta = cleantext(part2, repkeep=False)
    result = f'{cleanpart1} [MASK] {cleanpart2}'
    return result

explanationexample = 'Dit s [= is] een mingo [= flamingo]'
print(f'\n***************\n{explanationexample}:\n')
explwithspans = getexplanationswithspan(explanationexample)
for explwithspan in explwithspans:
    print(explwithspan)
    uttforbertje = getuttforbertje(explanationexample, explwithspan[2])
    print(uttforbertje)

replacementexample = 'Dit s [: is] een mingo [: flamingo]'
print(f'\n***************\n{replacementexample}:\n')

replwithspans= getreplacementswithspan(replacementexample)
for replwithspan in replwithspans:
    print(replwithspan)
    uttforbertje = getuttforbertje(replacementexample, replwithspan[2])
    print(uttforbertje)


noncompletionexample = 'Dit (i)s een fla(m)ingo en een olifan(t)'
print(f'\n***************\n{noncompletionexample}:\n')

noncompletionswithspans = getnoncompletionswithspan(noncompletionexample)
for noncompletionwithspan in noncompletionswithspans:
    print(noncompletionwithspan)
    uttforbertje = getuttforbertje(noncompletionexample, noncompletionwithspan[2])
    print(uttforbertje)
