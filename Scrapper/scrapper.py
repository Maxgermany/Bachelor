from bs4 import BeautifulSoup
import requests
import json
import os
import Data.Scripts.Database as DatabaseHelper

def scrapChessGameSite(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    gameTable = soup.find("table", {"class": "dialog"})

    comments = gameTable.find_all("td", {"style": "vertical-align: top;"})
    moves = gameTable.find_all("td", {"style": "vertical-align: top; width: 20%;"})

    gameData = soup.find("div", {"style": "padding: 4px 0px; line-height: 150%;"})
    gameData = gameData.text.split("\n")

    amountPages = getAmountOfPages(gameTable)

    for i in range(1, amountPages):

        page = requests.get(url + "&pg=" + str(i))
        soup = BeautifulSoup(page.content, 'html.parser')

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
    exportData['opening'] = gameData[4][15:]

    path = "../Data/GameknotJSON/" + gameData[1].replace('"', "") + ".json"
    i = 1

    while os.path.exists(path):
        path = "../Data/GameknotJSON/" + gameData[1].replace('"', "") + " - " + str(i) + ".json"
        i += 1

    f = open(path, "w+")

    f.write(json.dumps(exportData, indent=4))
    f.close()

    return exportData['opening']


def getAmountOfPages(gameTable):
    pageTable = gameTable.find("table", {"class": "paginator"})

    if pageTable is None:
        return 1

    pages = pageTable.find_all(("td"))
    return int(pages[-2].text)


def scrapChessGames(url, pagingationString = '?p='):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    gamesTr = soup.find_all("tr", {"class": ["evn_list", "odd_list"]})

    games = []

    amountPages = getAmountOfPages(soup)

    for i in range(1, amountPages):
        page = requests.get(url + pagingationString + str(i))
        soup = BeautifulSoup(page.content, 'html.parser')

        for game in soup.find_all("tr", {"class": ["evn_list", "odd_list"]}):
            gamesTr.append(game)

    for game in gamesTr:

        gameObject = {}
        gameObject['initialURL'] = url
        gameObject['url'] = "https://gameknot.com" + game.find_all("a")[1]['href']
        gameObject['gameName'] = game.find_all("a")[1].text

        for tag in game.find_all('em'):
            tag.decompose()

        gameObject['players'] = game.text.split("\n")[2]

        tds = game.find_all("td")
        gameObject['result'] = tds[2].text
        gameObject['time'] = tds[3].text

        games.append(gameObject)

        DatabaseHelper.writeGameIntoDB(gameName = gameObject['gameName'], url = gameObject['url'], initialURL = url, players = gameObject['players'], result = gameObject['result'], time = gameObject['time'])

    path = '../Data/GameknotJSON/links.json'

    if os.path.exists(path):
        f = open(path, "r+")
    else:
        f = open(path, "w+")

    content = f.read()

    if content == "":
        json.dump(games, f, indent = 4)
    else:
        data = json.loads(content)
        data += [game for game in games if game not in data]
        f.seek(0)
        json.dump(data, f, indent = 4)
        f.close()


def scrapChessGameSiteAutomatic():

    urls = DatabaseHelper.getUnscrapedURLS(10)
    for url in urls:
        opening = scrapChessGameSite(url[0])
        DatabaseHelper.setURLToScraped(url[0], opening)

# Some test links
# scrapChessGameSite('https://gameknot.com/annotation.pl/the-evergreen-game?gm=561')
# scrapChessGameSite('https://gameknot.com/annotation.pl/bobby-fischers-game-of-the-century?gm=256')
# scrapChessGameSite('https://gameknot.com/annotation.pl/tournament-in-wijk-aan-zee-annotated-by-g-kasparov?gm=216')
# scrapChessGameSite('https://gameknot.com/annotation.pl/team-play-effect-of-competitive-situation-on-style-of-play?gm=11878')
# scrapChessGameSite('https://gameknot.com/annotation.pl/a-short-fight-against-the-classical-pawn-center?gm=17618')

#scrapChessGames('https://gameknot.com/best-annotated-games.pl', '?pp=')
#scrapChessGames('https://gameknot.com/list_annotated.pl?u=all', '&p=')


scrapChessGameSiteAutomatic()