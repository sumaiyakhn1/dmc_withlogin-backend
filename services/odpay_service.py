import requests
import time
from fastapi import HTTPException

ODPAY_LOGIN_URL = "https://staging.odpay.in/login"
STUDENT_LOGIN_URL = "https://staging.odpay.in/studentLogin"
STUDENT_VIEW_URL = "https://staging.odpay.in/api/view/student"

ENTITY_ID = "6608ec3120337200120f347e"
MOBILE = "9015434510"
PASSWORD = "9015434510"

_token = None
_token_time = 0
TOKEN_TTL = 20 * 60  # 20 minutes


def get_token():
    global _token, _token_time

    if _token and time.time() - _token_time < TOKEN_TTL:
        return _token

    res = requests.post(
        ODPAY_LOGIN_URL,
        json={"mobile": MOBILE, "password": PASSWORD},
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(401, "ODPay login failed")

    _token = res.json()["token"]
    _token_time = time.time()
    return _token


def get_session_list(reg_no: str):
    token = get_token()

    res = requests.post(
        STUDENT_LOGIN_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"entity": ENTITY_ID, "regNo": reg_no},
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(404, "Student not found")

    return res.json()["sessionList"]


def get_student_details(reg_no: str, session: str):
    token = get_token()

    res = requests.get(
        STUDENT_VIEW_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "entity": ENTITY_ID,
            "session": session,
            "regNo": reg_no
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(404, "Student details fetch failed")

    return res.json()
