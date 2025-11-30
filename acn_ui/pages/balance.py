from typing import List

import ttkbootstrap as ttk

from api import APIError


#*================ BALANCE PAGE =====================*
class BalancePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.statusLabel = ttk.Label(self, text="", font=("Helvetica", 12))
    self.statusLabel.pack(pady=5)

    self.tableFrame = ttk.Frame(self)
    self.tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

  def onShow(self):
    self.statusLabel.config(text="Loading balances...")
    self.after(50, self.load_balances)

  def load_balances(self):
    try:
      users = self.controller.refresh_users()
    except APIError as exc:
      self.statusLabel.config(text=f"Error: {exc}")
      self._clear_table()
      return

    self.statusLabel.config(text="")
    self._render_table(users)

  def _clear_table(self):
    for widget in self.tableFrame.winfo_children():
      widget.destroy()

  def _render_table(self, users: List[dict]):
    self._clear_table()

    header = ttk.Frame(self.tableFrame)
    header.pack(fill="x", pady=(0, 5))
    ttk.Label(header, text="Name", width=15, anchor="w", font=("Helvetica", 12, "bold")).pack(side="left")
    ttk.Label(header, text="Balance", width=15, anchor="w", font=("Helvetica", 12, "bold")).pack(side="left")
    ttk.Label(header, text="Status", anchor="w", font=("Helvetica", 12, "bold")).pack(side="left", fill="x", expand=True)

    if not users:
      ttk.Label(self.tableFrame, text="No users found.", anchor="w").pack(fill="x")
      return

    for user in users:
      balance = user.get("balance", 0) or 0
      if balance > 0:
        status_text = "owed to them"
        color = "success"
      elif balance < 0:
        status_text = "they owe"
        color = "danger"
      else:
        status_text = "settled"
        color = "info"

      row = ttk.Frame(self.tableFrame)
      row.pack(fill="x", pady=2)

      ttk.Label(row, text=user["name"], width=15, anchor="w").pack(side="left")
      ttk.Label(
        row,
        text=f"${balance:.2f}",
        width=15,
        anchor="w",
        bootstyle=color,
      ).pack(side="left")
      ttk.Label(row, text=status_text, anchor="w").pack(side="left", fill="x", expand=True)
