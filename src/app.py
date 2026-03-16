"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
import os
from pathlib import Path
import secrets

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

security = HTTPBasic()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Team training sessions and interschool soccer matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice basketball fundamentals and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
    },
    "School Choir": {
        "description": "Develop vocal techniques and perform at school events",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["mia@mergington.edu", "amelia@mergington.edu"]
    },
    "Painting Workshop": {
        "description": "Explore painting styles and create original artwork",
        "schedule": "Fridays, 2:30 PM - 4:00 PM",
        "max_participants": 18,
        "participants": ["charlotte@mergington.edu", "harper@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and present science fair projects",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["henry@mergington.edu", "lucas@mergington.edu"]
    },
    "Debate Team": {
        "description": "Build argumentation skills and participate in debate competitions",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["evelyn@mergington.edu", "abigail@mergington.edu"]
    }
}

# Simple in-memory credentials and records used for the exercise.
registered_students = {
    "michael@mergington.edu": "student123",
    "daniel@mergington.edu": "student123",
    "emma@mergington.edu": "student123",
    "sophia@mergington.edu": "student123",
    "john@mergington.edu": "student123",
    "olivia@mergington.edu": "student123",
    "liam@mergington.edu": "student123",
    "noah@mergington.edu": "student123",
    "ava@mergington.edu": "student123",
    "isabella@mergington.edu": "student123",
    "mia@mergington.edu": "student123",
    "amelia@mergington.edu": "student123",
    "charlotte@mergington.edu": "student123",
    "harper@mergington.edu": "student123",
    "henry@mergington.edu": "student123",
    "lucas@mergington.edu": "student123",
    "evelyn@mergington.edu": "student123",
    "abigail@mergington.edu": "student123"
}

teacher_accounts = {
    "teacher": "teacher123"
}

notifications_log = []
grades = {}


class ActivityCreate(BaseModel):
    description: str
    schedule: str
    max_participants: int = Field(gt=0)
    participants: list[EmailStr] = Field(default_factory=list)


class ActivityUpdate(BaseModel):
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: Optional[int] = Field(default=None, gt=0)


