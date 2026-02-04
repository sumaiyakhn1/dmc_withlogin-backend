from fastapi import APIRouter, Query
from services.odpay_service import get_student_details

router = APIRouter()

@router.get("/details")
def student_details(
    regNo: str = Query(...),
    session: str = Query(...)
):
    data = get_student_details(regNo, session)

    return {
        "name": data.get("name"),
        "gender": data.get("gender"),
        "dob": data.get("dob"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "fatherName": data.get("fatherName"),
        "motherName": data.get("motherName"),
        "course": data.get("course"),
        "stream": data.get("stream"),
        "batch": data.get("batch"),
        "section": data.get("section"),
        "regNo": data.get("regNo"),
        "session": session
    }
