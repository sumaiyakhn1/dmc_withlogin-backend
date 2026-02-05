import requests
from fastapi import HTTPException

ENTITY_ID = "6608ec3120337200120f347e"
ODPAY_URL = "https://staging.odpay.in/api/view/student"


def fetch_student_details(regNo: str, session: str, token: str):
    res = requests.get(
        ODPAY_URL,
        headers={
            # IMPORTANT: raw token (no Bearer)
            "Authorization": token
        },
        params={
            "entity": ENTITY_ID,
            "session": session,
            "regNo": regNo
        },
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(res.status_code, res.text)

    data = res.json()

    return {
        "basic": {
            "name": data.get("name"),
            "regNo": data.get("regNo"),
            "gender": data.get("gender"),
            "dob": data.get("dob"),
            "phone": data.get("phone"),
            "email": data.get("email"),
        },
        "academic": {
            "course": data.get("course"),
            "stream": data.get("stream"),
            "batch": data.get("batch"),
            "section": data.get("section"),
            "session": data.get("session"),
        },
        "subjects": [
            {
                "name": s.get("name"),
                "code": s.get("code"),
                "mode": s.get("mode"),
            }
            for s in data.get("subjects", [])
        ],
        "fee": {
            "total": sum(d["amount"] for d in data.get("studentDemand", {}).get("demand", [])),
            "paid": sum(d["received"] for d in data.get("studentDemand", {}).get("demand", [])),
            "due": sum(d["amount"] - d["received"] for d in data.get("studentDemand", {}).get("demand", [])),
        }
    }
