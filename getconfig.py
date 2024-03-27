from transformers import pipeline
from transformers import BertConfig

config = BertConfig()
print(config)

pipe = pipeline('fill-mask', model='GroNLP/bert-base-dutch-cased')
for res in pipe('Ik wou dat ik een [MASK] was.'):
    print(res['sequence'])

for res in pipe('deze gaan we [MASK] .'):
    print(res['sequence'])

for res in pipe('deze gaan we [MASK] . die gaan we ook gebruiken , ja . ja . oh , dat zijn nieuwe .'):
    print(res['sequence'])

for res in pipe('moet rij [MASK] kraan'):
    print(res['sequence'])

