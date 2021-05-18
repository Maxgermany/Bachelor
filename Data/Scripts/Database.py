import sqlite3

def createTables():

    con = sqlite3.connect('../chessData.db')

    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS GAMES (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                gameName VARCHAR(255),
                url VARCHAR(255),
                scrapped BOOLEAN,
                opening VARCHAR(255),
                players VARCHAR(255)
            );
        """)

    con.close()

createTables()
