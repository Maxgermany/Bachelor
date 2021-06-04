from os import walk
import os
import json
from langdetect import detect

def sortFilesInFolder():
    _, _, filenames = next(walk("../Gameknot/JSON/"))

    for filename in filenames:
        if filename[0] == " ":
            os.rename("../Gameknot/JSON/" + filename, "../Gameknot/JSON/space/" + filename)
        else:
            if not os.path.exists("../Gameknot/JSON/" + filename[0] + "/"):
                os.mkdir("../Gameknot/JSON/" + filename[0] + "/")
            os.rename("../Gameknot/JSON/" + filename, "../Gameknot/JSON/" + filename[0] + "/" + filename)


def createCorpus():

    folders = os.listdir("../Gameknot/JSON/")

    with open("../Gameknot/corpus.txt", "w+", encoding="utf-8") as file:
        for folder in folders:
            _, _, filenames = next(walk("../Gameknot/JSON/" + folder + "/"))
            for filename in filenames:
                with open("../Gameknot/JSON/" + folder + "/" + filename, "r", encoding="utf-8") as jsonFile:
                    content = json.load(jsonFile)
                    for move in content["moves"]:
                        file.write((content["moves"][move] + " ").replace("\n", " "))

                    file.write("\n")

def preprocessCorpus():

    processingFunctions = ["lowerCase", "filterOtherLanguages"]

    with open("../Gameknot/corpus.txt", "r+", encoding="utf-8") as file:
        content = file.read()

    for function in processingFunctions:
        content = eval(function + "(content)")
        with open("../Gameknot/corpus" + function + ".txt", "w+", encoding="utf-8") as file:
            file.write(content)

def lowerCase(content):
    return content.lower()

def filterOtherLanguages(content):
    lines = content.split("\n")

    contentTemp = ""

    for line in lines:
        if len(line) > 10:
            try:
                lang = detect(line)
                with open("../Gameknot/corpus" + lang.upper() + ".txt", "a+", encoding="utf-8") as file:
                    file.write(line)
                    file.write('\n')
                if lang == 'en':
                    contentTemp += line
                    contentTemp += "\n"
            except:
                with open("../Gameknot/corpusExcept.txt", "a+", encoding="utf-8") as file:
                    file.write(line)
                    file.write("\n")
    return contentTemp

