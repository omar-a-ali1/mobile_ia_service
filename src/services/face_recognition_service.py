import os
import numpy as np
import face_recognition
import cv2
from datetime import datetime

UPLOAD_DIR = "uploads"

async def match_face(file):
    contents = await file.read()

    # Convert to OpenCV image
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}

    rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
    encodings = face_recognition.face_encodings(rgb)

    if not encodings:
        return {"status": "no_face_detected"}

    unknown_encoding = encodings[0]

    known_encodings = []
    known_names = []

    # Load all saved encodings
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(".npy"):
            name = file.replace(".npy", "")
            encoding = np.load(os.path.join(UPLOAD_DIR, file))

            known_encodings.append(encoding)
            known_names.append(name)

    if not known_encodings:
        return {"status": "no_registered_faces"}

    matches = face_recognition.compare_faces(known_encodings, unknown_encoding)
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)

    best_index = np.argmin(distances)

    if matches[best_index]:
        return {
            "status": "matched",
            "name": known_names[best_index],
            "time": datetime.now().isoformat()
        }

    return {"status": "unknown"}