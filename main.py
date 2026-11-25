from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, EmailStr
import functions


app = FastAPI(
    title="Campus Connect"
    )

functions.create_admin()

class RegisterModel(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=1)

class LoginModel(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

class RefreshToken(BaseModel):
    refresh_token: str


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
        "access_token": new_access_token,
        "token_type": "bearer"
    }