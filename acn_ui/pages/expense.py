import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from api import APIError

# *================ EXPENSE PAGE =====================*
class ExpensePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    ttk.Label(self, text="New Expense", font=("Helvetica", 18, "bold")).pack(pady=10)

    #Payer 
    payerFrame = ttk.Frame(self)
    payerFrame.pack(fill="x", padx=15, pady=5)

    ttk.Label(payerFrame, text="Payer:", font=("Helvetica", 12)).pack(anchor="w")

    self.payerBox = ttk.Combobox(payerFrame, state="readonly")
    self.payerBox.pack(fill="x")

    #Amount
    amountFrame = ttk.Frame(self)
    amountFrame.pack(fill="x", padx=15, pady=5)

    ttk.Label(amountFrame, text="Amount:", font=("Helvetica", 12)).pack(anchor="w")

    self.amount = ttk.StringVar()
    ttk.Entry(amountFrame, textvariable=self.amount).pack(fill="x")

    #amount buttons
    buttonRow = ttk.Frame(amountFrame)
    buttonRow.pack(pady=5)
    for val in (1, 10, 100):
      ttk.Button(buttonRow, text=f"+{val}", width=6, command= lambda v=val: self.addAmount(v)).pack(side="left", padx=5)
    
    #category 
    categoryFrame = ttk.Frame(self)
    categoryFrame.pack(fill="x", padx=15, pady=5)

    ttk.Label(categoryFrame, text="Category:", font=("Helvetica", 12)).pack(anchor="w")

    self.categoryBox = ttk.Combobox(categoryFrame, state="readonly")
    self.categoryBox.pack(fill="x")

    #split
    splitFrame = ttk.Frame(self)
    splitFrame.pack(fill="x", padx=15, pady=5)

    ttk.Label(splitFrame, text="Split between:", font=("Helvetica", 12)).pack(anchor="w")

    self.splitCheckFrame = ttk.Frame(splitFrame)
    self.splitCheckFrame.pack(side="left", pady=5)

    self.checkVars = {}

    ttk.Button(splitFrame, text="Save Expense", bootstyle="success", command=self.saveExpense).pack(side="right", padx=10)
    
    #Buttons
    clrBut = ttk.Button(buttonRow, text="CLR", width=6, command=self.clearAmount)
    clrBut.pack(side="left", padx=5)

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

    for u in self.controller.users:
      var = tk.BooleanVar(value=True)
      ttk.Checkbutton(self.splitCheckFrame, text=u["name"], variable=var).pack(side="left", padx=5)
      self.checkVars[u["id"]] = var

  def addAmount(self, value):
    current = self.amount.get()
    try:
      current = float(current) if current else 0
    except ValueError:
      current = 0
    self.amount.set(str(current + value))

  def saveExpense(self):
    payerName = self.payerBox.get()
    categoryName = self.categoryBox.get()

    try:
      amount = float(self.amount.get())
      if amount <= 0:
          raise ValueError
    except:
      Messagebox.show_error("Invalid amount", "Amount must be a positive number.")
      return

    if not payerName:
      Messagebox.show_error("Error", "Select a payer.")
      return

    if not categoryName:
      Messagebox.show_error("Error", "Select a category.")
      return

    payerId = next(u["id"] for u in self.controller.users if u["name"] == payerName)

    categoryId = self.controller.get_category_id(categoryName)

    splitUsersId = [uid for uid, var in self.checkVars.items() if var.get() == 1]
    if not splitUsersId:
      Messagebox.show_error("Error", "Select at least one member to split with.")
      return
    
    payload = {
      "payer_id": payerId,
      "amount": amount,
      "category_id": categoryId,
      "split_with": splitUsersId
    }

    try:
      self.controller.api.create_expense(payload)
    except APIError as exc:
      MemoryError.show_error("Unable to save", str(exc))
      return
    
    self.controller.refresh_users()
    Messagebox.ok("Expense saved succesfully!")

    #Reset ui
    self.amount.set("0")
    for var in self.checkVars.values():
      var.set(True)
  
  def clearAmount(self):
    self.amount.set("")
