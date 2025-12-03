import tkinter as tk
from datetime import datetime
from io import BytesIO

import requests
import ttkbootstrap as ttk
from PIL import ImageTk
from PIL import Image

API_KEY = "c034e762d2e06d9182f3af02bec5452b"
CITY = "Taipei"

# *============= HOME PAGE ===================*
class HomePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    butStyle = ttk.Style()
    butStyle.configure("MyButton.TButton", font=("Helvetica", 13))

    #Top frame container line1 + line2
    self.topFrame = ttk.Frame(self)
    self.topFrame.pack(side="top", fill="x")

    #line1
    self.line1 = ttk.Frame(self.topFrame)
    self.line1.pack(pady=2)

    #line2
    self.line2 = ttk.Frame(self.topFrame)
    self.line2.pack(pady=2)

    #Middle frame (buttons)
    self.middleFrame = ttk.Label(self)
    self.middleFrame.pack(fill="both", expand=True, pady=10)

    #Labels
    self.label1 = ttk.Label(self.line1, text="Hello Maia!", font=("Helvetica", 15))   #!Face recognition
    self.label1.pack(side="left", padx=5)

    self.dayTime = ttk.Label(self.line1, font=("Helvetica", 13))
    self.dayTime.pack(side="left", padx=10, pady=5)

    self.tempLabel = ttk.Label(self.line2, font=("Helvetica", 12))
    self.tempLabel.pack(side="left", padx=5)

    self.iconLabel = ttk.Label(self.line2)
    self.iconLabel.pack(side="left", padx=5)

    self.descripLabel = ttk.Label(self.line2, font=("Helvetica", 12))
    self.descripLabel.pack(side="left", padx=5)

    #grid weights
    for col in range(2):
      self.middleFrame.columnconfigure(col, weight=1)
    for row in range(2):
      self.middleFrame.rowconfigure(row, weight=1)

    #Buttons
    logOutBut = ttk.Button(self, image=controller.logoutIm, command=self.logout)
    logOutBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    nightModeBut = ttk.Button(self, image=controller.nightModeIm, command=self.controller.toggle_night_mode)
    nightModeBut.place(x=5, y=5, anchor="nw")

    #grid of buttons
    self.bt1 = ttk.Button(self.middleFrame, text="See balance", style="MyButton.TButton", command=lambda: self.controller.show_frame("balance"))
    self.bt1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    self.bt2 = ttk.Button(self.middleFrame, text="Took trash out", style="MyButton.TButton", command=lambda: self.controller.show_frame("trash"))
    self.bt2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    self.bt3 = ttk.Button(self.middleFrame, text="New expense", style="MyButton.TButton", command=lambda: self.controller.show_frame("expense"))
    self.bt3.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    self.bt4 = ttk.Button(self.middleFrame, text="Clean the room", style="MyButton.TButton", command=lambda: self.controller.show_frame("cleanroom"))
    self.bt4.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    self.weather()
    self.dateTime()
  
  def onShow(self):
    user = self.controller.current_user
    if user:
      self.label1.config(text=f"Hello {user}!")
    else:
      self.label1.config(text="Hello!")

  def logout(self):
    self.controller.clear_current_user()
    self.controller.show_frame("face")

  def weather(self):
    icon_url, temperature, description = self.get_weather(CITY)

    response = requests.get(icon_url).content
    image = Image.open(BytesIO(response))
    image = image.resize((30, 30))
    icon = ImageTk.PhotoImage(image)

    self.iconLabel.configure(image=icon)
    self.iconLabel.image = icon

    self.tempLabel.configure(text=f"Temp: {temperature:.1f} ˚C")
    self.descripLabel.configure(text=f"{description.capitalize()}")

    self.after(600000, self.weather)

  def get_weather(self, city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    res = requests.get(url)

    weather = res.json()
    icon_id = weather['weather'][0]['icon']
    temperature = weather['main']['temp'] - 273.15
    description = weather['weather'][0]['description']

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return(icon_url, temperature, description)
  
  def dateTime(self):
    now = datetime.now()

    formatted = now.strftime("%a %b %d  %I:%M %p").upper()
    self.dayTime.configure(text=formatted)

    self.after(1000, self.dateTime)



