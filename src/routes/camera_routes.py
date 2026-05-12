import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.core.mongo import get_collection  # Import de votre utilitaire

router = APIRouter()

# --- Configuration ---
UPLOAD_DIR = "uploads"
sessions_col = get_collection("sessions")
already_logged = {} # Pour éviter d'enregistrer la même personne toutes les secondes

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

def gen_frames():
    # Lien vers votre caméra
    camera = cv2.VideoCapture("http://amr:amro@10.189.27.163:8080/video", cv2.CAP_FFMPEG)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    
    process_this_frame = True
    face_locations = []
    face_names = []

    while True:
        success, frame = camera.read()
        if not success:
            break

        if process_this_frame:
            # 1. Optimisation (x0.25)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # 2. Détection
            face_locations = face_recognition.face_locations(rgb_small_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in current_face_encodings:
                name = "Inconnu"
                
                if KNOWN_ENCODINGS:
                    matches = face_recognition.compare_faces(KNOWN_ENCODINGS, face_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance(KNOWN_ENCODINGS, face_encoding)
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = KNOWN_NAMES[best_match_index]
                            
                            # --- LOGIQUE DE PRÉSENCE SYNCHRONE ---
                            now = datetime.now()
                            # On n'enregistre qu'une fois toutes les 5 min (300s) pour éviter les doublons
                            last_seen = already_logged.get(name)
                            if last_seen is None or (now - last_seen).total_seconds() > 300:
                                attendance_doc = {
                                    "name": name,
                                    "timestamp": now,
                                    "date": now.strftime("%Y-%m-%d"),
                                    "time": now.strftime("%H:%M:%S")
                                }
                                # Insertion directe dans MongoDB
                                try:
                                    sessions_col.insert_one(attendance_doc)
                                    already_logged[name] = now
                                    print(f"Log: {name} présent")
                                except Exception as e:
                                    print(f"Erreur DB: {e}")
                
                face_names.append(name)

        process_this_frame = not process_this_frame

        # 3. Dessiner l'interface
        # for (top, right, bottom, left), name in zip(face_locations, face_names):
        #     top *= 4; right *= 4; bottom *= 4; left *= 4
        #     color = (0, 255, 0) if name != "Inconnu" else (0, 0, 255)
        #     cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        #     cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        # 4. Encodage
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@router.get("/video_feed")
def video_feed():
    # Note : On retire le 'async' devant def video_feed() pour être 100% synchrone
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")