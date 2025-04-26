# app/main.py

from fastapi import FastAPI
from . import auth, models
from .database import engine

app = FastAPI()

models.SQLModel.metadata.create_all(engine)

app.include_router(auth.router)
