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

#E5
@app.put("/clubs/{club_id}")
def update_club_details(club_id: int, name: str, description: str, category: str, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    coordinator_id = get_user_id_from_token(token)

    club = functions.update_club(club_id, coordinator_id, name, description, category)

    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    if club is False:
        raise HTTPException(status_code=403, detail="Not authorized")

    return club

#E6
@app.post("/clubs/{club_id}/apply")
def apply_to_club(club_id: int, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    student_id = get_user_id_from_token(token)

    membership = functions.apply_club(club_id, student_id)

    if membership is None:
        raise HTTPException(status_code=404, detail="Club not found")

    if membership is False:
        raise HTTPException(status_code=400, detail="Already applied to this club")

    return membership