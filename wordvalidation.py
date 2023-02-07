from http.client import HTTPException
import sqlite3
from fastapi import FastAPI,status

app = FastAPI()

#service to check if an input word is a  valid dictionary word
@app.get("/api/word/{word}",status_code=status.HTTP_200_OK)
async def validateWord(word):
    connection = sqlite3.connect("dictionary.db")
    cursor = connection.cursor()

    recordsCount=0
    dbResultList = cursor.execute("SELECT word from words where word=?",[word]).fetchall()
    if dbResultList is not None:
        recordsCount = len(dbResultList)
        if recordsCount>0:
            dbOutWord = dbResultList[0][0]
    else:
        #return ("not a valid letter")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={word+" is not a valid 5-letter word"})

    cursor.close()
    connection.close()

    if recordsCount>0 and dbOutWord is not None and len(dbOutWord)==5 and dbOutWord==word:
       return [recordsCount,word+" is a valid 5-letter word"]
    elif recordsCount==0 or dbOutWord is not None and len(dbOutWord)!=5 or dbOutWord is not None and dbOutWord!=word:
        return [recordsCount,word+" is not a valid 5-letter word"]
        
        