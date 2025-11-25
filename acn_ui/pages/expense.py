import tkinter as tk
import ttkbootstrap as ttk

# *================ EXPENSE PAGE =====================*
class ExpensePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller


    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")



