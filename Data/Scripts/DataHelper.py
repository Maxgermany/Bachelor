from os import walk
import json

def createCorpus():
    _, _, filenames = next(walk("../GameknotJSON"))
    filenames.remove("links.json")

    file = open("../GameknotJSON/corpus.txt", "w+", encoding="utf-8")

    for filename in filenames:
        jsonFile = open("../GameknotJSON/" + filename, "r", encoding="utf-8")
        content = json.load(jsonFile)
        for move in content["moves"]:
            file.write(content["moves"][move] + " ")
        jsonFile.close()

    file.close()
