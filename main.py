from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, EmailStr
import functions


app = FastAPI(
    title="Campus Connect"
    )

functions.create_admin()

#E4
@app.get("/clubs/{club_id}")
def get_club_details(club_id: int, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    club = functions.get_club(club_id)

    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    return club
