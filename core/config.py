import os
from dotenv import load_dotenv
load_dotenv() 

class Settings:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")



    SECRET_POOL = {
        "apartment_numbers": ["101", "202", "303", "404", "505", "606", "707"],
        "elevator_codes":    ["1234", "5678", "9012", "3456", "7890"],
        "resident_names":    ["أحمد", "محمد", "علي", "حسن", "كريم", "سامي"],
        "door_passwords":    ["باب123", "سمسم", "افتح", "دخول99", "مفتاح7"],
        "safe_keys":         ["SAFE01", "KEY999", "LOCK77", "VAULT5", "BOX123"],
        "office_codes":      ["OFFICE1", "MGR007", "CEO123", "VIP999", "BOSS77"],
        "archive_keys":      ["ARCH01", "DOC999", "FILE77", "REC123", "ARC456"],
        "master_overrides":  ["MASTER1", "ROOT99", "ADMIN7", "SYS123", "GOD000"],
    }



settings = Settings()