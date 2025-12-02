import threading
from datetime import datetime

import ttkbootstrap as ttk

from api import APIError


# *================ TRASH PAGE =====================*
class TrashPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.button = ttk.Button(self, text="I took the trash out", command=self.trashOut)
    self.button.pack(pady=10)

    self.titleTrash = ttk.Label(self, text="Who took the trash out?", font=("Helvetica", 18))
    self.titleTrash.pack(pady=10)

    self.latestLabel = ttk.Label(self, text="", font=("Helvetica", 14))
    self.latestLabel.pack(pady=10)

    self.statusLabel = ttk.Label(self, text="", font=("Helvetica", 12))
    self.statusLabel.pack()

    self.historyFrame = ttk.Frame(self)
    self.historyFrame.pack(fill="both", expand=True)

  def onShow(self):
    self.refresh_history()

  def trashOut(self):
    user_id = self.controller.current_user_id
    if user_id is None:
      self.statusLabel.config(text="Error: Please recognize a user first.")
      return

    try:
      category_id = self.controller.get_category_id("Trash")
    except APIError as exc:
      self.statusLabel.config(text=f"Error: {exc}")
      return

    if category_id is None:
      self.statusLabel.config(text="Error: 'Trash' category not found.")
      return

    self.button.config(state="disabled", text="Logging...")
    self.statusLabel.config(text="Capturing photo...")
    threading.Thread(
      target=self._submit_trash_event, args=(user_id, category_id), daemon=True
    ).start()

  def _submit_trash_event(self, user_id: int, category_id: int):
    try:
      photo = self.controller.capture_snapshot()
      payload = {
        "user_id": user_id,
        "category_id": category_id,
        "notes": "Took out the trash",
      }
      self.controller.api.create_event(payload, photo)
      self.after(0, lambda: self.statusLabel.config(text="Trash event logged!"))
      self.after(0, self.refresh_history)
    except (RuntimeError, APIError) as exc:
      self.after(0, lambda: self.statusLabel.config(text=f"Error: {exc}"))
    finally:
      self.after(
        0,
        lambda: self.button.config(state="normal", text="I took the trash out"),
      )

  def refresh_history(self):
    self.statusLabel.config(text="Loading history...")
    threading.Thread(target=self._load_history, daemon=True).start()

  def _load_history(self):
    try:
      events = self.controller.api.get_events(category_name="Trash", limit=8)
      self.after(0, lambda: self._render_history(events))
      self.after(0, lambda: self.statusLabel.config(text=""))
    except APIError as exc:
      self.after(0, lambda: self.statusLabel.config(text=f"Error: {exc}"))

  def _render_history(self, events):
    for widget in self.historyFrame.winfo_children():
      widget.destroy()

    ttk.Label(self.historyFrame, text="Previous Records:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    if not events:
      self.latestLabel.config(text="No trash records yet.")
      ttk.Label(self.historyFrame, text="No records yet.", font=("Helvetica", 12)).pack(anchor="w", padx=20)
      return

    latest = events[0]
    latest_time = self._format_time(latest.get("logged_at"))
    self.latestLabel.config(text=f"🗑 {latest['user']['name']} at {latest_time}")

    for event in events[1:]:
      t = self._format_time(event.get("logged_at"))
      ttk.Label(
        self.historyFrame,
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
