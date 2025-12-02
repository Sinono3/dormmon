import tkinter as tk
import pyrealsense2 as rs 
import numpy as np
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
from pages.noise_alert import NoiseAlertPage

class UI(ttk.Window):
  def __init__(self):
    super().__init__(themename="simplex") 

    self.attributes('-fullscreen', True) 
    self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
    #self.geometry("480x320")
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
      "cleanroom": CleanroomPage,
      "noise_alert": NoiseAlertPage
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
    # 1. Configurar el Pipeline de RealSense
    pipeline = rs.pipeline()
    config = rs.config()
    
    # 2. ACTIVAR EL COLOR (Esta línea es la clave para que no se vea B/N)
    # 640x480 es una resolución segura, bgr8 es el formato de color estándar
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    try:
      # 3. Iniciar la cámara
      pipeline.start(config)
      
      # 4. Leer varios frames para dejar que la cámara ajuste la luz (Auto-Exposure)
      frame_data = None
      for _ in range(15): # Leemos 15 veces para estabilizar
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if color_frame:
            # Convertir a arreglo numpy (formato imagen)
            frame_data = np.asanyarray(color_frame.get_data())

      if frame_data is None:
        raise RuntimeError("No image could be obtained from RealSense")

      # 5. Codificar la imagen final para tu programa
      # La imagen ya viene en BGR, así que OpenCV la entiende directo
      success, buffer = cv2.imencode(".jpg", frame_data)
      
      if not success:
        raise RuntimeError("The captured image could not be encoded.")
        
      return buffer.tobytes()

    except Exception as e:
       print(f"Camera error: {e}")
       raise RuntimeError(f"Error RealSense: {e}")
       
    finally:
      # 6. IMPORTANTE: Apagar la cámara para liberar el USB
      pipeline.stop()


if __name__ == '__main__':
  ui = UI()
  ui.mainloop()
