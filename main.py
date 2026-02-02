from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

# Absolute path (important for Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "students.xlsx")


class LoginRequest(BaseModel):
    login_id: str
    password: str


def load_students():
    if not os.path.exists(EXCEL_FILE):
        raise HTTPException(status_code=500, detail="students.xlsx not found")

    df = pd.read_excel(EXCEL_FILE)

    df.columns = df.columns.str.strip()
    df["Scholar ID"] = df["Scholar ID"].astype(str).str.strip()
    df["Birthday"] = pd.to_datetime(df["Birthday"]).dt.strftime("%d-%b-%Y")

    return df


@app.get("/")
def home():
    return {"message": "Student Login API Running 🚀"}


@app.post("/login")
def login(data: LoginRequest):

    df = load_students()

    login_id = data.login_id.strip()
    password = data.password.strip()

    student = df[
        (df["Scholar ID"] == login_id) &
        (df["Birthday"] == password)
    ]

    if student.empty:
        raise HTTPException(status_code=401, detail="Invalid ID or Password")

    student_data = student.iloc[0].to_dict()
    student_data.pop("Birthday", None)

    return {
        "message": "Login Successful",
        "student": student_data
    }
