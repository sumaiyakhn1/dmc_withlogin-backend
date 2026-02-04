from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(
    title="Student Session API",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
ENTITY_ID = "6608ec3120337200120f347e"
ODPAY_LOGIN_URL = "https://staging.odpay.in/login"
STUDENT_LOGIN_URL = "https://staging.odpay.in/studentLogin"

ODPAY_MOBILE = "9015434510"
ODPAY_PASSWORD = "9015434510"

LOGIN_TOKEN = None


# -------------------------------------------------
# LOGIN FUNCTION
# -------------------------------------------------
def login_odpay():
    global LOGIN_TOKEN

    res = requests.post(
        ODPAY_LOGIN_URL,
        json={
            "mobile": ODPAY_MOBILE,
            "password": ODPAY_PASSWORD
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(401, "ODPay login failed")

    LOGIN_TOKEN = res.json().get("token")
    return LOGIN_TOKEN


# -------------------------------------------------
# STUDENT LOGIN CALL (with retry)
# -------------------------------------------------
def call_student_login(regNo: str, retry=False):
    global LOGIN_TOKEN

    if not LOGIN_TOKEN:
        login_odpay()

    res = requests.post(
        STUDENT_LOGIN_URL,
        headers={
            "Authorization": f"Bearer {LOGIN_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "entity": ENTITY_ID,
            "regNo": regNo
        },
        timeout=10
    )

    # 🔁 Token expired → relogin once
    if res.status_code == 401 and not retry:
        login_odpay()
        return call_student_login(regNo, retry=True)

    return res


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/")
def home():
    return {"message": "Student Session API running 🚀"}


# -------------------------------------------------
# API FOR FRONTEND
# -------------------------------------------------
@app.post("/student/session")
def get_session_list(regNo: str):
    res = call_student_login(regNo)

    if res.status_code != 200:
        raise HTTPException(res.status_code, res.text)

    data = res.json()

    return {
        "regNo": regNo,
        "sessionList": data.get("sessionList", [])
    }
