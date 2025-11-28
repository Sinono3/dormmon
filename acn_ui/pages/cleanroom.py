from datetime import datetime
import tkinter as tk
import ttkbootstrap as ttk

# *================ CLEAN ROOM PAGE =====================*
class CleanroomPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller


    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.button = ttk.Button(self, text="I cleaned the room", command=self.cleanedRoom)
    self.button.pack(pady=10)

    #Labels
    self.latest = ttk.Label(self, text="", font=("Helvetica", 14))
    self.latest.pack(pady=5)

    self.next = ttk.Label(self, text="", font=("Helvetica", 14))
    self.next.pack(pady=5)

    #Frame for roaster
    self.rosterFrame = ttk.Frame(self)
    self.rosterFrame.pack(fill="both", expand=True)
  
  def cleanedRoom(self):
    user = self.controller.current_user
    if user is None:
      self.latest.config(text="Error: No user recognized")
      return

    t = datetime.now().strftime("%Y-%m-%d  %H:%M")
    record = {"user": user, "time": t}

    self.controller.clean_log.insert(0, record)

    self.latest.config(text=f"🧹 {user} cleaned the room at {t}")

    self.controller.members[user] += 1

    self.showRoster()

  def onShow(self):
    """Refresh roster every time page is shown."""
    self.showRoster()

  def showRoster(self):
    """Redraw the list of previous clean records."""
    # Clear previous widgets
    for widget in self.rosterFrame.winfo_children():
      widget.destroy()
    
    members = self.controller.members

    # Sort by who has cleaned the least
    sortedMembers = sorted(members.items(), key=lambda x: x[1])

    nextPerson = sortedMembers[0][0]

    ttk.Label(self.rosterFrame, text="Cleaning History:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    self.next.config(text=f"Next to clean: {nextPerson}", bootstyle="warning")

    if not self.controller.clean_log:
      ttk.Label(self.rosterFrame, text="No cleaning records yet.", font=("Helvetica", 12)).pack(anchor="w", padx=20)
      return

    # Skip index 0 (latest)
    for item in self.controller.clean_log:
      ttk.Label(self.rosterFrame, text=f"{item['user']} — {item['time']}", font=("Helvetica", 12)).pack(anchor="w", padx=20)

