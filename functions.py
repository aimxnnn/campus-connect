from sqlalchemy.orm import Session
from tables import engine, User, Club, Membership, Event, Registration
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from datetime import datetime, timedelta, timezone


SECRET_KEY = "campus-connect-secret-key-for-jwt-2026"
ALGORITHM = "HS256"

password_hasher = PasswordHasher()


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

#E4
def get_club(club_id):
    session=session(engine)

    club = session.query(Club).filter(club.id=club_id).first()

    if club:
        response = {
            "id"=club.id,
            "name"=club.name,
            "category"=club.category,
            "description"=club.description,
            "coordinator_id"=club.coordinator_id,
        }

        session.close()
        return response

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