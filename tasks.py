from datetime import datetime, timedelta
from typing import Dict, List
#ola
from flask import render_template

from database_access import (
    category_get_by_name,
    event_get_latest_by_category,
    event_user_has_category_entry_since,
    user_get_all,
)

TRASH_CATEGORY_NAME = "Trash"
CLEANING_CATEGORY_NAME = "Room Cleaning"
ROTATION_DAY_OF_WEEK = 5  # 5 = Saturday
RECENT_CLEANING_WINDOW_DAYS = 6


def routes(app):
    @app.route("/status_view")
    def status_view():
        status = _get_task_status()
        return render_template(
            "dialogs/task_status.html",
            cleaning_status=status["cleaning"],
            trash_status=status["trash"],
        )

    @app.route("/schedule")
    def schedule_view():
        schedule = _get_cleaning_schedule()
        return render_template("dialogs/cleaning_schedule.html", schedule=schedule)


def _get_task_status() -> Dict[str, Dict[str, str]]:
    trash_status = _build_trash_status()
    cleaning_status = _build_cleaning_status()
    return {"trash": trash_status, "cleaning": cleaning_status}


def _build_trash_status() -> Dict[str, str]:
    category = category_get_by_name(TRASH_CATEGORY_NAME)
    if not category:
        return {
            "name": "Trash",
            "icon": "⚪",
            "message": "Category missing. Add a 'Trash' category to enable tracking.",
        }

    last_event = event_get_latest_by_category(category)
    if not last_event:
        return {
            "name": "Trash",
            "icon": "🔴",
            "message": "Never registered.",
        }

    delta = datetime.utcnow() - last_event.logged_at
    if delta.days < 1:
        hours = int(delta.total_seconds() // 3600)
        icon = "🟢"
        message = f"Done by {last_event.user.name} ({hours}h ago)."
    elif delta.days < 2:
        icon = "🟡"
        message = f"Done yesterday by {last_event.user.name}."
    else:
        icon = "🔴"
        message = f"Not done for {delta.days} days!"

    return {"name": "Trash", "icon": icon, "message": message}


def _build_cleaning_status() -> Dict[str, str]:
    category = category_get_by_name(CLEANING_CATEGORY_NAME)
    if not category:
        return {
            "name": "Room Cleaning",
            "icon": "⚪",
            "message": "Category missing. Add 'Room Cleaning' to start rotation.",
        }

    schedule = _get_cleaning_schedule(weeks=1)
    if not schedule:
        return {
            "name": "Room Cleaning",
            "icon": "⚪",
            "message": "Add users to start rotation.",
        }

    current_assignment = schedule[0]
    assigned_user_id = current_assignment["user_id"]
    since = datetime.utcnow() - timedelta(days=RECENT_CLEANING_WINDOW_DAYS)
    completed = event_user_has_category_entry_since(assigned_user_id, category, since)

    if completed:
        icon = "✅"
        message = f"{current_assignment['user']} completed their turn."
    else:
        icon = "⚠️"
        message = f"Pending: {current_assignment['user']}'s turn."

    return {"name": "Room Cleaning", "icon": icon, "message": message}


def _get_cleaning_schedule(weeks: int = 6) -> List[Dict[str, str]]:
    users = list(user_get_all())
    if not users:
        return []

    category = category_get_by_name(CLEANING_CATEGORY_NAME)
    last_cleaner_id = None
    if category:
        last_event = event_get_latest_by_category(category)
        if last_event:
            last_cleaner_id = last_event.user.id

    user_ids = [user.id for user in users]
    if last_cleaner_id in user_ids:
        start_index = (user_ids.index(last_cleaner_id) + 1) % len(users)
    else:
        start_index = 0

    next_rotation_date = _next_rotation_date()
    schedule = []
    current_index = start_index
    for i in range(weeks):
        rotation_date = next_rotation_date + timedelta(weeks=i)
        assigned_user = users[current_index]
        schedule.append(
            {
                "date": rotation_date.strftime("%Y-%m-%d (%a)"),
                "user": assigned_user.name,
                "user_id": assigned_user.id,
            }
        )
        current_index = (current_index + 1) % len(users)

    return schedule


def _next_rotation_date(reference: datetime = None):
    now = reference or datetime.utcnow()
    today = now.date()
    days_until_rotation = (ROTATION_DAY_OF_WEEK - today.weekday() + 7) % 7
    rotation_date = today + timedelta(days=days_until_rotation)
    if days_until_rotation == 0 and now.hour >= 12:
        rotation_date += timedelta(days=7)
    return rotation_date

