import tkinter as tk
import ttkbootstrap as ttk
import requests

from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

from pages.face import FacePage
from pages.home import HomePage
from pages.balance import BalancePage
from pages.trash import TrashPage
from pages.expense import ExpensePage
from pages.cleanroom import CleanroomPage

class UI(ttk.Window):
  def __init__(self):
    super().__init__(themename="simplex") 

    self.geometry("480x320")
    self.title("UI")

    self.themeStyle = ttk.Style()
    self.themeStyle.theme_use("simplex")

    #Session variable
    self.current_user = None

    #Dictionary of frames
    self.frames = {}

    #History stack
    self.history = []

    self.trash_log = []
    self.clean_log = []

    #Load shared images
    self.load_images()

    self.members = {
      "Jaz" : 0,
      "Aldo": 0,
      "Simon": 0,
      "Maia": 0
    }

    page_mapping = {
      "face": FacePage,
      "home": HomePage,
      "balance": BalancePage,
      "trash": TrashPage,
      "expense": ExpensePage,
      "cleanroom": CleanroomPage
    }
    
    for page_name, PageClass in page_mapping.items():
      frame = PageClass(self)
      self.frames[page_name] = frame
      frame.place(x=0, y=0, relwidth=1, relheight=1)
    
    #Show face page first
    self.show_frame("face")


  def load_images(self):
    imgFace = Image.open("icons/faceRecognition.png")
    imgFace = imgFace.resize((60, 60))
    self.photoFace = ImageTk.PhotoImage(imgFace)

    imgLogO = Image.open("icons/logout.png")
    imgLogO = imgLogO.resize((15, 15))
    self.logoutIm = ImageTk.PhotoImage(imgLogO)

    imgTheme = Image.open("icons/theme.png")
    imgTheme = imgTheme.resize((15, 15))
    self.themeIm = ImageTk.PhotoImage(imgTheme)

    imgBack = Image.open("icons/back.png")
    imgBack = imgBack.resize((15, 15))
    self.backIm = ImageTk.PhotoImage(imgBack)

  def show_frame(self, page_name):
    current = getattr(self, "current_page", None)
    
    #Save old page in history
    if current is not None and current != page_name:
      self.history.append(current)
    
    #Raise new page
    frame = self.frames[page_name]
    frame.tkraise()
    self.current_page = page_name
    
    if hasattr(frame, "onShow"):
      frame.onShow()
  
  def toggle_theme(self):
    current = self.themeStyle.theme_use()
    if current == "simplex":
      self.themeStyle.theme_use("vapor")
    else:
      self.themeStyle.theme_use("simplex")

  def go_back(self):
    if self.history:
      previous = self.history.pop()
      self.show_frame(previous)


if __name__ == '__main__':
  ui = UI()
  ui.mainloop()
