import requests

LOGIN_URL = "https://staging.odpay.in/login"

def fetch_auth_token():
    payload = {
        "mobile": "9015434510",   # hardcoded
        "password": "9015434510"  # hardcoded
    }

    res = requests.post(LOGIN_URL, json=payload)

    if res.status_code != 200:
        return None

    data = res.json()
    return data.get("token")
