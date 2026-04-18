import os
from dotenv import load_dotenv
load_dotenv() 

class Settings:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  

    
settings = Settings()