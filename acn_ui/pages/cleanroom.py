import threading
from datetime import datetime

import ttkbootstrap as ttk

from api import APIError


# *================ CLEAN ROOM PAGE =====================*
class CleanroomPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.button = ttk.Button(self, text="I cleaned the room", command=self.cleanedRoom)
    self.button.pack(pady=10)

    self.latest = ttk.Label(self, text="", font=("Helvetica", 14))
    self.latest.pack(pady=5)

    self.next = ttk.Label(self, text="", font=("Helvetica", 14))
    self.next.pack(pady=5)

    self.statusLabel = ttk.Label(self, text="", font=("Helvetica", 12))
    self.statusLabel.pack()

    self.rosterFrame = ttk.Frame(self)
    self.rosterFrame.pack(fill="both", expand=True)
  
  def cleanedRoom(self):
    user_id = self.controller.current_user_id
    if user_id is None:
      self.statusLabel.config(text="Error: Please recognize a user first.")
      return

    try:
      category_id = self.controller.get_category_id("Room Cleaning")
    except APIError as exc:
      self.statusLabel.config(text=f"Error: {exc}")
      return

    if category_id is None:
      self.statusLabel.config(text="Error: 'Room Cleaning' category missing.")
      return

    self.button.config(state="disabled", text="Logging...")
    self.statusLabel.config(text="Capturing photo...")
    threading.Thread(
      target=self._submit_clean_event, args=(user_id, category_id), daemon=True
    ).start()

  def _submit_clean_event(self, user_id: int, category_id: int):
    try:
      photo = self.controller.capture_snapshot()
      payload = {
        "user_id": user_id,
        "category_id": category_id,
        "notes": "Room cleaned",
      }
      self.controller.api.create_event(payload, photo)
      self.after(0, lambda: self.statusLabel.config(text="Cleaning event logged!"))
      self.after(0, self.refresh_data)
    except (RuntimeError, APIError) as exc:
      self.after(0, lambda: self.statusLabel.config(text=f"Error: {exc}"))
    finally:
      self.after(
        0,
        lambda: self.button.config(state="normal", text="I cleaned the room"),
      )

  def onShow(self):
    """Refresh roster every time page is shown."""
    self.refresh_data()

  def refresh_data(self):
    self.statusLabel.config(text="Loading cleaning data...")
    threading.Thread(target=self._load_data, daemon=True).start()

  def _load_data(self):
    try:
      events = self.controller.api.get_events(
        category_name="Room Cleaning", limit=8
      )
      schedule = self.controller.api.get_schedule()
      self.after(0, lambda: self._render(events, schedule))
      self.after(0, lambda: self.statusLabel.config(text=""))
    except APIError as exc:
      self.after(0, lambda: self.statusLabel.config(text=f"Error: {exc}"))

  def _render(self, events, schedule):
    if events:
      latest = events[0]
      t = self._format_time(latest.get("logged_at"))
      self.latest.config(text=f"🧹 {latest['user']['name']} cleaned at {t}")
    else:
      self.latest.config(text="No cleaning records yet.")

    if schedule:
      next_assignment = schedule[0]
      self.next.config(
        text=f"Next to clean: {next_assignment['user']} ({next_assignment['date']})",
        bootstyle="warning",
      )
    else:
      self.next.config(text="No schedule available.", bootstyle="secondary")

    self._render_history(events)

  def _render_history(self, events):
    for widget in self.rosterFrame.winfo_children():
      widget.destroy()

    ttk.Label(self.rosterFrame, text="Cleaning History:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    if not events:
      ttk.Label(self.rosterFrame, text="No cleaning records yet.", font=("Helvetica", 12)).pack(anchor="w", padx=20)
      return

    for event in events:
      t = self._format_time(event.get("logged_at"))
      ttk.Label(
        self.rosterFrame,
        text=f"{event['user']['name']} — {t}",
        font=("Helvetica", 12),
      ).pack(anchor="w", padx=20)

  @staticmethod
  def _format_time(timestamp: str):
    try:
      dt = datetime.fromisoformat(timestamp)
      return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
      return timestamp
