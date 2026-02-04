from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.session import router as session_router
from routes.student import router as student_router

app = FastAPI(title="Student Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(session_router, prefix="/student", tags=["Session"])
app.include_router(student_router, prefix="/student", tags=["Student"])

# --------------------------------------------------
# ROOT
# --------------------------------------------------
@app.get("/")
def health():
    return {"status": "Backend running 🚀"}
