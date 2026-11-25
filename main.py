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

class AttendanceModel(BaseModel):
    student_id: int
    attended: bool = True

# E10 - GET ALL EVENTS

@app.get("/events")
def get_all_events():

    events = functions.get_all_events()

    return {
        "events": events
    }

# E11 - REGISTER FOR AN EVENT

@app.post("/events/{event_id}/register", status_code=201)
def register_for_event(event_id: int, token: str = Header(None)):

    result = functions.register_for_event(token, event_id)

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]

# E12 - CANCEL EVENT REGISTRATION

@app.delete("/events/{event_id}/register")
def cancel_registration(event_id: int, token: str = Header(None)):

    result = functions.cancel_registration(token, event_id)

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]

# E13 - MARK EVENT ATTENDANCE

@app.put("/events/{event_id}/attendance")
def mark_attendance(event_id: int, data: AttendanceModel, token: str = Header(None)):

    result = functions.mark_attendance(
        token,
        event_id,
        data.student_id,
        data.attended
    )

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]

# E14 - GET REGISTERED PARTICIPANTS OF AN EVENT

@app.get("/events/{event_id}/participants")
def get_event_participants(event_id: int, token: str = Header(None)):

    result = functions.get_event_participants(token, event_id)

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return {
        "participants": result["data"]
    }

