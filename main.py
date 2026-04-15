from fastapi import FastAPI
from core.database import engine, Base
from api.auth_api import router as auth_router

import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)