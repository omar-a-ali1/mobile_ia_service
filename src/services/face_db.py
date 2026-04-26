import os
import shutil
import numpy as np
import face_recognition

UPLOAD_DIR = "uploads"

async def register_face(name, file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    image_path = os.path.join(UPLOAD_DIR, f"{name}.jpg")
    encoding_path = os.path.join(UPLOAD_DIR, f"{name}.npy")

    # Save image
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load image
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        os.remove(image_path)
        return {"error": "No face detected"}

    encoding = encodings[0]

    # Save encoding
    np.save(encoding_path, encoding)

    return {"message": f"{name} registered successfully"}