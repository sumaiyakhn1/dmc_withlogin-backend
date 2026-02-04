from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import requests
import os
import time

app = FastAPI(title="Student Login Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "students.xlsx")

ENTITY_ID = "6608ec3120337200120f347e"

ODPAY_LOGIN_URL = "https://staging.odpay.in/login"
STUDENT_LOGIN_URL = "https://staging.odpay.in/studentLogin"

ODPAY_MOBILE = "9015434510"
ODPAY_PASSWORD = "9015434510"

# --------------------------------------------------
# TOKEN CACHE
# --------------------------------------------------
TOKEN = None
TOKEN_TIME = 0
TOKEN_TTL = 20 * 60  # 20 minutes

# --------------------------------------------------
# MODELS
# --------------------------------------------------
class LoginRequest(BaseModel):
    login_id: str
    password: str   # 01-Mar-2005

# --------------------------------------------------
# LOAD EXCEL
# --------------------------------------------------
def load_students():
    if not os.path.exists(EXCEL_FILE):
        raise HTTPException(500, "students.xlsx not found")

    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.str.strip()

    df["Scholar ID"] = df["Scholar ID"].astype(str).str.strip()
    df["Birthday"] = pd.to_datetime(df["Birthday"]).dt.strftime("%d-%b-%Y")

    return df

# --------------------------------------------------
# GET ODPAY TOKEN
# --------------------------------------------------
def get_odpay_token():
    global TOKEN, TOKEN_TIME

    if TOKEN and (time.time() - TOKEN_TIME < TOKEN_TTL):
        return TOKEN

    res = requests.post(
        ODPAY_LOGIN_URL,
        json={"mobile": ODPAY_MOBILE, "password": ODPAY_PASSWORD},
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(401, "ODPay login failed")

    TOKEN = res.json().get("token")
    TOKEN_TIME = time.time()

    return TOKEN

# --------------------------------------------------
# ROOT
# --------------------------------------------------
@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

# --------------------------------------------------
# LOGIN + SESSION PIPELINE
# --------------------------------------------------
@app.post("/login")
def login(data: LoginRequest):
    df = load_students()

    roll_no = data.login_id.strip()
    dob = data.password.strip()

    student = df[
        (df["Scholar ID"] == roll_no) &
        (df["Birthday"] == dob)
    ]

    if student.empty:
        raise HTTPException(401, "Invalid Roll Number or DOB")

    student_row = student.iloc[0]

    # 1️⃣ Get ODPay token
    token = get_odpay_token()

    # 2️⃣ Call studentLogin
    res = requests.post(
        STUDENT_LOGIN_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "entity": ENTITY_ID,
            "regNo": roll_no
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(404, "Student not found in ODPay")

    session_list = res.json().get("sessionList", [])

    # 3️⃣ FINAL RESPONSE
    return {
        "name": student_row["Name as per 10th Document"],
        "regNo": roll_no,
        "sessionList": session_list
    }
