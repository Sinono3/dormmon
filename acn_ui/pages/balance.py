import ttkbootstrap as ttk
from api import APIError

from typing import List

#*================ BALANCE PAGE =====================*
class BalancePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.statusLabel = ttk.Label(self, text="", font=("Helvetica", 14))
    self.statusLabel.pack(pady=5)

    self.tableFrame = ttk.Frame(self)
    self.tableFrame.pack(fill="both", expand=True, padx=10, pady=10)

    # SMALL DROPDOWN MENU (hidden initially)
    self.menuFrame = ttk.Frame(self, relief="raised", borderwidth=2)

    # ⋮ MENU BUTTON
    self.menuBtn = ttk.Button(self, image=controller.menuIm, width=3, command=self.toggle_menu)
    self.menuBtn.place(x=5, y=5)

    ttk.Button(self.menuFrame, text="Pay", command=self.show_pay_form).pack(fill="x")
    ttk.Button(self.menuFrame, text="Refresh", command=self.onShow).pack(fill="x")
    ttk.Button(self.menuFrame, text="Close", command=self.toggle_menu).pack(fill="x")

    # PAY FORM (hidden)
    self.payForm = ttk.Frame(self, relief="groove", borderwidth=2)

  def toggle_menu(self):
    if self.menuFrame.winfo_ismapped():
      self.menuFrame.place_forget()
    else:
      # place below the ⋮ button
      self.menuFrame.place(x=5, y=40)

  def show_pay_form(self):
    self.toggle_menu()  # hide menu when choosing Pay

    # Clear form before drawing
    for w in self.payForm.winfo_children():
      w.destroy()

    ttk.Label(self.payForm, text="Pay", font=("Helvetica", 10, "bold")).pack(pady=2)

    ttk.Label(self.payForm, text="From:").pack(anchor="w", padx=5)
    self.fromBox = ttk.Combobox(self.payForm, state="readonly")
    self.fromBox.pack(fill="x", padx=5)

    ttk.Label(self.payForm, text="To:").pack(anchor="w", padx=5, pady=(3,0))
    self.toBox = ttk.Combobox(self.payForm, state="readonly")
    self.toBox.pack(fill="x", padx=5)

    ttk.Label(self.payForm, text="Amount:").pack(anchor="w", padx=5, pady=(3,0))
    self.amountEntry = ttk.Entry(self.payForm)
    self.amountEntry.pack(fill="x", padx=5)

    # --- AMOUNT BUTTON ROW ---
    btnFrame = ttk.Frame(self.payForm)
    btnFrame.pack(fill="x", padx=5, pady=5)

    # helper - must be at SAME indentation as button creation
    def add_amount(v):
      try:
        current = float(self.amountEntry.get() or 0)
      except ValueError:
        current = 0
      self.amountEntry.delete(0, "end")
      self.amountEntry.insert(0, str(current + v))

    # BUTTONS (correct indentation)
    ttk.Button(btnFrame, text="+1", command=lambda: add_amount(1)).pack(side="left", expand=True, fill="x", padx=1)
    ttk.Button(btnFrame, text="+10", command=lambda: add_amount(10)).pack(side="left", expand=True, fill="x", padx=1)
    ttk.Button(btnFrame, text="+100", command=lambda: add_amount(100)).pack(side="left", expand=True, fill="x", padx=1)
    ttk.Button(btnFrame, text="CLR", bootstyle="danger",
               command=lambda: self.amountEntry.delete(0, "end")).pack(
      side="left", expand=True, fill="x", padx=1
    )

    ttk.Button(self.payForm, text="Save", width=5, bootstyle="success", padding = 5, command=self.save_payment).pack(side="right", padx=5, pady=5)
    ttk.Button(self.payForm, text="Cancel", bootstyle="danger", command=self.hide_pay_form).pack(side="left", padx=5)

    # Fill names
    if hasattr(self.controller, "users"):
      names = [u["name"] for u in self.controller.users]
      self.fromBox["values"] = names
      self.toBox["values"] = names

    # PAY FORM APPEARS HERE ✔
    self.payForm.place(x=250, y=40, width=230, height=300)



  def hide_pay_form(self):
    self.payForm.place_forget()

  def save_payment(self):
    frm = self.fromBox.get()
    to = self.toBox.get()
    amt = self.amountEntry.get()

    print("Saving payment:", frm, "→", to, amt)

    # TODO: call your backend API here:
    # self.controller.api.record_payment(frm, to, amt)

    self.hide_pay_form()


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
    ttk.Label(header, text="Name", width=15, anchor="w", font=("Helvetica", 16, "bold")).pack(side="left")
    ttk.Label(header, text="Balance", width=15, anchor="w", font=("Helvetica", 16, "bold")).pack(side="left")
    ttk.Label(header, text="Status", anchor="w", font=("Helvetica", 16, "bold")).pack(side="left", fill="x", expand=True)

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
      
