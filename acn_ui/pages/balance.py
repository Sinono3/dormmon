import tkinter as tk
import ttkbootstrap as ttk

#*================ BALANCE PAGE =====================*
class BalancePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    #Label
    label = ttk.Label(self, text="hola")
    label.pack()

    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")



