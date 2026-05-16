import os
import cv2
import numpy as np
import face_recognition
import asyncio  # Added for async broadcast
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from src.core.mongo import get_collection
from src.services.websocket_service import manager

router = APIRouter()

# --- Configuration ---
UPLOAD_DIR = "uploads"
sessions_col = get_collection("sessions")
cameras_col = get_collection("cameras")
users_col = get_collection("users") 
already_logged = {} 

# --- Face Recognition Setup ---

def load_known_faces():
    known_encodings = []
    known_ids = [] 
    if not os.path.exists(UPLOAD_DIR):
        return known_encodings, known_ids
    
    for file in os.listdir(UPLOAD_DIR):
        if file.endswith(".npy"):
            user_id = file.replace(".npy", "")
            encoding = np.load(os.path.join(UPLOAD_DIR, file))
            known_encodings.append(encoding)
            known_ids.append(user_id)
    return known_encodings, known_ids

KNOWN_ENCODINGS, KNOWN_IDS = load_known_faces()

# --- Camera Management Routes ---

@router.post("/cameras")
def add_camera(camera_id: str, departement: str, ip: str, camera_type: str):
    if camera_type not in ["entering", "sorting"]:
        raise HTTPException(status_code=400, detail="Type must be 'entering' or 'sorting'")
    
    camera_doc = {
        "_id": camera_id, 
        "ip": ip, 
        "departement": departement,
        "type": camera_type,
        "created_at": datetime.now()
    }
    cameras_col.update_one({"_id": camera_id}, {"$set": camera_doc}, upsert=True)
    return {"message": f"Camera {camera_id} registered successfully"}

@router.get("/cameras")
def list_cameras():
    try:
        cameras = list(cameras_col.find())
        for cam in cameras:
            cam["id"] = str(cam["_id"])
            if "_id" in cam: del cam["_id"]
        return cameras
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Core Recognition Logic ---

def gen_frames(camera_id: str):
    camera_info = cameras_col.find_one({"_id": camera_id})
    if not camera_info:
        return

    camera_url = camera_info["ip"]
    camera_type = camera_info["type"] 

    cap = cv2.VideoCapture(camera_url + "/video", cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    process_this_frame = True

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            if process_this_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                current_face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in current_face_encodings:
                    if KNOWN_ENCODINGS:
                        matches = face_recognition.compare_faces(KNOWN_ENCODINGS, face_encoding, tolerance=0.5)
                        face_distances = face_recognition.face_distance(KNOWN_ENCODINGS, face_encoding)
                        
                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            
                            if matches[best_match_index]:
                                user_id_str = KNOWN_IDS[best_match_index]
                                now = datetime.now()
                                log_key = f"{user_id_str}_{camera_id}"
                                last_seen = already_logged.get(log_key)

                                if last_seen is None or (now - last_seen).total_seconds() > 300:
                                    attendance_doc = {
                                        "user_id": ObjectId(user_id_str),
                                        "camera_id": camera_id,
                                        "action": camera_type,
                                        "timestamp": now,
                                        "date": now.strftime("%Y-%m-%d"),
                                        "time": now.strftime("%H:%M:%S")
                                    }
                                    try:
                                        sessions_col.insert_one(attendance_doc)
                                        already_logged[log_key] = now
                                        
                                        # --- WEBSOCKET BROADCAST ---
                                        # We use this to push the data to the frontend immediately
                                        payload = {
                                            "user_id": user_id_str,
                                            "camera_id": camera_id,
                                            "action": camera_type,
                                            "time": attendance_doc["time"]
                                        }
                                        # Schedule the async broadcast in the running event loop
                                        asyncio.run_coroutine_threadsafe(manager.broadcast(payload), asyncio.get_event_loop())
                                        
                                        print(f"Logged & Broadcasted: User {user_id_str}")
                                    except Exception as e:
                                        print(f"Error: {e}")

            process_this_frame = not process_this_frame
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        cap.release()


@router.get("/video_feed/{camera_id}")
async def video_feed(camera_id: str):
    return StreamingResponse(gen_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Listening for client messages (or just keeping connection open)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)