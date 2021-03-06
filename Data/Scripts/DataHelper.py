from os import walk
import os
import json
from langdetect import detect
import re
import Data.Scripts.DatabaseHelper as DatabaseHelper
from collections import defaultdict
from flair.data import Sentence
from flair.models import SequenceTagger


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

def getFrequencyOfLanguages():

    folders = os.listdir("../Gameknot/JSON/")

    languages = {}
    counter = 0

    for folder in folders:
        _, _, filenames = next(walk("../Gameknot/JSON/" + folder + "/"))
        for filename in filenames:
            with open("../Gameknot/JSON/" + folder + "/" + filename, "r", encoding="utf-8") as jsonFile:
                content = json.load(jsonFile)
                comment = ""
                for move in content["moves"]:
                    comment += content["moves"][move] + " "
                try:
                    lang = detect(comment)
                    if lang in languages:
                        languages[lang] += 1
                    else:
                        languages[lang] = 1
                except:
                    continue

                counter += 1

    print(languages)
    print(counter)


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
                    records.append((gameId, content["moves"][move], 'initial', move))
                DatabaseHelper.writeManyMoveCommentPairsIntoDB(records)


def filterShortMovesInDB():
    pairs = DatabaseHelper.getMoveCommentsPairs()
    finalPairs = []
    for pair in pairs:
        if len(pair[2]) > 10:
            finalPairs.append((pair[1], pair[2], 'shortMoves', pair[4]))
    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)


def filterEnglishMovesInDB():
    pairs = DatabaseHelper.getMoveCommentsPairs(stage='shortMoves')
    finalPairs = []
    for pair in pairs:
        try:
            lang = detect(pair[2])
            if lang == 'en':
                finalPairs.append((pair[1], pair[2], 'englishMoves', pair[4]))
        except:
            continue

    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)

def lowerMovesInDB():
    pairs = DatabaseHelper.getMoveCommentsPairs(stage='englishMoves')
    finalPairs = []
    for pair in pairs:
        finalPairs.append((pair[1], pair[2].casefold(), 'lowerCase', pair[4]))

    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)

def removeTabsNewLinesAndSpacesInDB():
    pairs = DatabaseHelper.getMoveCommentsPairs(stage='lowerCase')
    finalPairs = []
    for pair in pairs:
        finalPairs.append((pair[1], " ".join(pair[2].split()), 'removeTabsNewLinesAndSpaces', pair[4]))

    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)

def removePairsWithHTMLInDB(stage = 'removeTabsNewLinesAndSpaces'):
    pairs = DatabaseHelper.getMoveCommentsPairs(stage=stage)
    finalPairs = []
    for pair in pairs:
        if "<" not in pair[2]:
            finalPairs.append((pair[1], pair[2], 'removeHTML', pair[4]))
            
    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)
    
def removePairsWithLinksInDB(stage = 'removeHTML'):
    pairs = DatabaseHelper.getMoveCommentsPairs(stage=stage)
    finalPairs = []
    for pair in pairs:
        if "http" not in pair[2]:
            finalPairs.append((pair[1], pair[2], 'removeLinks', pair[4]))
            
    DatabaseHelper.writeManyMoveCommentPairsIntoDB(finalPairs)

def getAllDistinctWordsOfStage(stage = "initial", findWords=[]):
    pairs = DatabaseHelper.getMoveCommentsPairs(stage=stage)
    wordFrequency = defaultdict(int)
    for pair in pairs:
        for word in pair[2].split():
            wordFrequency[word] += 1

    wordFrequency = sorted(wordFrequency.items(), key=lambda item: item[1])

    print(wordFrequency)

    for freq in wordFrequency:
        if freq[0] in findWords:
            print(freq)


def writeNamedEntitiesInDB(stage = "inital"):
    pairs = DatabaseHelper.getMoveCommentsPairs(stage = stage)
    tagger = SequenceTagger.load('ner-fast')
    maxId = DatabaseHelper.getMaxCommentIDFromNamedEntities()
    for pair in pairs:
        if pair[0] < maxId[0]:
            continue
        sentence = Sentence(pair[2])
        tagger.predict(sentence)
        if len(sentence.get_spans('ner')) > 0:
            for entity in sentence.get_spans():
                DatabaseHelper.writeNamedEntitiyIntoDB(pair[0], entity.tag, entity.text)


writeNamedEntitiesInDB("removeLinks")
