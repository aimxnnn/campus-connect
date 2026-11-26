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