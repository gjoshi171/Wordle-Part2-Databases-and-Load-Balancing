import datetime
from http.client import HTTPException
import sqlite3
from fastapi import FastAPI, status

app = FastAPI()

#Service to check a valid guess against the answer for the day
@app.get("/api/answer/{guess}",status_code=status.HTTP_200_OK)
async def checkAnswer(guess):
    today = datetime.datetime.now()

    connection = sqlite3.connect("answers.db")
    cursor = connection.cursor()

    dayword = ""
    dbResultList = cursor.execute("SELECT word from answers where playingDate =?",[today.date()]).fetchall()
    if dbResultList is not None:
        recordsCount = len(dbResultList)
        if recordsCount>0:
            dayword = dbResultList[0][0]
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={dayword+" is not a valid 5-letter word"})
        #return ("not a valid 5-letter word")
    cursor.close()
    connection.close()
    
    inthecorrectspot=[]
    inthewrongspot=[]
    notintheword=[]

    if guess is not None and len(guess)==5:
        if dayword==guess:
            return "Guessed word is correct"
        else:
            for i, v in enumerate(guess):
                pos = dayword.find(v)

                if pos==-1:
                    notintheword.append(v)
                elif pos==i:
                    inthecorrectspot.append(v)
                elif pos!=-1 and pos!=i:
                    if(dayword[i]==v):
                        inthecorrectspot.append(v)
                    else:
                        inthewrongspot.append(v)
    elif guess is None or guess is not None and len(guess)!=5:
        return "Please input a valid 5-letter word"
    
    x = "Letters in the correct spot= "
    x += ','.join(inthecorrectspot)

    y = "Letters in the wrong spot: "
    y += ','.join(inthewrongspot)

    z = "Letters NOT in the answer: "
    z += ','.join(notintheword)

    return [x,y,z]