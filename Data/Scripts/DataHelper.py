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
    folders = os.listdir("../Gameknot/JSON/")

    file = open("../Gameknot/corpus.txt", "w+", encoding="utf-8")

    for folder in folders:
        _, _, filenames = next(walk("../Gameknot/JSON/" + folder + "/"))
        for filename in filenames:
            jsonFile = open("../Gameknot/JSON/" + folder + "/" + filename, "r", encoding="utf-8")
            content = json.load(jsonFile)
            for move in content["moves"]:
                file.write(content["moves"][move] + " ")
            jsonFile.close()

    file.close()




