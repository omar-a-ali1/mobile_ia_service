import time
import threading
from .camera.factory import create_camera
import cv2

class CameraService:

    def __init__(self):
        self.camera = create_camera()
        self.frame = None
        self.running = False
        self.thread = None

    def start(self):
        self.camera.start()
        self.running = True

        self.thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self.thread.start()

    def _loop(self):
        while self.running:
            frame = self.camera.get_frame()
    
            if frame is None:
                print("❌ no frame received", flush=True)
                time.sleep(0.1)
                continue
    
            self.frame = frame
            
            cv2.imshow("Camera Feed", frame)
            cv2.waitKey(1)
    
    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        self.camera.stop()
        