class GradeInput(BaseModel):
    score: float = Field(ge=0, le=100)
    comments: Optional[str] = None


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_activity_or_404(activity_name: str):
    activity = activities.get(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


def unauthorized_exception(detail: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Basic"}
    )


def get_authenticated_student(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    email = normalize_email(credentials.username)
    expected_password = registered_students.get(email)

    if expected_password is None:
        raise unauthorized_exception("Student account not found")

    if not secrets.compare_digest(credentials.password, expected_password):
        raise unauthorized_exception("Invalid student credentials")

    return email


def get_authenticated_teacher(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    teacher_name = credentials.username.strip()
    expected_password = teacher_accounts.get(teacher_name)

    if expected_password is None:
        raise unauthorized_exception("Teacher account not found")

    if not secrets.compare_digest(credentials.password, expected_password):
        raise unauthorized_exception("Invalid teacher credentials")

    return teacher_name


def send_confirmation_email(email: str, activity_name: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    notifications_log.append({
        "to": email,
        "subject": f"Activity signup confirmation: {activity_name}",
        "message": f"You are now registered in {activity_name}.",
        "sent_at": timestamp
    })


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: EmailStr,
    authenticated_email: str = Depends(get_authenticated_student)
):
    """Sign up a student for an activity"""
    activity = get_activity_or_404(activity_name)
    normalized_email = normalize_email(str(email))

    if normalized_email != authenticated_email:
        raise HTTPException(
            status_code=403,
            detail="Authenticated student can only sign up with their own email"
        )

    if normalized_email in activity["participants"]:
        raise HTTPException(
            status_code=409,
            detail=f"Student {normalized_email} is already registered for {activity_name}"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail=f"{activity_name} is full")

    activity["participants"].append(normalized_email)
    send_confirmation_email(normalized_email, activity_name)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def cancel_signup(
    activity_name: str,
    email: EmailStr,
    authenticated_email: str = Depends(get_authenticated_student)
):
    """Cancel a student registration for an activity"""
    activity = get_activity_or_404(activity_name)
    normalized_email = normalize_email(str(email))

    if normalized_email != authenticated_email:
        raise HTTPException(
            status_code=403,
            detail="Authenticated student can only cancel their own registration"
        )

    if normalized_email not in activity["participants"]:
        raise HTTPException(
            status_code=404,
            detail=f"Student {normalized_email} is not registered for {activity_name}"
        )

    activity["participants"].remove(normalized_email)
    return {"message": f"Cancelled signup for {normalized_email} in {activity_name}"}


@app.get("/activities/{activity_name}/participants")
def get_activity_participants(activity_name: str):
    """Get the participant list for an activity"""
    activity = get_activity_or_404(activity_name)
    return {
        "activity": activity_name,
        "participants": activity["participants"],
        "count": len(activity["participants"]),
        "max_participants": activity["max_participants"]
    }


@app.get("/notifications")
def get_notifications(teacher: str = Depends(get_authenticated_teacher)):
    """List simulated confirmation notifications"""
    return {"requested_by": teacher, "notifications": notifications_log}


@app.post("/admin/activities")
def create_activity(
    activity_name: str,
    payload: ActivityCreate,
    teacher: str = Depends(get_authenticated_teacher)
):
    """Create a new activity (teacher only)"""
    if activity_name in activities:
        raise HTTPException(status_code=409, detail="Activity already exists")

    participants = [normalize_email(str(email)) for email in payload.participants]
    if len(participants) > payload.max_participants:
        raise HTTPException(status_code=400, detail="Participants exceed max_participants")

    activities[activity_name] = {
        "description": payload.description,
        "schedule": payload.schedule,
        "max_participants": payload.max_participants,
        "participants": participants
    }
    return {"message": f"Activity {activity_name} created", "created_by": teacher}


@app.put("/admin/activities/{activity_name}")
def update_activity(
    activity_name: str,
    payload: ActivityUpdate,
    teacher: str = Depends(get_authenticated_teacher)
):
    """Update an activity (teacher only)"""
    activity = get_activity_or_404(activity_name)

    if payload.max_participants is not None and payload.max_participants < len(activity["participants"]):
        raise HTTPException(
            status_code=400,
            detail="max_participants cannot be lower than current participant count"
        )

    if payload.description is not None:
        activity["description"] = payload.description
    if payload.schedule is not None:
        activity["schedule"] = payload.schedule
    if payload.max_participants is not None:
        activity["max_participants"] = payload.max_participants

    return {"message": f"Activity {activity_name} updated", "updated_by": teacher}


@app.delete("/admin/activities/{activity_name}")
def delete_activity(activity_name: str, teacher: str = Depends(get_authenticated_teacher)):
    """Delete an activity (teacher only)"""
    get_activity_or_404(activity_name)
    activities.pop(activity_name)
    grades.pop(activity_name, None)
    return {"message": f"Activity {activity_name} deleted", "deleted_by": teacher}


@app.put("/admin/activities/{activity_name}/grades")
def evaluate_participation(
    activity_name: str,
    email: EmailStr,
    payload: GradeInput,
    teacher: str = Depends(get_authenticated_teacher)
):
    """Create or update a participation grade for a student (teacher only)"""
    activity = get_activity_or_404(activity_name)
    normalized_email = normalize_email(str(email))

    if normalized_email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Student is not registered in this activity")

    grades.setdefault(activity_name, {})
    grades[activity_name][normalized_email] = {
        "score": payload.score,
        "comments": payload.comments,
        "evaluated_by": teacher,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }

    return {"message": f"Grade saved for {normalized_email} in {activity_name}"}


@app.get("/admin/activities/{activity_name}/grades")
def get_participation_grades(
    activity_name: str,
    teacher: str = Depends(get_authenticated_teacher)
):
    """Get all participation grades for an activity (teacher only)"""
    get_activity_or_404(activity_name)
    return {
        "activity": activity_name,
        "requested_by": teacher,
        "grades": grades.get(activity_name, {})
    }
