from sqlalchemy.orm import Session
from tables import engine, User, Club, Membership, Event, Registration
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from datetime import datetime, timedelta, timezone


SECRET_KEY = "campus-connect-secret-key-for-jwt-2026"
ALGORITHM = "HS256"

password_hasher = PasswordHasher()

# ---- Functions used commonly across all endpoints ---- 

def fail(message, code):
    return {"error": message, "code": code, "data": None}


def ok(data, code=200):
    return {"error": None, "code": code, "data": data}


def create_token(email, token_type):

    if token_type == "access":
        expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    else:
        expiry = datetime.now(timezone.utc) + timedelta(days=7)

    payload = {
        "sub": email,
        "type": token_type,
        "exp": expiry
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_token(token, token_type):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")
        actual_type = payload.get("type")

        if email is None or actual_type != token_type:
            return None

        return email

    except jwt.InvalidTokenError:
        return None


def get_user(session, token):

    if token is None:
        return None

    email = verify_token(token, "access")

    if email is None:
        return None

    return session.query(User).filter(User.email == email).first()


def club_error(session, user, club_id):

    if user.role != "coordinator":
        return fail("Coordinator access required", 403)

    club = session.query(Club).filter(Club.id == club_id).first()

    if club is None:
        return fail("Club not found", 404)

    if club.coordinator_id != user.id:
        return fail("You are not the coordinator of this club", 403)

    return None


def create_admin():

    session = Session(engine)

    admin = session.query(User).filter(User.role == "admin").first()

    if admin is None:
        new_admin = User(
            username="Admin",
            email="admin@campus.com",
            hashed_password=password_hasher.hash("admin123"),
            role="admin"
        )
        session.add(new_admin)
        session.commit()

    session.close()

#Aiman:- 

# E10 - GET ALL EVENTS

def get_all_events():

    session = Session(engine)

    events = session.query(Event).all()

    response = []

    for event in events:

        club = session.query(Club).filter(Club.id == event.club_id).first()

        registered = session.query(Registration).filter(
            Registration.event_id == event.id
        ).count()

        seats_left = event.capacity - registered

        is_open = seats_left > 0 and event.deadline > datetime.now()

        temp_event = {
            "id": event.id,
            "club_id": event.club_id,
            "club_name": club.name,
            "title": event.title,
            "description": event.description,
            "venue": event.venue,
            "event_date": event.event_date,
            "deadline": event.deadline,
            "capacity": event.capacity,
            "registered": registered,
            "seats_left": seats_left,
            "registration_open": is_open
        }

        response.append(temp_event)

    session.close()

    return response

# E11 - REGISTER FOR AN EVENT

def register_for_event(token, event_id):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    if user.role != "student":
        session.close()
        return fail("Student access required", 403)

    event = session.query(Event).filter(Event.id == event_id).first()

    if event is None:
        session.close()
        return fail("Event not found", 404)

    if event.deadline < datetime.now():
        session.close()
        return fail("Registration deadline has passed", 400)

    existing = session.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.student_id == user.id
    ).first()

    if existing:
        session.close()
        return fail("You already registered for this event", 409)

    registered = session.query(Registration).filter(
        Registration.event_id == event_id
    ).count()

    if registered >= event.capacity:
        session.close()
        return fail("Event is full", 400)

    new_registration = Registration(
        event_id=event_id,
        student_id=user.id
    )

    session.add(new_registration)
    session.commit()
    session.refresh(new_registration)

    response = {
        "registration_id": new_registration.id,
        "event_id": new_registration.event_id,
        "message": "Registered successfully"
    }

    session.close()

    return ok(response, 201)

# E12 - CANCEL EVENT REGISTRATION

def cancel_registration(token, event_id):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    if user.role != "student":
        session.close()
        return fail("Student access required", 403)

    registration = session.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.student_id == user.id
    ).first()

    if registration is None:
        session.close()
        return fail("You are not registered for this event", 404)

    if registration.attended:
        session.close()
        return fail("Attendance already marked, cannot cancel", 400)

    session.delete(registration)
    session.commit()

    session.close()

    return ok({"message": "Registration cancelled"})

# E13 - MARK EVENT ATTENDANCE

def mark_attendance(token, event_id, student_id, attended):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    event = session.query(Event).filter(Event.id == event_id).first()

    if event is None:
        session.close()
        return fail("Event not found", 404)

    problem = club_error(session, user, event.club_id)

    if problem is not None:
        session.close()
        return problem

    registration = session.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.student_id == student_id
    ).first()

    if registration is None:
        session.close()
        return fail("Student is not registered for this event", 404)

    registration.attended = attended

    session.commit()

    response = {
        "event_id": event_id,
        "student_id": student_id,
        "attended": attended
    }

    session.close()

    return ok(response)

# E14 - GET REGISTERED PARTICIPANTS OF AN EVENT

def get_event_participants(token, event_id):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    event = session.query(Event).filter(Event.id == event_id).first()

    if event is None:
        session.close()
        return fail("Event not found", 404)

    problem = club_error(session, user, event.club_id)

    if problem is not None:
        session.close()
        return problem

    registrations = session.query(Registration).filter(
        Registration.event_id == event_id
    ).all()

    response = []

    for r in registrations:

        student = session.query(User).filter(User.id == r.student_id).first()

        temp_participant = {
            "student_id": student.id,
            "username": student.username,
            "email": student.email,
            "attended": r.attended,
            "registered_at": r.created_at
        }

        response.append(temp_participant)

    session.close()

    return ok(response)

# E15 - GET STUDENT'S EVENT PARTICIPATION HISTORY

def get_my_history(token):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    if user.role != "student":
        session.close()
        return fail("Student access required", 403)

    registrations = session.query(Registration).filter(
        Registration.student_id == user.id
    ).all()

    response = []

    for r in registrations:

        event = session.query(Event).filter(Event.id == r.event_id).first()
        club = session.query(Club).filter(Club.id == event.club_id).first()

        temp_history = {
            "event_id": event.id,
            "title": event.title,
            "venue": event.venue,
            "event_date": event.event_date,
            "club_name": club.name,
            "registered_at": r.created_at,
            "attended": r.attended
        }

        response.append(temp_history)

    session.close()

    return ok(response)