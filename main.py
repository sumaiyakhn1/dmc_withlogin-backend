from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import requests
import os
import time

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------
app = FastAPI(title="Student Login + Session API")

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "students.xlsx")

# -------------------------------------------------
# TOKEN CACHE
# -------------------------------------------------
LOGIN_TOKEN = None
TOKEN_TIME = 0
TOKEN_TTL = 20 * 60  # 20 minutes

def get_odpay_token():
    global LOGIN_TOKEN, TOKEN_TIME

    if LOGIN_TOKEN and (time.time() - TOKEN_TIME < TOKEN_TTL):
        return LOGIN_TOKEN

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
    TOKEN_TIME = time.time()
    return LOGIN_TOKEN

# -------------------------------------------------
# REQUEST MODEL
# -------------------------------------------------
class LoginRequest(BaseModel):
    login_id: str   # regNo
    password: str   # DOB (01-Mar-2005)

# -------------------------------------------------
# EXCEL VALIDATION
# -------------------------------------------------
def validate_student_from_excel(regNo: str, dob: str):
    if not os.path.exists(EXCEL_FILE):
        raise HTTPException(500, "students.xlsx not found")

    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.str.strip()

    df["Scholar ID"] = df["Scholar ID"].astype(str).str.strip()
    df["Birthday"] = pd.to_datetime(df["Birthday"]).dt.strftime("%d-%b-%Y")

    student = df[
        (df["Scholar ID"] == regNo) &
        (df["Birthday"] == dob)
    ]

    if student.empty:
        return None

    return student.iloc[0].to_dict()

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

# -------------------------------------------------
# LOGIN API (STEP 2 ONLY)
# -------------------------------------------------
@app.post("/login")
def login(data: LoginRequest):
    regNo = data.login_id.strip()
    dob = data.password.strip()

    # 1️⃣ Validate from Excel
    student = validate_student_from_excel(regNo, dob)
    if not student:
        raise HTTPException(401, "Invalid Roll Number or DOB")

    # 2️⃣ Get ODPay token
    token = get_odpay_token()

    # 3️⃣ Call studentLogin → session list
    res = requests.post(
        STUDENT_LOGIN_URL,
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "entity": ENTITY_ID,
            "regNo": regNo
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(404, "Session list not found")

    session_list = res.json().get("sessionList", [])

    # 4️⃣ Return clean response
    return {
        "student": {
            "name": student.get("Name as per 10th Document"),
            "regNo": regNo
        },
        "sessionList": session_list
    }
