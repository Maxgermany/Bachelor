from bs4 import BeautifulSoup
import requests
import json

def scrapChessGame(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    gameTable = soup.find("table", {"class": "dialog"})

    comments = gameTable.find_all("td", {"style": "vertical-align: top;"})
    moves = gameTable.find_all("td", {"style": "vertical-align: top; width: 20%;"})

    amountPages = getAmountOfPages(gameTable)

    for i in range(1, amountPages):

        page = requests.get(url + "&pg=" + str(i))
        soup = BeautifulSoup(page.content, 'html.parser')

        gameData = soup.find("div", {"style": "padding: 4px 0px; line-height: 150%;"})
        gameData = gameData.text.split("\n")

        gameTable = soup.find("table", {"class": "dialog"})
        commentTemp = gameTable.find_all("td", {"style": "vertical-align: top;"})
        movesTemp = gameTable.find_all("td", {"style": "vertical-align: top; width: 20%;"})

        for comment in commentTemp:
            comments.append(comment)

        for move in movesTemp:
            moves.append(move)

    commentsByMove = {}

    for i in range(0, len(moves)):
        commentsByMove[moves[i].text.replace('\n', '').replace(' ', ' ')] = comments[i].text

    exportData = {}

    exportData['moves'] = commentsByMove
    exportData['url'] = url
    exportData['gameName'] = gameData[1]
    exportData['players'] = gameData[2]
    exportData['oppening'] = gameData[4]

    f = open("../Data/GameknotJSON/" + gameData[1].replace('"', "") + ".json", "w+")
    f.write(json.dumps(exportData, indent=4))
    f.close()


def getAmountOfPages(gameTable):
    pageTable = gameTable.find("table", {"class": "paginator"})
    return len(pageTable.find_all("td")) - 2

#Some test links
scrapChessGame('https://gameknot.com/annotation.pl/the-evergreen-game?gm=561')
scrapChessGame('https://gameknot.com/annotation.pl/bobby-fischers-game-of-the-century?gm=256')
scrapChessGame('https://gameknot.com/annotation.pl/tournament-in-wijk-aan-zee-annotated-by-g-kasparov?gm=216')
scrapChessGame('https://gameknot.com/annotation.pl/team-play-effect-of-competitive-situation-on-style-of-play?gm=11878')
scrapChessGame('https://gameknot.com/annotation.pl/a-short-fight-against-the-classical-pawn-center?gm=17618')
