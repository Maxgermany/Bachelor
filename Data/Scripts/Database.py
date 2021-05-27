import sqlite3

def createTables():

    con = sqlite3.connect('../Data/chessData.db')

    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS GAMES (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                gameName VARCHAR(255),
                url VARCHAR(255),
                initialURL VARCHAR(255),
                scrapped BOOLEAN,
                opening VARCHAR(255),
                players VARCHAR(255),
                result varchar(15),
                time varchar(127)
            );
        """)

    con.close()

def writeGameIntoDB(gameName = "", url = "", initialURL = '', scrapped = False, opening = "", players = "", result = "", time = ""):

    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:

        sql = "INSERT INTO GAMES (gameName, url, initialURL, scrapped, opening, players, result, time) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"

        con.execute(sql, (gameName, url, initialURL, scrapped, opening, players, result, time))

    con.close()

def getUnscrappedURLS(amount = 10):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT url FROM GAMES WHERE scrapped = 0 LIMIT ?"
        c.execute(sql, (amount,))
        return c.fetchall()

    con.close()