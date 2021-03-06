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

        con.execute("""
            CREATE TABLE IF NOT EXISTS GAMECOMMENTS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                gameId INTEGER NOT NULL,
                comment TEXT,
                stage VARCHAR(255),
                moves VARCHAR(255),
                FOREIGN KEY(gameId) REFERENCES GAMES(id)
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS NAMEDENTITIES (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                commentId INTEGER NOT NULL,
                tag VARCHAR(16),
                entityName VARCHAR(255),
                FOREIGN KEY(commentID) REFERENCES GAMECOMMENTS(id)
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS DATAPOINTS (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                commentId INTEGER NOT NULL,
                entityName VARCHAR(32),
                attributeName VARCHAR(256),
                attributeValue VARCHAR(256)
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

def getUnscrapedURLS(amount = 10):
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

def setURLToScraped(url = "", opening = ""):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "UPDATE GAMES SET scrapped = 1, opening = ? WHERE url = ?"
        con.execute(sql, (opening, url))

    con.close()

def getGameIDFromURL(url = ""):
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT id FROM GAMES WHERE url = ? LIMIT 1"
        c.execute(sql, (url,))
        return c.fetchall()[0][0]

    con.close()

def writeMoveCommentPairIntoDB(gameId = 1, comment = '', stage = 'initial', moves = ''):
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "INSERT INTO GAMECOMMENTS (gameId, comment, stage, moves) VALUES(?, ?, ?, ?)"

        con.execute(sql, (gameId, comment, stage, moves))

    con.close()

def writeManyMoveCommentPairsIntoDB(records):
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "INSERT INTO GAMECOMMENTS (gameId, comment, stage, moves) VALUES(?, ?, ?, ?)"

        con.executemany(sql, records)

    con.close()

def writeNamedEntitiyIntoDB(commentId = 1, tag = '', entityName = ''):
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='NAMEDENTITIES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "INSERT INTO NAMEDENTITIES (commentId, tag, entityName) VALUES(?, ?, ?)"

        con.execute(sql, (commentId, tag, entityName))

    con.close()

def getMaxCommentIDFromNamedEntities():
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='NAMEDENTITIES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT MAX(commentId) FROM NAMEDENTITIES"

        c.execute(sql)
        return c.fetchone()

    con.close()

def getMoveCommentsPairs(stage = 'initial'):
    con = sqlite3.connect('../chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMECOMMENTS WHERE stage = ?"
        c.execute(sql, (stage,))
        return c.fetchall()

    con.close()

def getMoveCommentsOfGame(gameId=1, stage='initial'):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMECOMMENTS WHERE stage = ? AND gameId = ? ORDER BY Id"
        c.execute(sql, (stage, gameId))
        return c.fetchall()

def getGame(gameId=1):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMES WHERE Id = ?"
        c.execute(sql, (gameId,))
        return c.fetchone()

def writeManyDataPointsIntoDB(records):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DATAPOINTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "INSERT INTO DATAPOINTS (commentId, entityName, attributeName, attributeValue) VALUES(?, ?, ?, ?)"
        con.executemany(sql, records)

    con.close()

def getAllDataPointsOfComment(commentId=1):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DATAPOINTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM DATAPOINTS WHERE commentId = ?"
        c.execute(sql, (commentId,))
        return c.fetchall()

    con.close()

def getAllDataPoints():
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DATAPOINTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM DATAPOINTS"
        c.execute(sql)
        return c.fetchall()

    con.close()

def getCommentById(commentId=1):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMECOMMENTS WHERE Id = ?"
        c.execute(sql, (commentId,))
        return c.fetchone()

    con.close()

def getDistinctCommentIdsFromDatapoints():
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DATAPOINTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT DISTINCT commentId FROM DATAPOINTS"
        c.execute(sql)
        return c.fetchall()

    con.close()

def getAllComments(stage = 'removeLinks'):
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMECOMMENTS' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMECOMMENTS WHERE stage = ?"
        c.execute(sql, (stage,))
        return c.fetchall()

    con.close()

def getAllGames():
    con = sqlite3.connect('../Data/chessData.db')

    c = con.cursor()
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='GAMES' ''')

    if c.fetchone()[0] != 1:
        createTables()

    with con:
        sql = "SELECT * FROM GAMES"
        c.execute(sql)
        return c.fetchall()

    con.close()