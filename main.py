from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import requests
import os
import time

from student_details import fetch_student_details

app = FastAPI(title="Student Login API")

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

TOKEN = None
TOKEN_TIME = 0
TOKEN_TTL = 20 * 60

# --------------------------------------------------
# MODELS
# --------------------------------------------------
class LoginRequest(BaseModel):
    login_id: str
    password: str

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def load_students():
    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.str.strip()
    df["Scholar ID"] = df["Scholar ID"].astype(str).str.strip()
    df["Birthday"] = pd.to_datetime(df["Birthday"]).dt.strftime("%d-%b-%Y")
    return df


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
# ROUTES
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
        raise HTTPException(401, "Invalid Scholar ID or DOB")

    token = get_odpay_token()

    res = requests.post(
        STUDENT_LOGIN_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"entity": ENTITY_ID, "regNo": roll_no},
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(404, "Student not found in ODPay")

    return {
        "name": student.iloc[0]["Name as per 10th Document"],
        "regNo": roll_no,
        "sessionList": res.json().get("sessionList", [])
    }


@app.get("/student/details")
def student_details(regNo: str, session: str):
    token = get_odpay_token()
    return fetch_student_details(regNo, session, token)
