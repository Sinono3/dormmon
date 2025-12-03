"""Face encoding utilities for user face recognition."""
import face_recognition
import numpy as np
from typing import List, Optional


def encode_face_from_image(image_path: str) -> Optional[np.ndarray]:
    """
    Encode a face from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Face encoding array or None if no face found
    """
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            return encodings[0]
        return None
    except Exception:
        return None


def average_encodings(encodings: List[np.ndarray]) -> np.ndarray:
    """
    Average multiple face encodings into a single encoding.
    
    Args:
        encodings: List of face encoding arrays
        
    Returns:
        Averaged face encoding array
    """
    if not encodings:
        raise ValueError("Cannot average empty list of encodings")
    return np.mean(encodings, axis=0)


def encode_face_to_bytes(encoding: np.ndarray) -> bytes:
    """Convert face encoding array to bytes for storage."""
    return encoding.tobytes()


def decode_face_from_bytes(face_bytes: bytes) -> np.ndarray:
    """Convert bytes back to face encoding array."""
    return np.frombuffer(face_bytes, dtype=np.float64)

