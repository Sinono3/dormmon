import tkinter as tk
from typing import Tuple
from datetime import datetime

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

from database import EventCategory
from database_access import database_init, event_add, user_get_all
from face_encoding import decode_face_from_bytes

FONT = cv2.FONT_HERSHEY_PLAIN
PROCESS_PERIOD = 2
COUNTDOWN_START = 20

def resize_with_pad(image: np.array, 
                    new_shape: Tuple[int, int], 
                    padding_color: Tuple[int] = (255, 255, 255)) -> np.array:
    border_v = 0
    border_h = 0
    if (new_shape[1]/new_shape[0]) >= (image.shape[0]/image.shape[1]):
        border_v = int((((new_shape[1]/new_shape[0])*image.shape[1])-image.shape[0])/2)
    else:
        border_h = int((((new_shape[0]/new_shape[1])*image.shape[0])-image.shape[1])/2)
    image = cv2.copyMakeBorder(image, border_v, border_v, border_h, border_h, cv2.BORDER_CONSTANT, 0)
    image = cv2.resize(image, (new_shape[0], new_shape[1]))
    return image

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.update_tables()
        self.title("dormmon")
        self.geometry("320x240")
        self.minsize(320, 240)
        self.maxsize(320, 240)
        self.lift()
        self.after(1, lambda: self.focus_force())

        # Create a container to hold all pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in [MenuApp, CameraApp]:
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.current_frame = "MenuApp"
        self.frames[self.current_frame].init()
        self.frames[self.current_frame].tkraise()

    def update_tables(self):
        self.users = list(user_get_all())
        self.user_id = [user.id for user in self.users]
        self.user_enc = [decode_face_from_bytes(user.face_encoding) for user in self.users]
        self.user_name_by_id = {user.id: user.name for user in self.users}

    def switch(self, new_frame: str):
        self.frames[self.current_frame].deinit()
        self.frames[new_frame].init()
        self.frames[new_frame].tkraise()
        self.current_frame = new_frame


class MenuApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="lightblue") # Color to distinguish state

        label = tk.Label(self, text="dorm monitor", bg="lightblue", font=("Arial", 16))
        label.pack(pady=20)

        def goto_camera():
            self.controller.switch("CameraApp")

        btn = tk.Button(self, text="Add trash event", command=goto_camera)
        btn.pack()

    def init(self):
        pass

    def deinit(self):
        pass

class CameraApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cap = None
        self.prev_face_ids = []
        self.process_idx = 0
        self.countdown = COUNTDOWN_START

        self.video_label = tk.Label(self)
        self.video_label.pack()

    def init(self):
        self.cap = cv2.VideoCapture(0)
        self.prev_face_ids = []
        self.process_idx = 0
        self.countdown = COUNTDOWN_START
        self.after(10, self.update_frame)

    def deinit(self):
        self.cap.release()
        self.cap = None

    def update_frame(self):
        confirmed_user_id = None

        ret, frame = self.cap.read()
        if (self.process_idx % PROCESS_PERIOD) == 0:
            frame = resize_with_pad(frame, (320, 240)) # Force 320x240
            # BGR -> RGB for `face_recognition`
            rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            face_ids = []

            for face_encoding in face_encodings:
                # Check which faces match
                matches = face_recognition.compare_faces(self.controller.user_enc, face_encoding)

                # Look for the nearest face and check if it's even a match.
                face_distances = face_recognition.face_distance(self.controller.user_enc, face_encoding)
                best_match_index = np.argmin(face_distances)
                id = -1
                if matches[best_match_index]:
                    id = self.controller.user_id[best_match_index]
                face_ids.append(id)

            # Conditions for confirmation
            frame_valid = (
                # Only one person
                (len(face_ids) == 1)
                # Person not unknown
                and (face_ids[0] != -1)
                # No change in person from previous frame
                and (set(face_ids) == set(self.prev_face_ids))
            )
            self.prev_face_ids = face_ids

            # If valid continue counting down, if not restart.
            if frame_valid:
                self.countdown -= 1
                if self.countdown == 0:
                    confirmed_user_id = face_ids[0]
            else:
                self.countdown = COUNTDOWN_START

            # Display the results
            for (top, right, bottom, left), id in zip(face_locations, face_ids):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size

                if id != -1:
                    name = self.controller.user_name_by_id[id]
                    color = (0, 255, 0)
                else:
                    name = "Intruder"
                    color = (0, 0, 255)

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 1)
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 20), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), FONT, 1.0, (0, 0, 0), 1)

            if frame_valid:
                name = self.controller.user_name_by_id[id]
                text = f"Confirming {name}... {self.countdown}"
                cv2.putText(frame, text, (10, 20), FONT, 1.0, (0, 255, 0), 1)
                # print(text)
            else:
                error_text = ""

                if len(face_ids) == 0:
                    error_text = "No people detected"
                elif len(face_ids) > 1:
                    error_text = "Only one face should be in frame"
                elif face_ids[0] == -1:
                    error_text = "Unknown user"

                cv2.putText(frame, error_text, (10, 20), FONT, 1.0, (0, 0, 255), 1)
                # print(f"Error: {error_text}")

            # Display `frame` in tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk  # Keep a reference to prevent Garbage Collection
            self.video_label.configure(image=imgtk)

        self.process_idx += 1

        if confirmed_user_id is not None:
            self.controller.switch("MenuApp")

            selected_user_id = face_ids[0]
            selected_user_name = self.controller.user_name_by_id[selected_user_id]
            print(f"Selected user {selected_user_id}: {selected_user_name}")

            category_trash, _ = EventCategory.get_or_create(
                name='Trash',
                defaults={'icon': '🗑️', 'created_at': datetime.utcnow()}
            )
            event_add(
                user_id=face_ids[0],
                category_id=category_trash,
                photo_path="",
                notes="trash",
            )
            print("Event inserted")
            
        else:
            # Schedule the update_frame function to be called again in 10ms
            self.after(10, self.update_frame)


if __name__ == "__main__":
    database_init()
    app = MainApp()
    app.mainloop()
