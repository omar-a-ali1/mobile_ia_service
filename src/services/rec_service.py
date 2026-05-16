import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from src.core.mongo import get_collection

UPLOAD_DIR = "uploads"
sessions_col = get_collection("sessions")

def load_known_faces():
    """
    Utility to load all saved face encodings from disk.
    """
    known_encodings = []
    known_names = []
    
    if not os.path.exists(UPLOAD_DIR):
        return known_encodings, known_names

    for file_name in os.listdir(UPLOAD_DIR):
        if file_name.endswith(".npy"):
            name = file_name.replace(".npy", "")
            encoding = np.load(os.path.join(UPLOAD_DIR, file_name))
            known_encodings.append(encoding)
            known_names.append(name)
            
    return known_encodings, known_names


async def match_face_v2(file, status: str = "late"):
    """
    Matches a face in the given image file against known encodings.
    If matched, creates/updates the attendance record in MongoDB sessions.
    """
    contents = await file.read()

    # Convert to OpenCV image
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return {"status": "failed", "detail": "Invalid image file"}

    # Process face detection and encoding
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb)

    if not encodings:
        return {"status": "failed", "detail": "No face detected"}

    unknown_encoding = encodings[0]
    known_encodings, known_names = load_known_faces()

    if not known_encodings:
        return {"status": "failed", "detail": "No registered faces in database"}

    # Find the closest matching face match
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_index = np.argmin(distances)
    matches = face_recognition.compare_faces([known_encodings[best_index]], unknown_encoding)

    if not matches[0]:
        return {"status": "failed", "detail": "Face not recognized"}

    matched_name = known_names[best_index]
    
    # --- Attendance Recording Logic ---
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")  # Object dynamic identifier key
    current_time = now.strftime("%H:%M:%S")

    attendance_record = {
        "id": matched_name,  # Using name/id string as specified
        "time": current_time,
        "status": status
    }

    try:
        # Upsert: updates or inserts dynamically using the current date as the document criteria
        sessions_col.update_one(
            {"date": current_date},
            {"$push": {"users": attendance_record}},
            upsert=True
        )
    except Exception as e:
        return {"status": "failed", "detail": f"Database recording error: {str(e)}"}

    return {
        "status": "success",
        "name": matched_name,
        "date": current_date,
        "time": current_time,
        "attendance_status": status
    }


async def remove_face_from_database(name: str) -> bool:
    """
    Removes a face from the file system database by name.
    """
    file_path = os.path.join(UPLOAD_DIR, f"{name}.npy")
    if not os.path.exists(file_path):
        return False
    
    os.remove(file_path)
    return True


async def match_frame(frame, known_encodings, known_names):
    """
    Directly processes a video stream frame (BGR) for real-time inference.
    """
    # Resize frame to 1/4 size for faster processing speed performance
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    encodings = face_recognition.face_encodings(rgb_small_frame)
    if not encodings:
        return None

    for unknown_encoding in encodings:
        distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        best_index = np.argmin(distances)

        if distances[best_index] < 0.75:  
            return {
                "name": known_names[best_index],
                "time": datetime.now().isoformat()
            }
            
    return None