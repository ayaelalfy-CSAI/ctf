import requests
from core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def exchange_code_for_token(code: str):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=data)

    print("STATUS:", response.status_code)
    print("BODY:", response.text) 

    return response.json()


def get_user_info(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    return response.json()