from datetime import datetime
import tkinter as tk
import ttkbootstrap as ttk

# *================ TRASH PAGE =====================*
class TrashPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    # Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.button = ttk.Button(self, text="I took the trash out", command=self.trashOut)
    self.button.pack(pady=10)

    # Title
    self.titleTrash = ttk.Label(self, text="Who took the trash out?", font=("Helvetica", 18))
    self.titleTrash.pack(pady=10)

    # Latest record
    self.latestLabel = ttk.Label(self, text="", font=("Helvetica", 14))
    self.latestLabel.pack(pady=10)

    # History frame
    self.historyFrame = ttk.Frame(self)
    self.historyFrame.pack(fill="both", expand=True)

  def trashOut(self):
    user = self.controller.current_user

    if user is None:
        self.latestLabel.config(text="Error: No user recognized")
        return

    # Create new record
    t = datetime.now().strftime("%Y-%m-%d  %H:%M")
    record = {"user": user, "time": t}

    # Add newest first
    self.controller.trash_log.insert(0, record)

    # Update latest record
    self.latestLabel.config(text=f"🗑 {user} took out the trash at {t}")

    self.controller.members[user] += 1

    self.show_history()

  def onShow(self):
    """Called every time this page becomes visible."""
    # Refresh the list
    self.show_history()

  def show_history(self):
    """Redraw the list of previous trash records."""
    # Clear previous widgets
    for widget in self.historyFrame.winfo_children():
      widget.destroy()

    ttk.Label(self.historyFrame, text="Previous Records:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    if not self.controller.trash_log:
      ttk.Label(self.historyFrame, text="No records yet.", font=("Helvetica", 12)).pack(anchor="w", padx=20)
      return

    # Skip index 0 (latest)
    for item in self.controller.trash_log[1:]:
      ttk.Label(self.historyFrame, text=f"{item['user']} — {item['time']}", font=("Helvetica", 12)).pack(anchor="w", padx=20)

    

