import threading
import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from api import APIError

# *================ EXPENSE PAGE =====================*
class ExpensePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller
    self.savingExpense = False
    self.content_frame_id = None
    self.title_font = ("Helvetica", 20, "bold")
    self.label_font = ("Helvetica", 14)
    self.input_font = ("Helvetica", 14)
    self.button_font = ("Helvetica", 13, "bold")
    self.status_font = ("Helvetica", 12, "italic")

    self.contentCanvas = tk.Canvas(self, highlightthickness=0)
    self.contentCanvas.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
    self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.contentCanvas.yview)
    self.scrollbar.pack(side="right", fill="y", pady=8)
    self.contentCanvas.configure(yscrollcommand=self.scrollbar.set)

    self.contentFrame = ttk.Frame(self.contentCanvas)
    self.content_frame_id = self.contentCanvas.create_window((0, 0), window=self.contentFrame, anchor="nw")
    self.contentFrame.bind("<Configure>", lambda _: self._update_scroll_region())
    self.contentCanvas.bind("<Configure>", self._resize_canvas)
    self.contentCanvas.bind("<Enter>", lambda _: self._bind_mousewheel(True))
    self.contentCanvas.bind("<Leave>", lambda _: self._bind_mousewheel(False))

    ttk.Label(self.contentFrame, text="New Expense", font=self.title_font).pack(pady=(0, 6))

    # Top row containers
    topRow = ttk.Frame(self.contentFrame)
    topRow.pack(fill="x", padx=5, pady=4)
    for col in range(3):
      topRow.columnconfigure(col, weight=1, uniform="expense-top")

    # Payer column
    payerCol = ttk.Frame(topRow)
    payerCol.grid(row=0, column=0, sticky="nsew", padx=2)
    ttk.Label(payerCol, text="Payer:", font=self.label_font).pack(anchor="w")
    self.payerBox = ttk.Combobox(payerCol, state="readonly", font=self.input_font)
    self.payerBox.pack(fill="x")

    # Category column
    categoryCol = ttk.Frame(topRow)
    categoryCol.grid(row=0, column=1, sticky="nsew", padx=2)
    ttk.Label(categoryCol, text="Category:", font=self.label_font).pack(anchor="w")
    self.categoryBox = ttk.Combobox(categoryCol, state="readonly", font=self.input_font)
    self.categoryBox.pack(fill="x")

    # Amount column
    amountCol = ttk.Frame(topRow)
    amountCol.grid(row=0, column=2, sticky="nsew", padx=2)
    ttk.Label(amountCol, text="Amount:", font=self.label_font).pack(anchor="w")
    self.amount = ttk.StringVar()
    ttk.Entry(amountCol, textvariable=self.amount, font=self.input_font).pack(fill="x")

    # amount buttons below amount entry
    buttonRow = ttk.Frame(amountCol)
    buttonRow.pack(fill="x", pady=3)
    for val in (1, 10, 100):
      btn = ttk.Button(
        buttonRow,
        text=f"+{val}",
        width=4,
        padding=3,
        command=lambda v=val: self.addAmount(v),
        # bootstyle="info",
      )
      btn.pack(side="left", expand=True, padx=2)
    clrBut = ttk.Button(buttonRow, text="CLR", width=4, padding=3, command=self.clearAmount, bootstyle="danger")
    clrBut.pack(side="left", padx=1)

    #split
    splitFrame = ttk.Frame(self.contentFrame)
    splitFrame.pack(fill="x", padx=5, pady=4)

    ttk.Label(splitFrame, text="Split between:", font=self.label_font).pack(anchor="w")

    self.splitCheckFrame = ttk.Frame(splitFrame)
    self.splitCheckFrame.pack(fill="x", pady=4)

    self.checkVars = {}

    self.saveExpenseBtn = ttk.Button(splitFrame, text="Save Expense", bootstyle="success", padding=10, command=self.saveExpense)
    self.saveExpenseBtn.pack(anchor="e", pady=4)
    
    self.statusLabel = ttk.Label(self.contentFrame, text="", font=self.status_font)
    self.statusLabel.pack(pady=(6, 0), anchor="w")

    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")
  
  def onShow(self):
    #Load names
    userNames = [u["name"] for u in self.controller.users]
    self.payerBox["values"] = userNames

    if self.controller.current_user:
      self.payerBox.set(self.controller.current_user)
    elif userNames:
      self.payerBox.set(userNames[0])

    #Load categories
    catNames = [c["name"] for c in self.controller.categories]
    self.categoryBox["values"] = catNames

    if catNames:
      self.categoryBox.set(catNames[0])

    #Reload split checkboxes
    for w in self.splitCheckFrame.winfo_children():
      w.destroy()

    self.checkVars = {}

    columns = 2 if len(self.controller.users) > 2 else 1
    for idx, u in enumerate(self.controller.users):
      var = tk.BooleanVar(value=True)
      chk = ttk.Checkbutton(
        self.splitCheckFrame,
        text=u["name"],
        variable=var,
        bootstyle="round-toggle",
        padding=6,
        width=14,
      )
      chk.grid(row=idx // columns, column=idx % columns, sticky="w", padx=4, pady=3)
      self.checkVars[u["id"]] = var
    for col in range(columns):
      self.splitCheckFrame.columnconfigure(col, weight=1)
    self.contentCanvas.after(0, lambda: self.contentCanvas.yview_moveto(0))

  def addAmount(self, value):
    current = self.amount.get()
    try:
      current = float(current) if current else 0
    except ValueError:
      current = 0
    self.amount.set(str(current + value))

  def saveExpense(self):
    if self.savingExpense:
      return

    payerName = (self.payerBox.get() or "").strip()
    categoryName = (self.categoryBox.get() or "").strip()

    try:
      amount = float(self.amount.get())
    except (TypeError, ValueError):
      Messagebox.show_error("Invalid amount", "Amount must be a positive number.")
      return

    if amount <= 0:
      Messagebox.show_error("Invalid amount", "Amount must be a positive number.")
      return

    if not payerName:
      Messagebox.show_error("Error", "Select a payer.")
      return

    if not categoryName:
      Messagebox.show_error("Error", "Select a category.")
      return

    payer = next((u for u in self.controller.users if u["name"] == payerName), None)
    if not payer:
      Messagebox.show_error("Error", "Unknown payer selected.")
      return

    try:
      categoryId = self.controller.get_category_id(categoryName)
    except APIError as exc:
      Messagebox.show_error("Error", f"Unable to load categories: {exc}")
      return

    if categoryId is None:
      Messagebox.show_error("Error", "Category not found.")
      return

    splitUsersId = [uid for uid, var in self.checkVars.items() if var.get()]
    if not splitUsersId:
      Messagebox.show_error("Error", "Select at least one member to split with.")
      return

    if payer["id"] not in splitUsersId:
      splitUsersId.append(payer["id"])

    payload = {
      "user_id": payer["id"],
      "category_id": categoryId,
      "cost": int(round(amount)),
      "costsharers": splitUsersId,
      "notes": f"{payerName} recorded an expense",
    }

    self._set_saving_state(True, "Capturing receipt...")
    threading.Thread(target=self._submit_expense, args=(payload,), daemon=True).start()
  
  def clearAmount(self):
    self.amount.set("")

  def _set_saving_state(self, saving: bool, message: str = ""):
    self.savingExpense = saving
    if self.saveExpenseBtn:
      self.saveExpenseBtn.config(state="disabled" if saving else "normal")
    self.statusLabel.config(text=message)

  def _submit_expense(self, payload: dict):
    try:
      photo = self.controller.capture_snapshot()
    except RuntimeError as exc:
      self.after(0, lambda: self._handle_expense_error(f"Camera error: {exc}"))
      self.after(0, lambda: self._set_saving_state(False))
      return

    try:
      self.controller.api.create_event(payload, photo)
      self.controller.refresh_users()
      self.after(0, self._handle_expense_success)
    except APIError as exc:
      self.after(0, lambda: self._handle_expense_error(str(exc)))
    finally:
      self.after(0, lambda: self._set_saving_state(False))

  def _handle_expense_success(self):
    self.statusLabel.config(text="Expense saved!")
    Messagebox.ok("Expense saved", "Expense saved successfully!")
    self.amount.set("0")
    for var in self.checkVars.values():
      var.set(True)

  def _handle_expense_error(self, message: str):
    self.statusLabel.config(text=f"Error: {message}")
    Messagebox.show_error("Unable to save", message)

  def _update_scroll_region(self):
    if self.contentCanvas:
      self.contentCanvas.configure(scrollregion=self.contentCanvas.bbox("all"))

  def _resize_canvas(self, event):
    if self.content_frame_id is not None:
      self.contentCanvas.itemconfig(self.content_frame_id, width=event.width)

  def _bind_mousewheel(self, enable: bool):
    sequences = ("<MouseWheel>", "<Button-4>", "<Button-5>")
    if enable:
      for seq in sequences:
        self.contentCanvas.bind(seq, self._on_mousewheel, add="+")
    else:
      for seq in sequences:
        self.contentCanvas.unbind(seq)

  def _on_mousewheel(self, event):
    if event.delta:
      self.contentCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif event.num == 4:
      self.contentCanvas.yview_scroll(-1, "units")
    elif event.num == 5:
      self.contentCanvas.yview_scroll(1, "units")
