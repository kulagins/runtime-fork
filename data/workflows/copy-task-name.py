import pathlib
import os
import in_place

directory = os.fsencode("./")
maxMem = 192
maxTime = 1000
maxInput = 500
s = set()
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".dot"):
        print(filename)
        with in_place.InPlace(filename) as file:
            for line in file:
                print(line)
                if "[task= in line:
                    line1 = line
                    taskName = line.split("\t")[1]
                    taskDescription = line.split("\t")[2]
                    indexOfstart = 0
                    try:
                        indexOfstart = taskDescription.index('<')
                    except:
                        file.write(line)
                        continue
                    indexOfEnd = taskDescription.index('>')
                    taskDescription = taskDescription[:indexOfstart] + taskName + taskDescription[indexOfEnd + 1:]
                    line = "\t" + taskName + "\t" + taskDescription
                file.write(line)
            file.close()

        # print(os.path.join(directory, filename))
        # print(directory)
        # print(filename)
        # text_file = open(filename, 'r')
        # read_file = text_file.read()
        # word_list = read_file.split()
        # uniquewords = set(word_list)
        # wfname = filename.split("-")[0]
        # uniquewords = filter(lambda word: "x" in word, uniquewords)
        #  for word in list(uniquewords):
        #     if "x" in word:
        #        uniquewords.discard(word)
        # with open('c2_pseudo.csv', 'a') as f:
        #   for word in list(uniquewords):
        #        if word[-1] == ";":
        #           word = word[:-1]
        #       f.write("c2,")#Machine

        continue
    else:
        continue

print(s)
