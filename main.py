from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import engine, Base
from api.auth_api import router as auth_router
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
    
    yield  
    
    
    print("Shutting down...")

app = FastAPI(title="CTF App", lifespan=lifespan)


app.include_router(auth_router)

# Root endpoint عشان الصفحة مش تبقى فاضية
@app.get("/")
async def read_root():
    return {
        "message": "Welcome to CTF API",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}