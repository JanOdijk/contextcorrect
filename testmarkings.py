from chatfunctions import getnoncompletionswithspan, getnoncompletions, \
    getreplacementswithspan, getreplacements, getexplanationswithspan, getexplanations

testutts = ['fie(t)se(n)', 'fietse(n)', 'dit is een (non)completion, en meer', 'dit is een complet(ion), en meer', 'di tsi een noncom(ple)tion, en meer']

for testutt in testutts:
    results = getnoncompletions(testutt)
    for result in results:
        print(result)

    results = getnoncompletionswithspan(testutt)
    for result in results:
        print(result)