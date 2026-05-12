import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.core.mongo import get_collection

router = APIRouter()

# --- Configuration ---
UPLOAD_DIR = "uploads"
sessions_col = get_collection("sessions")
cameras_col = get_collection("cameras")  # New collection for camera management
already_logged = {} 

# --- Camera Management Routes ---

@router.post("/cameras")
def add_camera(camera_id: str,departement:str, ip: str, camera_type: str):
    """
    Register a new camera. 
    camera_type: 'entering' or 'sorting'
    """
    if camera_type not in ["entering", "sorting"]:
        raise HTTPException(status_code=400, detail="Type must be 'entering' or 'sorting'")
    
    camera_doc = {
        "_id": camera_id, 
        "ip": ip, 
        "departement":departement,
        "type": camera_type,
        "created_at": datetime.now()
    }
    cameras_col.update_one({"_id": camera_id}, {"$set": camera_doc}, upsert=True)
    return {"message": f"Camera {camera_id} registered successfully"}

# --- Additional Camera Management Routes ---

@router.get("/cameras")
def list_cameras():
    """
    Get a list of all registered cameras for the mobile app.
    """
    try:
        # We convert the cursor to a list and return it
        cameras = list(cameras_col.find())
        # MongoDB _id is an object, FastAPI needs a string to return JSON
        for cam in cameras:
            cam["id"] = str(cam["_id"])
        return cameras
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/cameras/{camera_id}")
def remove_camera(camera_id: str):
    """
    Remove a camera from the database by its ID.
    """
    result = cameras_col.delete_one({"_id": camera_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
        
    return {"message": f"Camera {camera_id} removed successfully"}
    
# --- Face Recognition Logic ---

def load_known_faces():
    known_encodings = []
    known_names = []
    if not os.path.exists(UPLOAD_DIR):
        return known_encodings, known_names
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(".npy"):
            name = file.replace(".npy", "")
            encoding = np.load(os.path.join(UPLOAD_DIR, file))
            known_encodings.append(encoding)
            known_names.append(name)
    return known_encodings, known_names

KNOWN_ENCODINGS, KNOWN_NAMES = load_known_faces()

def gen_frames(camera_id: str):
    # 1. Fetch camera details from MongoDB
    camera_info = cameras_col.find_one({"_id": camera_id})
    if not camera_info:
        print(f"Error: Camera {camera_id} not found in database")
        return

    camera_url = camera_info["ip"]
    camera_type = camera_info["type"] # 'entering' or 'sorting'

    camera = cv2.VideoCapture(camera_url+"/video", cv2.CAP_FFMPEG)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    
    process_this_frame = True

    while True:
        success, frame = camera.read()
        if not success:
            break

        if process_this_frame:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in current_face_encodings:
                name = "Inconnu"
                
                if KNOWN_ENCODINGS:
                    matches = face_recognition.compare_faces(KNOWN_ENCODINGS, face_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance(KNOWN_ENCODINGS, face_encoding)
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = KNOWN_NAMES[best_match_index]
                            
                            # --- LOGIQUE DE PRÉSENCE ---
                            now = datetime.now()
                            # Key by name + camera to allow logging same person on different cameras
                            log_key = f"{name}_{camera_id}"
                            last_seen = already_logged.get(log_key)

                            if last_seen is None or (now - last_seen).total_seconds() > 300:
                                attendance_doc = {
                                    "name": name,
                                    "camera_id": camera_id,
                                    "action": camera_type, # This will store 'entering' or 'sorting'
                                    "timestamp": now,
                                    "date": now.strftime("%Y-%m-%d"),
                                    "time": now.strftime("%H:%M:%S")
                                }
                                try:
                                    sessions_col.insert_one(attendance_doc)
                                    already_logged[log_key] = now
                                    print(f"Log: {name} {camera_type} via {camera_id}")
                                except Exception as e:
                                    print(f"Erreur DB: {e}")

        process_this_frame = not process_this_frame

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@router.get("/video_feed/{camera_id}")
def video_feed(camera_id: str):
    """
    Pass the camera ID in the URL to start the specific stream
    Example: /video_feed/front_door
    """
    return StreamingResponse(gen_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")