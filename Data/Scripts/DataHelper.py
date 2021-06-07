from os import walk
import os
import json
from langdetect import detect
import re
import Data.Scripts.DatabaseHelper as DatabaseHelper

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

def createPGN():

    folders = os.listdir("../Gameknot/JSON/")

    for folder in folders:
        _, _, filenames = next(walk("../Gameknot/JSON/" + folder + "/"))
        if not os.path.exists("../Gameknot/PGN/" + folder + "/"):
            os.mkdir("../Gameknot/PGN/" + folder + "/")
        for filename in filenames:
            with open("../Gameknot/PGN/" + folder + "/" + filename[:-5] + ".pgn", "w+", encoding="utf-8") as pgnFile:
                with open("../Gameknot/JSON/" + folder + "/" + filename, "r+", encoding="utf-8") as jsonFile:
                    content = json.load(jsonFile)
                    pgnFile.write('[Event "' + content["gameName"] + '"]\n')
                    pgnFile.write('[Site "' + content["url"] + '"]\n')
                    pgnFile.write('[Date "??"]\n')
                    pgnFile.write('[Round "1"]\n')
                    pgnFile.write('[White "' + content["players"].split("vs. ")[0][:-1] + '"]\n')
                    pgnFile.write('[Black "' + content["players"].split("vs. ")[1] + '"]\n')
                    pgnFile.write('[Opening "' + content["opening"] + '"]\n\n')

                    for move in content["moves"]:
                        if "..." in move:
                            pgnFile.write(" ".join(move.split(" ")[1:]))
                        else:
                            pgnFile.write(move)
                        pgnFile.write((" {" + content["moves"][move] + "} ").replace("\n", " "))

def writeMovesInDB():
    folders = os.listdir("../Gameknot/JSON/")

    for folder in folders:
        _, _, filenames = next(walk("../Gameknot/JSON/" + folder + "/"))
        for filename in filenames:
            with open("../Gameknot/JSON/" + folder + "/" + filename, "r+", encoding="utf-8") as jsonFile:
                content = json.load(jsonFile)
                gameId = DatabaseHelper.getGameIDFromURL(content["url"])
                records = []
                for move in content["moves"]:
                    for sentence in re.split("[.?!]", content["moves"][move]):
                        records.append((gameId, sentence, 'initial', move))
                DatabaseHelper.writeManyMoveCommentPairsIntoDB(records)

