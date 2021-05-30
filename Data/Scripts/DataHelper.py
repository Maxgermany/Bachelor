from os import walk
import os
import json

def sortFilesInFolder():
    _, _, filenames = next(walk("../Gameknot/JSON/"))

    for filename in filenames:
        if filename[0] == " ":
            os.rename("../Gameknot/JSON/" + filename, "../Gameknot/JSON/space/" + filename)
        else:
            if os.path.exists("../Gameknot/JSON/" + filename[0] + "/"):
                os.rename("../Gameknot/JSON/" + filename, "../Gameknot/JSON/" + filename[0] + "/" + filename)
            else:
                os.mkdir("../Gameknot/JSON/" + filename[0] + "/")
                os.rename("../Gameknot/JSON/" + filename, "../Gameknot/JSON/" + filename[0] + "/" + filename)


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
