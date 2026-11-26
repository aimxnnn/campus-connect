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


# E6
@app.post("/clubs/{club_id}/apply")
def apply_to_club(club_id: int, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    student_id = functions.get_user_id_from_token(token)

    if student_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    membership = functions.apply_club(club_id, student_id)

    if membership is None:
        raise HTTPException(status_code=404, detail="Club not found")

    if membership is False:
        raise HTTPException(status_code=400, detail="Already applied to this club")

    return membership



# E7
@app.patch("/clubs/{club_id}/requests/{request_id}")
def update_membership_request(club_id: int, request_id: int, status: str, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    coordinator_id = functions.get_user_id_from_token(token)

    if coordinator_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    membership = functions.update_membership(
        club_id, request_id, coordinator_id, status
    )

    if membership is None:
        raise HTTPException(status_code=404, detail="Club or membership request not found")

    if membership is False:
        raise HTTPException(status_code=403, detail="Not authorized")

    if membership == "invalid":
        raise HTTPException(status_code=400, detail="Invalid membership status")

    return membership

#E8
@app.get("/clubs/{club_id}/members")
def get_club_members(club_id: int, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    coordinator_id = functions.get_user_id_from_token(token)

    members = functions.get_club_members(club_id, coordinator_id)

    if members is None:
        raise HTTPException(status_code=404, detail="Club not found")

    if members is False:
        raise HTTPException(status_code=403, detail="Not authorized")

    return members
# E9
@app.post("/clubs/{club_id}/events")
def create_campus_event(
    club_id: int,
    title: str,
    description: str,
    venue: str,
    date: datetime,
    max_capacity: int,
    token: str = Header(None)
):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    if max_capacity <= 0:
        raise HTTPException(status_code=422, detail="Invalid event capacity")

    coordinator_id = functions.get_user_id_from_token(token)

    if coordinator_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    event = functions.create_event(
        club_id,
        coordinator_id,
        title,
        description,
        venue,
        date,
        max_capacity
    )

    if event is None:
        raise HTTPException(status_code=404, detail="Club not found")

    if event is False:
        raise HTTPException(status_code=403, detail="Not authorized")

    return event