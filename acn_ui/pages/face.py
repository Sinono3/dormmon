import tkinter as tk
import ttkbootstrap as ttk

# *============ FACE PAGE =================* 
class FacePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    #Container of Labe + Button
    self.content = ttk.Frame(self)
    self.content.pack(expand=True)

    #Labels
    self.faceLabel = ttk.Label(self.content, text="Face Recognition", font=("Helvetica", 18))
    self.faceLabel.pack(anchor='center', pady=5)

    self.statusLabel = ttk.Label(self.content, text="", font=("Helvetica", 18))
    self.statusLabel.pack(pady=5)

    #Buttons
    self.faceButton = ttk.Button(self.content, image=controller.photoFace, command=self.startFaceRecognition)
    self.faceButton.pack(anchor="center", pady=5)

  #! FACE RECOGNITION HERE !

  def onShow(self): #Called every time FacePage becomes visible
    self.statusLabel.config(text="")
    self.controller.current_user = None

  def startFaceRecognition(self): 
    self.statusLabel.config(text="Recognizing...")

    self.after(1500, self.fakeRecognition)

  def fakeRecognition(self):
    recognized = "Maia"  # simulate recognition
    self.controller.current_user = recognized

    self.statusLabel.config(text=f"Welcome {recognized}! ✓")

    self.after(800, lambda: self.controller.show_frame("home"))




