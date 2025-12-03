from datetime import datetime, timedelta
from typing import Dict, List

from flask import render_template

from database_access import (
    category_get_by_name,
    event_get_latest_by_category,
    event_user_has_category_entry_since,
    user_get_all,
)
from response_helpers import json_response, wants_json_response

TRASH_CATEGORY_NAME = "Trash"
CLEANING_CATEGORY_NAME = "Room Cleaning"
ROTATION_DAY_OF_WEEK = 5  # 5 = Saturday
RECENT_CLEANING_WINDOW_DAYS = 6


def routes(app):
    @app.route("/status_view")
    def status_view():
        status = _get_task_status()

        if wants_json_response():
            return json_response(status)

        return render_template(
            "dialogs/task_status.html",
            cleaning_status=status["cleaning"],
            trash_status=status["trash"],
        )

    @app.route("/schedule")
    def schedule_view():
        schedule = _get_cleaning_schedule()

        if wants_json_response():
            return json_response({"schedule": schedule})

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

    delta = datetime.now() - last_event.logged_at
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
            "message": "Category missing.",
        }

    schedule = _get_cleaning_schedule(weeks=1)
    if not schedule:
        return {
            "name": "Room Cleaning",
            "icon": "⚪",
            "message": "Add users to start.",
        }

    current_assignment = schedule[0]
    assigned_user_id = current_assignment["user_id"]
    assigned_user_name = current_assignment["user"]
    
    # Buscamos si esa persona ha limpiado RECIENTEMENTE (esta semana)
    since = datetime.now() - timedelta(days=RECENT_CLEANING_WINDOW_DAYS)
    completed = event_user_has_category_entry_since(assigned_user_id, category, since)

    if completed:
        icon = "✅"
        message = f"{assigned_user_name} completed their turn."
    else:
        # Lógica de retraso:
        # Calculamos la fecha límite (sábado a las 12:00 PM por ejemplo, o fin del día)
        # Aquí usaremos la lógica de _next_rotation_date para ver si ya nos pasamos
        now = datetime.now()
        limit_date = _next_rotation_date() # Próximo sábado
        
        # Si hoy es mayor a la fecha del turno y NO se ha hecho...
        # Nota: Como _next_rotation_date siempre da el futuro, necesitamos ver
        # si estamos en el periodo de "espera" o si ya es tarde.
        
        # Simplificación: Comparamos contra el ultimo sábado.
        # Si hoy es Martes, y el turno era el Sábado pasado...
        today = datetime.now().date()
        target_date_str = current_assignment["date"].split(" ")[0] # "2025-11-29"
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        
        # Si la fecha que muestra el calendario ya pasó y no hay evento:
        if today > target_date:
            days_late = (today - target_date).days
            icon = "🔴"
            message = f"{assigned_user_name} is late by {days_late} days!"
        else:
            icon = "⚠️"
            message = f"Pending: {assigned_user_name}'s turn ({target_date_str})."

    return {"name": "Room Cleaning", "icon": icon, "message": message}

def _get_cleaning_schedule(weeks: int = 6) -> List[Dict[str, str]]:
    users = list(user_get_all())
    if not users:
        return []

    category = category_get_by_name(CLEANING_CATEGORY_NAME)
    
    last_cleaner_id = None
    last_event_time = None

    if category:
        last_event = event_get_latest_by_category(category)
        if last_event:
            last_cleaner_id = last_event.user.id
            last_event_time = last_event.logged_at

    user_ids = [user.id for user in users]
    
    # Fecha del PRÓXIMO sábado (limite de esta semana)
    next_rotation_date = _next_rotation_date()
    # Fecha del sábado PASADO (inicio del ciclo actual)
    current_cycle_start = next_rotation_date - timedelta(days=7)
    # Fecha del sábado ANTEPASADO (inicio del ciclo anterior)
    previous_cycle_start = current_cycle_start - timedelta(days=7)

    start_index = 0

    if last_cleaner_id in user_ids:
        current_cleaner_index = user_ids.index(last_cleaner_id)

        # CASO 1: Alguien limpió esta semana (adelantado o a tiempo).
        # El turno se queda en ella para mostrar "Completado".
        if last_event_time and last_event_time.date() > current_cycle_start:
            start_index = current_cleaner_index
        
        # CASO 2: La última limpieza fue la semana pasada (ciclo normal).
        # Toca rotar al siguiente.
        elif last_event_time and last_event_time.date() > previous_cycle_start:
            start_index = (current_cleaner_index + 1) % len(users)
            
        # CASO 3: La última limpieza es muy vieja (hace más de dos semanas).
        # Significa que alguien NO limpió la semana pasada.
        # El turno se queda "trabado" en la persona que le tocaba la semana pasada.
        else:
            # Calculamos a quién le tocaba basándonos en el último que sí cumplió
            # Si el último fue hace 2 semanas, le tocaba al siguiente de él.
            # Y como no lo hizo, el sistema se queda esperándolo a él.
            start_index = (current_cleaner_index + 1) % len(users)

    schedule = []
    current_index = start_index
    
    for i in range(weeks):
        # Si es el primer item de la lista (el turno actual) y estamos atrasados,
        # mostramos la fecha vieja en la que debió limpiar.
        if i == 0 and last_event_time and last_event_time.date() <= previous_cycle_start:
             # Mostramos la fecha del sábado pasado que se perdió
             rotation_date = current_cycle_start + timedelta(days=7) # = next_rotation_date actual
             # Nota visual: Podrías querer restar días aquí si quieres mostrar la fecha pasada
        else:
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
    now = reference or datetime.now()
    today = now.date()
    days_until_rotation = (ROTATION_DAY_OF_WEEK - today.weekday() + 7) % 7
    rotation_date = today + timedelta(days=days_until_rotation)
    if days_until_rotation == 0 and now.hour >= 12:
        rotation_date += timedelta(days=7)
    return rotation_date


