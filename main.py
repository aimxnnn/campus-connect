from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, EmailStr
import functions


app = FastAPI(
    title="Campus Connect"
    )

functions.create_admin()
