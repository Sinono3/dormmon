import threading

import ttkbootstrap as ttk
from api import APIError

from typing import List

#*================ BALANCE PAGE =====================*
class BalancePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller
    self.paySaveBtn = None
    self.payAmountButtons = []
    self.title_font = ("Helvetica", 18, "bold")
    self.label_font = ("Helvetica", 14)
    self.input_font = ("Helvetica", 14)
    self.button_font = ("Helvetica", 13, "bold")
    self.status_font = ("Helvetica", 13, "italic")
    self.table_header_font = ("Helvetica", 18, "bold")
    self.table_row_font = ("Helvetica", 15)

    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    self.statusLabel = ttk.Label(self, text="", font=self.status_font)
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

    ttk.Label(self.payForm, text="Record Payment", font=self.title_font).pack(pady=4)

    topRow = ttk.Frame(self.payForm)
    topRow.pack(fill="x", padx=6, pady=6)
    for col in range(3):
      topRow.columnconfigure(col, weight=1, uniform="payrow")

    # From column
    fromCol = ttk.Frame(topRow)
    fromCol.grid(row=0, column=0, sticky="nsew", padx=3)
    ttk.Label(fromCol, text="From:", font=self.label_font).pack(anchor="w")
    self.fromBox = ttk.Combobox(fromCol, state="readonly", font=self.input_font)
    self.fromBox.pack(fill="x", pady=(2, 0))

    # To column
    toCol = ttk.Frame(topRow)
    toCol.grid(row=0, column=1, sticky="nsew", padx=3)
    ttk.Label(toCol, text="To:", font=self.label_font).pack(anchor="w")
    self.toBox = ttk.Combobox(toCol, state="readonly", font=self.input_font)
    self.toBox.pack(fill="x", pady=(2, 0))

    # Amount column
    amtCol = ttk.Frame(topRow)
    amtCol.grid(row=0, column=2, sticky="nsew", padx=3)
    ttk.Label(amtCol, text="Amount:", font=self.label_font).pack(anchor="w")
    self.amountEntry = ttk.Entry(amtCol, font=self.input_font)
    self.amountEntry.pack(fill="x", pady=(2, 0))

    # --- AMOUNT BUTTON ROW ---
    btnFrame = ttk.Frame(amtCol)
    btnFrame.pack(fill="x", pady=4)
    self.payAmountButtons = []

    # helper - must be at SAME indentation as button creation
    def add_amount(v):
      try:
        current = float(self.amountEntry.get() or 0)
      except ValueError:
        current = 0
      self.amountEntry.delete(0, "end")
      self.amountEntry.insert(0, str(current + v))

    # BUTTONS (correct indentation)
    for val in (1, 10, 50, 100):
      btn = ttk.Button(btnFrame, text=f"+{val}", command=lambda v=val: add_amount(v), padding=4, bootstyle="info", width=5)
      btn.pack(side="left", expand=True, fill="x", padx=1)
      self.payAmountButtons.append(btn)
    clr_btn = ttk.Button(btnFrame, text="CLR", bootstyle="danger",
               command=lambda: self.amountEntry.delete(0, "end"), padding=4, width=5)
    clr_btn.pack(side="left", expand=True, fill="x", padx=1)
    self.payAmountButtons.append(clr_btn)

    actionRow = ttk.Frame(self.payForm)
    actionRow.pack(fill="x", padx=6, pady=6)
    self.paySaveBtn = ttk.Button(
      actionRow,
      text="Save",
      width=8,
      bootstyle="success",
      padding=8,
      command=self.save_payment,
    )
    self.paySaveBtn.pack(side="right", padx=4)
    cancel_btn = ttk.Button(actionRow, text="Cancel", bootstyle="danger", command=self.hide_pay_form, padding=8, width=8)
    cancel_btn.pack(side="left", padx=4)

    # Fill names
    if hasattr(self.controller, "users"):
      names = [u["name"] for u in self.controller.users]
      self.fromBox["values"] = names
      self.toBox["values"] = names

    # PAY FORM APPEARS HERE ✔
    self.payForm.place(x=0, y=0, width=480, height=320)



  def hide_pay_form(self):
    self.payForm.place_forget()

  def save_payment(self):
    if not hasattr(self, "fromBox"):
      return

    frm_name = (self.fromBox.get() or "").strip()
    to_name = (self.toBox.get() or "").strip()
    amount_raw = (self.amountEntry.get() or "").strip()

    if not frm_name or not to_name:
      self.statusLabel.config(text="Select both users.")
      return

    if frm_name == to_name:
      self.statusLabel.config(text="Choose different users.")
      return

    try:
      amount_value = float(amount_raw)
    except ValueError:
      self.statusLabel.config(text="Enter a valid amount.")
      return

    amount_int = int(round(amount_value))
    if amount_int <= 0:
      self.statusLabel.config(text="Amount must be positive.")
      return

    try:
      from_user = self._get_user_by_name(frm_name)
      to_user = self._get_user_by_name(to_name)
    except APIError as exc:
      self.statusLabel.config(text=f"Error: {exc}")
      return

    if not from_user or not to_user:
      self.statusLabel.config(text="Invalid user selection.")
      return

    payload = {
      "from_user_id": from_user["id"],
      "to_user_id": to_user["id"],
      "amount": amount_int,
    }

    self.statusLabel.config(text="Recording payment...")
    self._set_pay_form_enabled(False)
    threading.Thread(target=self._submit_payment, args=(payload,), daemon=True).start()


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
    header.pack(fill="x", pady=(0, 6))
    ttk.Label(header, text="Name", width=10, anchor="w", font=self.table_header_font).pack(side="left")
    ttk.Label(header, text="Balance", width=15, anchor="w", font=self.table_header_font).pack(side="left")
    ttk.Label(header, text="Status", anchor="w", font=self.table_header_font).pack(side="left", fill="x", expand=True)

    if not users:
      ttk.Label(self.tableFrame, text="No users found.", anchor="w", font=self.table_row_font).pack(fill="x")
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

      ttk.Label(row, text=user["name"], width=10, anchor="w", font=self.table_row_font).pack(side="left")
      ttk.Label(
        row,
        text=f"${balance:.2f}",
        width=15,
        anchor="w",
        bootstyle=color,
        font=self.table_row_font,
      ).pack(side="left")
      ttk.Label(row, text=status_text, anchor="w", font=self.table_row_font).pack(side="left", fill="x", expand=True)
  
  def _set_pay_form_enabled(self, enabled: bool):
    if self.paySaveBtn:
      self.paySaveBtn.config(state="normal" if enabled else "disabled")
    state_entry = "normal" if enabled else "disabled"
    combo_state = "readonly" if enabled else "disabled"
    if hasattr(self, "amountEntry"):
      self.amountEntry.config(state=state_entry)
    if hasattr(self, "fromBox"):
      self.fromBox.config(state=combo_state)
    if hasattr(self, "toBox"):
      self.toBox.config(state=combo_state)
    for btn in getattr(self, "payAmountButtons", []):
      btn.config(state="normal" if enabled else "disabled")

  def _get_user_by_name(self, name: str):
    user = next((u for u in self.controller.users if u["name"] == name), None)
    if user is None:
      users = self.controller.refresh_users()
      user = next((u for u in users if u["name"] == name), None)
    return user

  def _submit_payment(self, payload: dict):
    try:
      self.controller.api.record_payment(**payload)
      self.controller.refresh_users()
      self.after(0, self.load_balances)
      self.after(0, self.hide_pay_form)
      self.after(0, lambda: self.statusLabel.config(text="Payment recorded!"))
    except APIError as exc:
      self.after(0, lambda: self.statusLabel.config(text=f"Error: {exc}"))
    finally:
      self.after(0, lambda: self._set_pay_form_enabled(True))
