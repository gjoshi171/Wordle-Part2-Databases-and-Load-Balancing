from http.client import HTTPException
import sqlite3
import uuid
from fastapi import FastAPI,status
from pydantic import BaseModel
import pandas as pd
from datetime import date, timedelta

app = FastAPI(root_path="api/v1")

#retrieve a win or loss for a particular game, along with a timestamp and number of guesses.
@app.get("/winorloss/{gameId}",status_code=status.HTTP_200_OK)
async def list_winorloss(gameId):
   connection = sqlite3.connect("./var/stats.db")
   cursor = connection.cursor()
   data= cursor.execute("SELECT won, finished, guesses FROM games where game_id=?",[gameId]).fetchall()
   df = pd.DataFrame(data)
   df_json= df.to_json(orient='index')
  
   cursor.close()
   connection.close()
   return df_json

#service to retrieve top 10 users by number of wins
@app.get("/api/stats/topwinners",status_code=status.HTTP_200_OK)
async def topWinners():
    connection = sqlite3.connect("./var/stats.db")
    cursor = connection.cursor()

    dbResultList = cursor.execute("SELECT user_id  from wins limit 10").fetchall()
    cursor.close()
    connection.close()
    return dbResultList

#service to retrieve top 10 users by longest streak
@app.get("/api/stats/topstreaks",status_code=status.HTTP_200_OK)
async def topStreaks():
    connection = sqlite3.connect("./var/stats.db")
    cursor = connection.cursor()

    dbResultList = cursor.execute("SELECT user_id,streak,beginning,ending from streaks limit 10").fetchall()
    cursor.close()
    connection.close()
    return dbResultList


#Models for Statistics API
class Guesses(BaseModel):
    g1: int
    g2: int
    g3: int
    g4: int
    g5: int
    g6: int
    fail: int

class Statistics(BaseModel):
    currentStreak: int
    maxStreak: int
    guesses: Guesses
    winPercentage: float
    gamesPlayed: int
    gamesWon: int
    averageGuesses: int

#service to retrieve statistics for a user
@app.get("/api/stats/statistics/{userid}", status_code=status.HTTP_200_OK)
async def statistics(userid):
    try:
        sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
        sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
        gamesPlayed = 0
        gamesWon = 0
        fail =0
        avgGuesses = 0
        currentStreak = 0
        maxStreak = 0
        guesses = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

        stats_connection = sqlite3.connect("./var/stats.db")
        stats_cursor = stats_connection.cursor()

        users_connection = sqlite3.connect("./shard/users.db", detect_types=sqlite3.PARSE_DECLTYPES)
        users_cursor = users_connection.cursor()

        gameShardNum = 0
        #usersResult = users_cursor.execute("select * from users where user_id = ?", [userid]).fetchall()
        users = users_cursor.execute("select * from users").fetchall()
        if users is not None and len(users):
            for u in users:
                if(str(u[1])==str(userid)):
                    gameShardNum = (int(u[0]) % 3) + 1
                    break
        print(gameShardNum)
        gamesdb_dict ={}

        gamesdb_dict = {
            1: "./shard/games1.db",
            2: "./shard/games2.db",
            3: "./shard/games3.db",
        }

        gamesdb = gamesdb_dict[gameShardNum]
        print(gamesdb)
        conn_games = sqlite3.connect(gamesdb, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor_games = conn_games.cursor()

        gamesResult = cursor_games.execute("SELECT guesses,won from games where user_id=?",[userid]).fetchall()
        print(gamesResult)
        #gamesResult = stats_cursor.execute("SELECT guesses,won from games where user_id=?",[userid]).fetchall()
        
        if gamesResult is not None:
            gamesPlayed = len(gamesResult)
            print(gamesPlayed)
            for g in gamesResult:
                guesses[g[0]]+=1
                if g[1] == 0:
                    fail+=1
            i = 1
            sumOfGuesses = 0
            while i <= 6:
                sumOfGuesses += i*guesses[i]
                i +=1

            winsResult = stats_cursor.execute("SELECT * from wins where user_id = ?",[userid]).fetchall()
            if winsResult is not None and len(winsResult)>0:
                gamesWon = winsResult[0][1]

            if gamesPlayed == 0:
                winPercentage = 0
            else:
                winPercentage = (gamesWon/gamesPlayed)*100
                avgGuesses = round(sumOfGuesses/gamesPlayed)

            streakResult = stats_cursor.execute("SELECT streak from streaks where user_id = ? order by ending desc",[userid]).fetchall()

            if (streakResult is not None and len(streakResult)>0 and streakResult[0] is not None and len(streakResult[0])>0):
                currentStreak = streakResult[0][0]
            else:
                currentStreak = 0

            maxStreakResult = stats_cursor.execute("SELECT MAX(streak) from streaks where user_id = ? order by ending desc",[userid]).fetchall()
            if (maxStreakResult is not None and len(maxStreakResult)>0):
                if len(maxStreakResult[0])!=0 and maxStreakResult[0][0] is not None:
                    maxStreak = maxStreakResult[0][0]
                else:
                    maxStreak = 0

            g = Guesses(g1=guesses[1], g2=guesses[2], g3=guesses[3], g4=guesses[4], g5=guesses[5], g6=guesses[6], fail=fail ) 
            stat = Statistics(currentStreak=currentStreak, maxStreak=maxStreak, guesses=g, winPercentage=round(winPercentage, 2), gamesPlayed=gamesPlayed, gamesWon=gamesWon, averageGuesses=avgGuesses)
        
        cursor_games.close()
        conn_games.close()
        users_cursor.close()
        users_connection.close()
        stats_cursor.close()
        stats_connection.close()
    except:
        print("Error!!")

    return stat