from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, EmailStr
import functions


app = FastAPI(
    title="Campus Connect"
    )

functions.create_admin()

#Aiman:-

# E4 - GET ONE CLUB

@app.get("/clubs/{club_id}")
def get_club(club_id: int, token: str = Header(None)):

    result = functions.get_club(token, club_id)

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]