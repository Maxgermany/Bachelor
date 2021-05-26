from bs4 import BeautifulSoup
import requests
import json

def scrapChessGameSite(url):
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
    pages = pageTable.find_all(("td"))
    return int(pages[-2].text)


def scrapChessGames(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    gamesTr = soup.find_all("tr", {"class": ["evn_list", "odd_list"]})

    games = {}

    games['url'] = url

    for game in gamesTr:
        games[game.find_all("a")[1].text] = game.find_all("a")[1]['href']

    f = open("../Data/GameknotJSON/links.json", "w+")
    f.write(json.dumps(games, indent=4))
    f.close()



# Some test links
# scrapChessGameSite('https://gameknot.com/annotation.pl/the-evergreen-game?gm=561')
# scrapChessGameSite('https://gameknot.com/annotation.pl/bobby-fischers-game-of-the-century?gm=256')
# scrapChessGameSite('https://gameknot.com/annotation.pl/tournament-in-wijk-aan-zee-annotated-by-g-kasparov?gm=216')
# scrapChessGameSite('https://gameknot.com/annotation.pl/team-play-effect-of-competitive-situation-on-style-of-play?gm=11878')
# scrapChessGameSite('https://gameknot.com/annotation.pl/a-short-fight-against-the-classical-pawn-center?gm=17618')

scrapChessGames('https://gameknot.com/best-annotated-games.pl')