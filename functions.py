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

def get_user_id_from_token(token):
    session = Session(engine)
    user = get_user(session, token)

    if user is None:
        session.close()
        return None

    user_id = user.id

    session.close()
    return user_id

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

# Shafff
# A1 - REGISTER USER

def register_user(username, email, password):

    session = Session(engine)

    existing_user = session.query(User).filter(User.email == email).first()

    if existing_user:
        session.close()
        return None

    hashed_password = password_hasher.hash(password)

    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role="student"
    )

    session.add(new_user)
    session.commit()

    session.close()

    return True

# A2 - LOGIN USER

def login_user(email, password):

    session = Session(engine)

    user = session.query(User).filter(User.email == email).first()

    if user is None:
        session.close()
        return None

    try:
        password_hasher.verify(user.hashed_password, password)

    except VerifyMismatchError:
        session.close()
        return None

    access_token = create_token(user.email, "access")
    refresh_token = create_token(user.email, "refresh")
    role = user.role

    session.close()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": role
    }


# A3 - GENERATE NEW ACCESS TOKEN

def refresh_access_token(refresh_token):

    email = verify_token(refresh_token, "refresh")

    if email is None:
        return None

    new_access_token = create_token(email, "access")

    return new_access_token


# E1 - CREATE COORDINATOR ACCOUNT

def create_coordinator(token, username, email, password):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    if user.role != "admin":
        session.close()
        return fail("Admin access required", 403)

    existing_user = session.query(User).filter(User.email == email).first()

    if existing_user:
        session.close()
        return fail("Email already exists", 409)

    new_user = User(
        username=username,
        email=email,
        hashed_password=password_hasher.hash(password),
        role="coordinator"
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    response = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

    session.close()

    return ok(response, 201)

# E2 - CREATE CLUB

def create_club(token, name, description, category, coordinator_id):

    session = Session(engine)

    user = get_user(session, token)

    if user is None:
        session.close()
        return fail("Invalid or missing access token", 401)

    if user.role != "admin":
        session.close()
        return fail("Admin access required", 403)

    coordinator = session.query(User).filter(
        User.id == coordinator_id,
        User.role == "coordinator"
    ).first()

    if coordinator is None:
        session.close()
        return fail("Coordinator not found", 404)

    existing_club = session.query(Club).filter(Club.name == name).first()

    if existing_club:
        session.close()
        return fail("Club name already exists", 409)

    new_club = Club(
        name=name,
        description=description,
        category=category,
        coordinator_id=coordinator_id
    )

    session.add(new_club)
    session.commit()
    session.refresh(new_club)

    response = {
        "id": new_club.id,
        "name": new_club.name,
        "description": new_club.description,
        "category": new_club.category,
        "coordinator_id": new_club.coordinator_id
    }

    session.close()

    return ok(response, 201)


# E3 - GET ALL CLUBS

def get_all_clubs():

    session = Session(engine)

    clubs = session.query(Club).all()

    response = []

    for club in clubs:

        coordinator = session.query(User).filter(
            User.id == club.coordinator_id
        ).first()

        temp_club = {
            "id": club.id,
            "name": club.name,
            "description": club.description,
            "category": club.category,
            "coordinator_id": club.coordinator_id,
            "coordinator_name": coordinator.username
        }

        response.append(temp_club)

    session.close()

    return response

#Madiha 
#E4
def get_club(club_id):
    session = Session(engine)

    club = session.query(Club).filter(
        Club.id == club_id
    ).first()

    if club:
        response = {
            "id": club.id,
            "name": club.name,
            "description": club.description,
            "category": club.category,
            "coordinator_id": club.coordinator_id
        }

        session.close()
        return response

    session.close()
    return None

#E5
def update_club(club_id, coordinator_id, name, description, category):
    session = Session(engine)

    club = session.query(Club).filter(Club.id == club_id).first()

    if club is None:
        session.close()
        return None

    if club.coordinator_id != coordinator_id:
        session.close()
        return False

    club.name = name
    club.description = description
    club.category = category

    session.commit()

    response = {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "category": club.category,
        "coordinator_id": club.coordinator_id
    }

    session.close()
    return response

#E6
def apply_club(club_id, student_id):
    session = Session(engine)

    club = session.query(Club).filter(Club.id == club_id).first()

    if club is None:
        session.close()
        return None

    existing_request = session.query(Membership).filter(
        Membership.club_id == club_id,
        Membership.student_id == student_id
    ).first()

    if existing_request:
        session.close()
        return False

    membership = Membership(
        club_id=club_id,
        student_id=student_id,
        status="pending"
    )

    session.add(membership)
    session.commit()

    response = {
        "id": membership.id,
        "club_id": membership.club_id,
        "student_id": membership.student_id,
        "status": membership.status
    }

    session.close()
    return response

#E7
def update_membership(club_id, request_id, coordinator_id, status):
    session = Session(engine)

    club = session.query(Club).filter(
        Club.id == club_id
    ).first()

    if club is None:
        session.close()
        return None

    if club.coordinator_id != coordinator_id:
        session.close()
        return False

    membership = session.query(Membership).filter(
        Membership.id == request_id,
        Membership.club_id == club_id
    ).first()

    if membership is None:
        session.close()
        return None

    if status not in ["approved", "rejected"]:
        session.close()
        return "invalid"

    membership.status = status

    session.commit()

    response = {
        "id": membership.id,
        "club_id": membership.club_id,
        "student_id": membership.student_id,
        "status": membership.status
    }

    session.close()
    return response

#E8
def get_club_members(club_id, coordinator_id):
    session = Session(engine)

    club = session.query(Club).filter(
        Club.id == club_id
    ).first()

    if club is None:
        session.close()
        return None

    if club.coordinator_id != coordinator_id:
        session.close()
        return False

    members = session.query(Membership).filter(
        Membership.club_id == club_id,
        Membership.status == "approved"
    ).all()

    session.close()
    return members

#E9
def create_event(club_id, coordinator_id, title, description, venue, date, max_capacity):
    session = Session(engine)

    club = session.query(Club).filter(
        Club.id == club_id
    ).first()

    if club is None:
        session.close()
        return None

    if club.coordinator_id != coordinator_id:
        session.close()
        return False

    event = Event(
        club_id=club_id,
        title=title,
        description=description,
        venue=venue,
        date=date,
        max_capacity=max_capacity
    )

    session.add(event)
    session.commit()

    response = {
        "id": event.id,
        "club_id": event.club_id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "date": event.date,
        "max_capacity": event.max_capacity
    }

    session.close()
    return response

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
