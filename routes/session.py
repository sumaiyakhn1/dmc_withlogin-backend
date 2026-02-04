from fastapi import APIRouter, Query
from services.odpay_service import get_session_list

router = APIRouter()

@router.post("/session")
def fetch_sessions(regNo: str = Query(...)):
    sessions = get_session_list(regNo)
    return {
        "regNo": regNo,
        "sessionList": sessions
    }
