from fastapi import APIRouter
from src.services.camera_instance import camera_service
from fastapi.responses import StreamingResponse
import cv2
import io

router = APIRouter()

@router.get("/frame")
def get_frame():
    frame = camera_service.get_frame()

    if frame is None:
        return {"error": "no frame"}

    _, buffer = cv2.imencode(".jpg", frame)
    return StreamingResponse(
        io.BytesIO(buffer.tobytes()),
        media_type="image/jpeg"
    )
    

def generate():
    while True:
        frame = camera_service.get_frame()

        if frame is None:
            continue

        _, buffer = cv2.imencode(".jpg", frame)

        yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n")

@router.get("/live")
def live():
    return StreamingResponse(generate(),
        media_type="multipart/x-mixed-replace; boundary=frame")