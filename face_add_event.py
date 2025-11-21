import copy
import tkinter as tk
from typing import Tuple

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

from database_access import database_init, user_get_all
from face_encoding import decode_face_from_bytes

font = cv2.FONT_HERSHEY_PLAIN

database_init()
users = user_get_all()
user_id = [user.id for user in users]
user_enc = [decode_face_from_bytes(user.face_encoding) for user in users]
user_name_by_id = {user.id: user.name for user in users}

root = tk.Tk()
root.title("dormmon")
root.minsize(320, 240)
root.maxsize(320, 240)
root.lift()
root.after(1, lambda: root.focus_force())

video_label = tk.Label(root)
video_label.pack()
cap = cv2.VideoCapture(0)

prev_face_ids = []
face_ids = []
face_locations = []
process_idx = 0
one_person = False
no_change = False
person_known = False
frame_valid = False

PROCESS_PERIOD = 20
COUNTDOWN_START = 10
countdown = COUNTDOWN_START

def resize_with_pad(image: np.array, 
                    new_shape: Tuple[int, int], 
                    padding_color: Tuple[int] = (255, 255, 255)) -> np.array:
    """Maintains aspect ratio and resizes with padding.
    Params:
        image: Image to be resized.
        new_shape: Expected (width, height) of new image.
        padding_color: Tuple in BGR of padding color
    Returns:
        image: Resized image with padding
    """
    border_v = 0
    border_h = 0
    if (new_shape[1]/new_shape[0]) >= (image.shape[0]/image.shape[1]):
        border_v = int((((new_shape[1]/new_shape[0])*image.shape[1])-image.shape[0])/2)
    else:
        border_h = int((((new_shape[0]/new_shape[1])*image.shape[0])-image.shape[1])/2)
    image = cv2.copyMakeBorder(image, border_v, border_v, border_h, border_h, cv2.BORDER_CONSTANT, 0)
    image = cv2.resize(image, (new_shape[0], new_shape[1]))
    return image

def update_frame():
    global face_locations, face_ids, process_idx, one_person, no_change, person_known, frame_valid, countdown

    ret, frame = cap.read()
    frame = resize_with_pad(frame, (320, 240)) # Force 320x240

    if (process_idx % PROCESS_PERIOD) == 0:
        # BGR -> RGB for `face_recognition`
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        prev_face_ids = copy.deepcopy(face_ids)
        face_ids = []

        for face_encoding in face_encodings:
            # Check which faces match
            matches = face_recognition.compare_faces(user_enc, face_encoding)

            # Look for the nearest face and check if it's even a match.
            face_distances = face_recognition.face_distance(user_enc, face_encoding)
            best_match_index = np.argmin(face_distances)
            id = -1
            if matches[best_match_index]:
                id = user_id[best_match_index]
            face_ids.append(id)

        # Conditions for confirmation
        frame_valid = (
            # Only one person
            (len(face_ids) == 1)
            # Person not unknown
            and (face_ids[0] != -1)
            # No change in person from previous frame
            and (set(face_ids) == set(prev_face_ids))
        )

        # If valid continue counting down, if not restart.
        if frame_valid:
            countdown -= 1
            if countdown == 0:
                exit(1)
        else:
            countdown = COUNTDOWN_START


    process_idx += 1

    # Display the results
    for (top, right, bottom, left), id in zip(face_locations, face_ids):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size

        if id != -1:
            name = user_name_by_id[id]
            color = (0, 255, 0)
        else:
            name = "Intruder"
            color = (0, 0, 255)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 1)
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 20), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 1)

    if frame_valid:
        text = f"Confirming {user_name_by_id[id]}... {countdown}"
        cv2.putText(frame, text, (10, 20), font, 1.0, (0, 255, 0), 1)
        # print(text)
    else:
        error_text = ""

        if len(face_ids) == 0:
            error_text = "No people detected"
        elif len(face_ids) > 1:
            error_text = "Only one face should be in frame"
        elif not person_known:
            error_text = "Unknown user"

        cv2.putText(frame, error_text, (10, 20), font, 1.0, (0, 0, 255), 1)
        # print(f"Error: {error_text}")

    # Display `frame` in tkinter
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk  # Keep a reference to prevent Garbage Collection
    video_label.configure(image=imgtk)
    # Schedule the update_frame function to be called again in 10ms
    video_label.after(10, update_frame)


update_frame()
root.mainloop()
cap.release()
