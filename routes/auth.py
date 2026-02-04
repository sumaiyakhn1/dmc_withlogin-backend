from fastapi import APIRouter, HTTPException
import requests
import time

router = APIRouter()

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
ODPAY_LOGIN_URL = "https://staging.odpay.in/login"
ODPAY_MOBILE = "9015434510"
ODPAY_PASSWORD = "9015434510"

# --------------------------------------------------
# TOKEN CACHE
# --------------------------------------------------
_auth_token = None
_token_time = 0
TOKEN_TTL = 20 * 60  # 20 minutes


def get_odpay_token():
    global _auth_token, _token_time

    # Reuse token if valid
    if _auth_token and (time.time() - _token_time < TOKEN_TTL):
        return _auth_token

    res = requests.post(
        ODPAY_LOGIN_URL,
        json={
            "mobile": ODPAY_MOBILE,
            "password": ODPAY_PASSWORD
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="ODPay login failed")

    _auth_token = res.json().get("token")
    _token_time = time.time()

    return _auth_token


# --------------------------------------------------
# DEBUG / HEALTH ENDPOINT
# --------------------------------------------------
@router.get("/token")
def fetch_token():
    """
    ONLY for testing / debugging.
    Confirms token generation & caching.
    """
    token = get_odpay_token()
    return {
        "token": token,
        "cached": True
    }
