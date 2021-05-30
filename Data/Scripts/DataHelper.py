import re
from os import walk
import os
import json
import string

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
                file.write((content["moves"][move] + " ").replace("\n", " "))
            file.write("\n")
            jsonFile.close()

    file.close()

def preprocessCorpus():

    processingFunctions = ["lowerCase", "filterOtherLanguages"]

    file = open("../Gameknot/corpus.txt", "r+", encoding="utf-8")

    content = file.read()

    file.close()

    for function in processingFunctions:
        content = eval(function + "(content)")
        file = open("../Gameknot/corpus" + function + ".txt", "w+", encoding="utf-8")
        file.write(content)
        file.close()

def lowerCase(content):
    return content.lower()

def filterOtherLanguages(content):
    lines = content.split("\n")

    contentTemp = ""

    file = open("../Gameknot/filteredLines.txt", "w+", encoding="utf-8")

    for line in lines:
        if any(x not in string.printable for x in line):
            file.write(line)
            file.write("\n")
            file.write("-------------------------------------")
            file.write("\n")
        else:
            contentTemp += line
            contentTemp += "\n"

    file.close()

    return contentTemp




