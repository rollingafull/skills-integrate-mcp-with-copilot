"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

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
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        "waitlist": [],
        "favorites": [],
        "attendance": {}
    }
}


def get_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


def get_spots_left(activity: dict):
    return max(0, activity["max_participants"] - len(activity["participants"]))


def validate_attendance_status(status: str):
    if status not in {"present", "absent"}:
        raise HTTPException(status_code=400, detail="Attendance status must be 'present' or 'absent'")
    return status


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = get_activity(activity_name)

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if email in activity["waitlist"]:
        raise HTTPException(status_code=400, detail="Student is already on the waitlist")

    if get_spots_left(activity) > 0:
        activity["participants"].append(email)
        return {
            "message": f"Signed up {email} for {activity_name}",
            "status": "registered",
            "spots_left": get_spots_left(activity)
        }

    activity["waitlist"].append(email)
    return {
        "message": f"{activity_name} is full. {email} has been added to the waitlist.",
        "status": "waitlisted",
        "waitlist_position": len(activity["waitlist"])
    }


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activity = get_activity(activity_name)

    if email in activity["participants"]:
        activity["participants"].remove(email)
        promoted_student = None

        if activity["waitlist"]:
            promoted_student = activity["waitlist"].pop(0)
            activity["participants"].append(promoted_student)

        message = f"Unregistered {email} from {activity_name}."
        if promoted_student:
            message += f" {promoted_student} was moved from the waitlist into the activity."

        return {
            "message": message,
            "spots_left": get_spots_left(activity),
            "waitlist_length": len(activity["waitlist"])
        }

    if email in activity["waitlist"]:
        activity["waitlist"].remove(email)
        return {
            "message": f"Removed {email} from the waitlist for {activity_name}.",
            "waitlist_length": len(activity["waitlist"])
        }

    raise HTTPException(status_code=400, detail="Student is not registered or waitlisted for this activity")


@app.post("/activities/{activity_name}/favorite")
def favorite_activity(activity_name: str, email: str):
    activity = get_activity(activity_name)

    if email in activity["favorites"]:
        activity["favorites"].remove(email)
        return {
            "message": f"{email} removed {activity_name} from favorites",
            "favorite_count": len(activity["favorites"])
        }

    activity["favorites"].append(email)
    return {
        "message": f"{email} added {activity_name} to favorites",
        "favorite_count": len(activity["favorites"])
    }


@app.post("/activities/{activity_name}/attendance")
def track_attendance(activity_name: str, email: str, status: str):
    activity = get_activity(activity_name)

    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student must be registered for the activity to record attendance"
        )

    status = validate_attendance_status(status)
    activity["attendance"][email] = status
    return {
        "message": f"Recorded {email} as {status} for {activity_name}",
        "attendance": activity["attendance"]
    }
