import os 
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2

router = APIRouter()

CAMERA_URL = os.environ.get("CAMERA_URL", "rtsp://username:password@ip_address:554/stream")

def gen_frames():
    camera = cv2.VideoCapture(CAMERA_URL, cv2.CAP_FFMPEG)
    
    # These flags help with "Premature End" errors
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 3)       
    process_this_frame = True

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Only process every other frame to save CPU
            if process_this_frame:
                # Logic: Trigger match_frame here 
                # (Ideally, use a background task or separate thread)
                pass
            
            process_this_frame = not process_this_frame

            # Encode for the web/mobile preview
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")