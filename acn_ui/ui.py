import tkinter as tk
import ttkbootstrap as ttk
import requests

from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

API_KEY = "c034e762d2e06d9182f3af02bec5452b"
CITY = "Taipei"

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

    #Load shared images
    self.load_images()

    self.members = {
      "Jaz" : 0,
      "Aldo": 0,
      "Simon": 0,
      "Maia": 0
    }

    #Create all frames
    for F in (FacePage, HomePage, BalancePage, TrashPage, ExpensePage, CleanroomPage):
      frame = F(self)
      self.frames[F] = frame
      frame.place(x=0, y=0, relwidth=1, relheight=1)

    #Show face page first
    self.show_frame(FacePage)

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

  def show_frame(self, page):
    current = getattr(self, "current_page", None)

    #Save old page in history
    if current is not None and current != page:
      self.history.append(current)

    #Raise new paige
    frame = self.frames[page]
    frame.tkraise()

    self.current_page = page

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

    self.after(800, lambda: self.controller.show_frame(HomePage))



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

    themeBut = ttk.Button(self, image=controller.themeIm, command=self.controller.toggle_theme)
    themeBut.place(x=5, y=5, anchor="nw")

    #grid of buttons
    self.bt1 = ttk.Button(self.middleFrame, text="See balance", style="MyButton.TButton", command=lambda: self.controller.show_frame(BalancePage))
    self.bt1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    self.bt2 = ttk.Button(self.middleFrame, text="Took trash out", style="MyButton.TButton", command=lambda: self.controller.show_frame(TrashPage))
    self.bt2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    self.bt3 = ttk.Button(self.middleFrame, text="New expense", style="MyButton.TButton", command=lambda: self.controller.show_frame(ExpensePage))
    self.bt3.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    self.bt4 = ttk.Button(self.middleFrame, text="Clean the room", style="MyButton.TButton", command=lambda: self.controller.show_frame(CleanroomPage))
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
    self.controller.current_user = None
    self.controller.show_frame(FacePage)

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



# *================ TRASH PAGE =====================*
class TrashPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    # Back button
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

    # Title
    self.titleTrash = ttk.Label(self, text="Who took the trash out?", font=("Helvetica", 18))
    self.titleTrash.pack(pady=10)

    # Latest record
    self.latestLabel = ttk.Label(self, text="", font=("Helvetica", 14))
    self.latestLabel.pack(pady=10)

    # History frame
    self.historyFrame = ttk.Frame(self)
    self.historyFrame.pack(fill="both", expand=True)

  def onShow(self):
    """Called every time this page becomes visible."""
    user = self.controller.current_user

    if user is None:
        self.latestLabel.config(text="Error: No user recognized")
        return

    # Create new record
    t = datetime.now().strftime("%Y-%m-%d  %H:%M")
    record = {"user": user, "time": t}

    # Add newest first
    self.controller.trash_log.insert(0, record)

    # Update latest record
    self.latestLabel.config(text=f"🗑 {user} took out the trash at {t}")

    # Refresh the list
    self.show_history()

  def show_history(self):
    """Redraw the list of previous trash records."""
    # Clear previous widgets
    for widget in self.historyFrame.winfo_children():
      widget.destroy()

    ttk.Label(self.historyFrame, text="Previous Records:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    # Skip index 0 (latest)
    for item in self.controller.trash_log[1:]:
      ttk.Label(self.historyFrame, text=f"{item['user']} — {item['time']}", font=("Helvetica", 12)).pack(anchor="w", padx=20)

    

# *================ EXPENSE PAGE =====================*
class ExpensePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller


    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")



# *================ CLEAN ROOM PAGE =====================*
class CleanroomPage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller


    #Buttons
    self.backBut = ttk.Button(self, image=controller.backIm, command=controller.go_back)
    self.backBut.place(relx=1.0, x=-5, y=5, anchor="ne")

ui = UI()
ui.mainloop()
