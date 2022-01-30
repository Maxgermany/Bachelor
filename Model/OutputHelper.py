import Data.Scripts.DatabaseHelper as DatabaseHelper
import re
import time
import json

def createAndWriteFileNewNew(fileName):

    allDataPoints = DatabaseHelper.getAllDataPointsWithBelongingInformations(percent=0.7)
    groupedDataPoints = {}
    groupedDataPointsList = []

    for dataPoint in allDataPoints:
        if dataPoint[1] in groupedDataPoints.keys():
            attributeName = dataPoint[3].replace("BLACK_", "").replace("WHITE_", "")
            colorNumber = 0
            if "BLACK" in dataPoint[2]:
                colorNumber = 1
            if attributeName in groupedDataPoints[dataPoint[1]]["box_score"].keys():
                groupedDataPoints[dataPoint[1]]["box_score"][attributeName][colorNumber] = dataPoint[4]
            else:
                groupedDataPoints[dataPoint[1]]["box_score"][attributeName] = {}
                groupedDataPoints[dataPoint[1]]["box_score"][attributeName][colorNumber] = dataPoint[4]

        else:
            groupedDataPoints[dataPoint[1]] = {}
            attributeName = dataPoint[3].replace("BLACK_", "").replace("WHITE_", "")
            colorNumber = 0
            if "BLACK" in dataPoint[2]:
                colorNumber = 1
            groupedDataPoints[dataPoint[1]]["box_score"] = {}
            groupedDataPoints[dataPoint[1]]["box_score"][attributeName] = {}
            groupedDataPoints[dataPoint[1]]["box_score"][attributeName][colorNumber] = dataPoint[4]

            if dataPoint[8] == "½-½":
                result = "Draw"
            elif dataPoint[8] == "1-0":
                result = "White"
            elif dataPoint[8] == "0-1":
                result = "Black"
            else:
                result = "Unknown"
            groupedDataPoints[dataPoint[1]]["game_result"] = result
            groupedDataPoints[dataPoint[1]]["summary"] = re.findall(r"[\w']+|[.,!?;]", dataPoint[7])

    for key in groupedDataPoints.keys():
        groupedDataPointsList.append(groupedDataPoints[key])

    file = open(fileName, "w")
    json.dump(groupedDataPointsList, file, indent=4)
    file.close()

def createAndWriteFileNew(filename):
    startTime = time.time()
    tempTime = time.time()
    outputString = "["

    allDataPoints = DatabaseHelper.getAllDataPointsWithBelongingInformations()

    groupedDataPoints = {}

    for dataPoint in allDataPoints:
        if dataPoint[1] in groupedDataPoints.keys():
            groupedDataPoints[dataPoint[1]]["datapoints"].append({
                "entityName": dataPoint[2],
                "attributeName": dataPoint[2].upper() + "_" + dataPoint[3],
                "attributeValue": dataPoint[4]
            })
        else:
            groupedDataPoints[dataPoint[1]] = {}
            groupedDataPoints[dataPoint[1]]["datapoints"] = []
            groupedDataPoints[dataPoint[1]]["datapoints"].append({
                "entityName": dataPoint[2],
                "attributeName": dataPoint[2].upper() + "_" + dataPoint[3],
                "attributeValue": dataPoint[4]
            })
            groupedDataPoints[dataPoint[1]]["comment"] = dataPoint[7]
            groupedDataPoints[dataPoint[1]]["result"] = dataPoint[8]

    file = open("anotherTestFile.json", "w")
    json.dump(groupedDataPoints, file, indent=4)
    file.close()

    j = 0

    for commentId in groupedDataPoints:

        if j % 1000 == 0:
            print(str(j) + " - " + str(time.time() - tempTime))
            tempTime = time.time()

        j += 1

        gameResult = groupedDataPoints[commentId]["result"]
        commentParts = re.findall(r"[\w']+|[.,!?;]", groupedDataPoints[commentId]["comment"])
        scoreDic = {}

        outputString += "{"

        outputString += '"box_score": {'

        for dataPoint in groupedDataPoints[commentId]["datapoints"]:
            attributeName = dataPoint["attributeName"].replace("BLACK_", "").replace("WHITE_", "")
            colorNumber = 0
            if "BLACK" in dataPoint["attributeName"]:
                colorNumber = 1
            if attributeName in scoreDic.keys():
                scoreDic[attributeName][colorNumber] = dataPoint["attributeValue"]
            else:
                scoreDic[attributeName] = ["", ""]
                scoreDic[attributeName][colorNumber] = dataPoint["attributeValue"]

        for key in scoreDic.keys():
            outputString += '"' + key + '": {'
            for i in range(len(scoreDic[key])):
                outputString += '"' + str(i) + '": "' + scoreDic[key][i] + '", '
            outputString = outputString[:-2]
            outputString += '}, '

        outputString = outputString[:-2]

        outputString += "}, "

        outputString += '"summary": ['

        for commentPart in commentParts:
            outputString += '"' + commentPart + '", '

        outputString = outputString[:-2]

        outputString += '], '

        outputString += '"game_result": "'

        if gameResult == "½-½":
            outputString += "Draw"
        elif gameResult == "1-0":
            outputString += "White"
        elif gameResult == "0-1":
            outputString += "Black"
        else:
            outputString += "Unknown"

        outputString += '"'
        outputString += "}, "

    outputString = outputString[:-2]

    outputString += "]"

    file = open(filename, "w")
    file.write(outputString)
    file.close()

    print("Whole-Time: " + str(time.time() - startTime))

def createAndWriteFile(fileName, commentId):
    dataPoints = DatabaseHelper.getAllDataPointsOfComment(commentId)
    comment = DatabaseHelper.getCommentById(commentId)
    gameId = comment[1]
    game = DatabaseHelper.getGame(gameId)
    gameResult = game[7]
    commentParts = re.findall(r"[\w']+|[.,!?;]", comment[2])
    print(comment)
    print(dataPoints)
    scoreDic = {}

    outputString = "["
    outputString += "{"

    outputString += '"box_score": {'

    #loop over all dataPoints
    for dataPoint in dataPoints:
        if dataPoint[3].replace("BLACK_", "").replace("WHITE_", "") in scoreDic.keys():
            scoreDic[dataPoint[3].replace("BLACK_", "").replace("WHITE_", "")].append(dataPoint[4])
        else:
            scoreDic[dataPoint[3].replace("BLACK_", "").replace("WHITE_", "")] = [dataPoint[4]]

    for key in scoreDic.keys():
        outputString += '"' + key + '": {'
        for i in range(len(scoreDic[key])):
            outputString += '"' + str(i) + '": "' + scoreDic[key][i] + '", '
        outputString = outputString[:-2]
        outputString += '}, '

    outputString = outputString[:-2]

    outputString += "}, "

    outputString += '"summary": ['

    for commentPart in commentParts:
        outputString += '"' + commentPart + '", '

    outputString = outputString[:-2]

    outputString += '], '

    outputString += '"game_result": "'

    if gameResult == "½-½":
        outputString += "Draw"
    elif gameResult == "1-0":
        outputString += "White"
    elif gameResult == "0-1":
        outputString += "Black"
    else:
        outputString += "Unknown"

    outputString += '"'

    outputString += "}"
    outputString += "]"

    print(outputString)

    #Create file and write outputString in file
    file = open(fileName, "w")
    file.write(outputString)
    file.close()

createAndWriteFileNewNew("train.json")



