from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os

# -------------------------------------------------
# Force Docs + OpenAPI enabled (important)
# -------------------------------------------------
app = FastAPI(
    title="Student Login API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# -------------------------------------------------
# Enable CORS (for frontend connection later)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Absolute path for Render
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "students.xlsx")


# -------------------------------------------------
# Request Model
# -------------------------------------------------
class LoginRequest(BaseModel):
    login_id: str
    password: str


# -------------------------------------------------
# Load Students
# -------------------------------------------------
def load_students():
    if not os.path.exists(EXCEL_FILE):
        raise HTTPException(status_code=500, detail="students.xlsx not found")

    df = pd.read_excel(EXCEL_FILE)

    df.columns = df.columns.str.strip()
    df["Scholar ID"] = df["Scholar ID"].astype(str).str.strip()
    df["Birthday"] = pd.to_datetime(df["Birthday"]).dt.strftime("%d-%b-%Y")

    return df


# -------------------------------------------------
# Root
# -------------------------------------------------
@app.get("/")
def home():
    return {"message": "Student Login API Running 🚀"}


# -------------------------------------------------
# Login
# -------------------------------------------------
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
