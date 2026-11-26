from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, EmailStr
import functions


app = FastAPI(
    title="Campus Connect"
    )

functions.create_admin()

#Shafff
class RegisterModel(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=1)

class LoginModel(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

class RefreshToken(BaseModel):
    refresh_token: str

class ClubModel(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    coordinator_id: int

# A1 - REGISTER USER

@app.post("/auth/register", status_code=201)
def register_user(data: RegisterModel):

    result = functions.register_user(
        data.username,
        data.email,
        data.password
    )

    if result is None:
        raise HTTPException(status_code=409, detail="Email already exists")

    return {
        "message": "User registered successfully"
    }


# A2 - LOGIN USER

@app.post("/auth/login")
def login_user(data: LoginModel):

    result = functions.login_user(
        data.email,
        data.password
    )

    if result is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return result


# A3 - GENERATE NEW ACCESS TOKEN

@app.post("/auth/refresh")
def refresh_token(data: RefreshToken):

    new_access_token = functions.refresh_access_token(data.refresh_token)

    if new_access_token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return {
        "access_token": new_access_token
    }


# E1 - CREATE COORDINATOR ACCOUNT

@app.post("/admin/coordinators", status_code=201)
def create_coordinator(data: RegisterModel, token: str = Header(None)):

    result = functions.create_coordinator(
        token,
        data.username,
        data.email,
        data.password
    )

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]


# E2 - CREATE CLUB

@app.post("/clubs", status_code=201)
def create_club(data: ClubModel, token: str = Header(None)):

    result = functions.create_club(
        token,
        data.name,
        data.description,
        data.category,
        data.coordinator_id
    )

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return result["data"]


# E3 - GET ALL CLUBS

@app.get("/clubs")
def get_all_clubs():

    clubs = functions.get_all_clubs()

    return {
        "clubs": clubs
    }

#Madiha
#E4
@app.get("/clubs/{club_id}")
def get_club_details(club_id: int, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    club = functions.get_club(club_id)

    if club is None:
        raise HTTPException(status_code=404, detail="Club not found")

    return club

# E5
@app.put("/clubs/{club_id}")
def update_club_details(club_id: int, name: str, description: str, category: str, token: str = Header(None)):

    if token is None:
        raise HTTPException(status_code=401, detail="Token required")

    coordinator_id = functions.get_user_id_from_token(token)

    if coordinator_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

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

# E15 - GET STUDENT'S EVENT PARTICIPATION HISTORY

@app.get("/students/me/participation")
def get_my_history(token: str = Header(None)):

    result = functions.get_my_history(token)

    if result["error"] is not None:
        raise HTTPException(status_code=result["code"], detail=result["error"])

    return {
        "history": result["data"]
    }
