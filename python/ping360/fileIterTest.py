import struct, re
class fileReader:
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        with open(self.filename, 'r') as file:
            i=0
            while i<26:
                yield file.read(2)
                i+=1

# reader = fileReader("./python/ping360/tester.txt")

# for char in reader:
#     print(char)

def extract_times(timestamp):
        numerical_strings = re.findall('[0-9][0-9]*', timestamp)
        floats = [float(n) for n in numerical_strings]
        while floats[0] == 0:
             floats.pop(0)
        return floats

print(extract_times("00:00:01:002"))

