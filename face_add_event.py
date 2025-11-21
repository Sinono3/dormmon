import copy
import tkinter as tk

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

from database_access import database_init, user_get_all
from face_encoding import decode_face_from_bytes

font = cv2.FONT_HERSHEY_DUPLEX

database_init()
users = user_get_all()
user_id = [user.id for user in users]
user_enc = [decode_face_from_bytes(user.face_encoding) for user in users]
user_name_by_id = {user.id: user.name for user in users}

root = tk.Tk()
root.title("dormmon")
# root.minsize(320, 240)
# root.maxsize(320, 240)
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

PROCESS_PERIOD = 5
COUNTDOWN_START = 10
countdown = COUNTDOWN_START

def update_frame():
    global face_locations, face_ids, process_idx, one_person, no_change, person_known, frame_valid, countdown

    ret, frame = cap.read()
    if (process_idx % PROCESS_PERIOD) == 0:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )

        prev_face_ids = copy.deepcopy(face_ids)
        face_ids = []
        for face_encoding in face_encodings:
            # Check which faces match
            matches = face_recognition.compare_faces(user_enc, face_encoding)
            id = -1

            # Look for the nearest face, check if it's even a match.
            face_distances = face_recognition.face_distance(user_enc, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                id = user_id[best_match_index]

            face_ids.append(id)

        print(f"{prev_face_ids=}")
        print(f"{face_ids=}")

        # Here, we check if there is only one person and the list of people
        # detected does not change.
        frame_valid = (
            # Only one person
            (len(face_ids) == 1)
            # Person not unknown
            and (face_ids[0] != -1)
            # No change in person from previous frame
            and (set(face_ids) == set(prev_face_ids))
        )

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
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        if id != -1:
            name = user_name_by_id[id]
            color = (0, 255, 0)
        else:
            name = "Intruder"
            color = (0, 0, 255)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        # Draw a label with a name below the face
        cv2.rectangle(
            frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED
        )
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 4.0, (255, 255, 255), 4)

    if frame_valid:
        text = f"Confirming {user_name_by_id[id]}... {countdown}"
        print(text)
        cv2.putText(frame, text, (200, 200), font, 2.0, (0, 255, 0), 2)
    else:
        error_text = ""

        if len(face_ids) == 0:
            error_text = "No people detected"
        elif len(face_ids) > 1:
            error_text = "Only one face should be in frame"
        elif not person_known:
            error_text = "Unknown user"

        print(f"Error: {error_text}")
        cv2.putText(frame, error_text, (200, 200), font, 2.0, (0, 0, 255), 2)

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
