import tkinter as tk

import cv2
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from api import DormmonAPI, APIError
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

    #Session variables
    self.current_user = None
    self.current_user_id = None
    self.current_user_info = None

    self.api = DormmonAPI()
    self.users = []
    self.users_by_id = {}
    self.categories = []
    self.categories_by_name = {}

    #Dictionary of frames
    self.frames = {}

    #History stack
    self.history = []

    #Load shared images
    self.load_images()

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
    self.after(100, self.initialize_reference_data)


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

    imgMenu = Image.open("icons/dots.png")
    imgMenu = imgMenu.resize((15, 15))
    self.menuIm = ImageTk.PhotoImage(imgMenu)


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

  def initialize_reference_data(self):
    try:
      self.refresh_users()
      self.refresh_categories()
    except APIError as exc:
      print(f"Unable to load initial data: {exc}")

  def refresh_users(self):
    users = self.api.get_users()
    self.users = users
    self.users_by_id = {user["id"]: user for user in users}
    return users

  def refresh_categories(self):
    categories = self.api.get_categories()
    self.categories = categories
    self.categories_by_name = {cat["name"]: cat for cat in categories}
    return categories

  def get_category_id(self, category_name: str):
    if category_name not in self.categories_by_name:
      try:
        self.refresh_categories()
      except APIError as exc:
        raise APIError(f"Unable to load categories: {exc}") from exc
    category = self.categories_by_name.get(category_name)
    return category["id"] if category else None

  def set_current_user(self, user_info):
    self.current_user = user_info["name"]
    self.current_user_id = user_info["id"]
    self.current_user_info = user_info

  def clear_current_user(self):
    self.current_user = None
    self.current_user_id = None
    self.current_user_info = None

  def capture_snapshot(self):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
      raise RuntimeError("Camera is not available")
    try:
      # Read a few frames, sometimes the webcam doesn't adjust in time.
      for _ in range(15):
        ret, frame = cap.read()
        if not ret:
          raise RuntimeError("Unable to read from camera")
      success, buffer = cv2.imencode(".jpg", frame)
      if not success:
        raise RuntimeError("Unable to encode captured frame")
      return buffer.tobytes()
    finally:
      cap.release()


if __name__ == '__main__':
  ui = UI()
  ui.mainloop()
