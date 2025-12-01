import tkinter as tk
import ttkbootstrap as ttk

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

    self.amount = ttk.StingVar()
    ttk.Entry(amountFrame, textvariable=self.amount).pack(fill="x")

    #amount buttons
    buttonRow = ttk.Frame(amountFrame)
    buttonRow.pack(pady=5)
    for val in (1, 10, 100):
      ttk.Button(buttonRow, text=f"+{val}", width=6).pack(side="left", padx=5)
    
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
    self.splitCheckFrame.pack(anchor="w", pady=5)

    self.checkVars = {}

    self.msg = ttk.Label(self, text="", font=("Helvetica", 11))
    self.msg.pack(pady=5)

    #bottom buttons
    btnFrame = ttk.Frame(self)
    btnFrame.pack(pady=10)

    ttk.Button(btnFrame, text="Save Expense", bootstyle="success").pack(side="left", padx=10)
    
    #Button
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")
  
  def onShow(self):
    userNames = [u["name"] for u in self.controller.users]
    self.payerBox["values"] = userNames

    if self.controller.current_user:
      self.payerBox.set(self.controller.current_user)
    elif userNames:
      self.payerBox.set(userNames[0])

    catNames = [c["name"] for c in self.controller.categories]
    self.categoryBox["values"] = catNames

    if catNames:
      self.categoryBox.set(catNames[0])

    for w in self.splitCheckFrame.winfo_children():
      w.destroy()

    self.checkVars = {}

    for u in self.controller.users:
      var = tk.BooleanVar(value=True)
      ttk.Checkbutton(self.splitCheckFrame, text=u["name"], variable=var).pack(anchor="w")
      self.checkVars[u["id"]] = var

    
    self.msg.config(text="")





