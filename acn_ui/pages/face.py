import threading
import tkinter as tk

import cv2
import face_recognition
import numpy as np
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from api import APIError

FONT = cv2.FONT_HERSHEY_PLAIN
PROCESS_PERIOD = 5
MAX_PROCESS_TIME = 100
COUNTDOWN_START = 8


def resize_with_pad(image: np.ndarray, size=(320, 240), color=(0, 0, 0)):
  target_w, target_h = size
  h, w = image.shape[:2]
  scale = min(target_w / w, target_h / h)
  new_w, new_h = int(w * scale), int(h * scale)
  resized = cv2.resize(image, (new_w, new_h))
  pad_w = (target_w - new_w) // 2
  pad_h = (target_h - new_h) // 2
  padded = cv2.copyMakeBorder(
    resized,
    pad_h,
    target_h - new_h - pad_h,
    pad_w,
    target_w - new_w - pad_w,
    cv2.BORDER_CONSTANT,
    value=color,
  )
  return padded


# *============ FACE PAGE =================* 
class FacePage(ttk.Frame):
  def __init__(self, controller):
    super().__init__(controller)
    self.controller = controller

    self.content = ttk.Frame(self)
    self.content.pack(expand=True, fill="both")

    self.faceLabel = ttk.Label(self.content, text="Face Recognition", font=("Helvetica", 18))
    self.faceLabel.pack(anchor='center', pady=5)

    self.statusLabel = ttk.Label(self.content, text="", font=("Helvetica", 14))
    self.statusLabel.pack(pady=5)

    self.video_label = ttk.Label(self.content)
    self.video_label.pack(pady=5)

    self.faceButton = ttk.Button(self.content, image=controller.photoFace, command=self.startFaceRecognition)
    self.faceButton.pack(anchor="center", pady=5)

    self.cap = None
    self.preview_job = None
    self.process_idx = 0
    self.process_idx_last_face_seen = 0
    self.countdown = COUNTDOWN_START
    self.prev_face_count = 0

    self.exitBut = ttk.Button(self, text="EXIT", command=self.closeWin)
    self.exitBut.place(relx=1.0, rely=1.0, x=-5, y=-5, anchor="se")

  def onShow(self):
    self.statusLabel.config(text="")
    self.controller.clear_current_user()
    self._stop_camera()
    self.faceButton.configure(state="normal")

  def startFaceRecognition(self):
    self.statusLabel.config(text="Starting camera...")
    self.faceButton.configure(state="disabled")
    self.countdown = COUNTDOWN_START
    self.process_idx = 0
    self.cap = cv2.VideoCapture(0)
    if not self.cap.isOpened():
      self._handle_error("Camera not available")
      return
    self.statusLabel.config(text="Look at the camera")
    self._schedule_frame()

  def closeWin(self):
    self._stop_camera()
    self.controller.destroy()

  def _schedule_frame(self):
    self.preview_job = self.after(10, self._update_frame)

  def _update_frame(self):
    if (self.process_idx - self.process_idx_last_face_seen) > MAX_PROCESS_TIME:
      self._stop_camera()
      self._hide_camera()
      self.statusLabel.config(text="")
      self.faceButton.configure(state="normal")
      return

    ret, frame = self.cap.read()
    if not ret:
      self._handle_error("Unable to read from camera")
      return

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = resize_with_pad(frame)
    overlay_frame = frame.copy()

    if (self.process_idx % PROCESS_PERIOD) == 0:
      rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      face_locations = face_recognition.face_locations(rgb_small)
      frame_valid = len(face_locations) == 1

      if frame_valid:
        self.countdown -= 1
        y1, x2, y2, x1 = face_locations[0]
        cv2.rectangle(overlay_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
          overlay_frame,
          f"Confirming... {self.countdown}",
          (10, 20),
          FONT,
          1.0,
          (0, 255, 0),
          1,
        )
        self.process_idx_last_face_seen = self.process_idx
        if self.countdown <= 0:
          self._submit_snapshot(frame)
          return
      else:
        self.countdown = COUNTDOWN_START
        if len(face_locations) == 0:
          msg = "No face detected"
        elif len(face_locations) > 1:
          msg = "Only one person please"
        else:
          msg = "Hold still"
        cv2.putText(
          overlay_frame,
          msg,
          (10, 20),
          FONT,
          1.0,
          (0, 0, 255),
          1,
        )

      rgb_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
      image = Image.fromarray(rgb_frame)
      imgtk = ImageTk.PhotoImage(image=image)
      self.video_label.configure(image=imgtk)
      self.video_label.image = imgtk

    self.process_idx += 1
    self._schedule_frame()

  def _submit_snapshot(self, frame):
    self._stop_camera()
    self.statusLabel.config(text="Recognizing...")

    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
      self._handle_error("Failed to capture photo")
      return
    photo_bytes = buffer.tobytes()
    threading.Thread(target=self._recognize_worker, args=(photo_bytes,), daemon=True).start()

  def _recognize_worker(self, photo_bytes: bytes):
    try:
      result = self.controller.api.perform_face_recognition(photo_bytes)
      user = result.get("user")
      if not user:
        raise APIError("No user returned from server")

      self.controller.set_current_user(user)
      self.after(0, lambda: self._on_success(user["name"]))
    except (RuntimeError, APIError) as exc:
      message = str(exc)
      self.after(0, lambda msg=message: self._handle_error(msg))
    except Exception as exc:
      message = f"Unexpected error: {exc}"
      self.after(0, lambda msg=message: self._handle_error(msg))

  def _on_success(self, user_name: str):
    self.faceButton.configure(state="normal")
    self.statusLabel.config(text=f"Welcome {user_name}! ✓")
    def after():
      self._hide_camera()
      self.controller.show_frame("home")
    self.after(800, after)

  def _handle_error(self, message: str):
    self._hide_camera()
    self.faceButton.configure(state="normal")
    self.statusLabel.config(text=f"Error: {message}")

  def _stop_camera(self):
    if self.preview_job is not None:
      self.after_cancel(self.preview_job)
      self.preview_job = None
    if self.cap is not None:
      self.cap.release()
      self.cap = None

  def _hide_camera(self):
    self.video_label.configure(image=None)
    self.video_label.image = None




