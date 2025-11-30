import numpy as np
import face_recognition
from flask import request

from database_access import user_get_all
from face_encoding import decode_face_from_bytes
from response_helpers import json_error, json_response


def routes(app):
    @app.route("/face/recognize", methods=["POST"])
    def perform_face_recognition():
        """Recognize a face from an uploaded photo and return the matched user."""
        photo = request.files.get("photo") or request.files.get("image")
        if not photo or not photo.filename:
            return json_error("Photo is required", 400)

        users = list(user_get_all())
        if not users:
            return json_error("No registered users", 404)

        try:
            photo.stream.seek(0)
            image = face_recognition.load_image_file(photo)
            encodings = face_recognition.face_encodings(image)
        except Exception:
            return json_error("Invalid image data", 400)

        if not encodings:
            return json_error("No recognizable faces found", 400)

        if len(encodings) > 1:
            return json_error("Multiple faces detected. Submit a photo with a single person.", 400)

        target_encoding = encodings[0]
        known_encodings = [decode_face_from_bytes(user.face_encoding) for user in users]
        matches = face_recognition.compare_faces(known_encodings, target_encoding)
        distances = face_recognition.face_distance(known_encodings, target_encoding)

        best_index = int(np.argmin(distances))
        confidence = max(0.0, 1.0 - float(distances[best_index]))

        if matches[best_index]:
            user = users[best_index]
            return json_response(
                {
                    "user": {"id": user.id, "name": user.name},
                    "confidence": confidence,
                }
            )

        return json_error("Face not recognized", 404, confidence=confidence)

