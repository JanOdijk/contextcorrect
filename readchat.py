
from chamd import ChatReader

examplefile = r'D:\Dropbox\various\Resources\CHILDES\VanKampen\VanKampen\laura34.cha'
reader = ChatReader()
chat = reader.read_file(examplefile) # or read_string

for item in chat.metadata:
    print(item)
for line in chat.lines:
    for item in line.metadata:
        print(item)
    print(line.text)