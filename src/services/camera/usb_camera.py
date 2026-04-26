import cv2
from .base import CameraStrategy

class USBCamera(CameraStrategy):

    def __init__(self, index=0):
        self.index = index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            raise Exception("USB camera not accessible")

    def get_frame(self):
        
        if not self.cap.isOpened():
            print("🔁 reopening camera...", flush=True)
            self.cap = cv2.VideoCapture(0)
    
        ret, frame = self.cap.read()
    
        if not ret:
            print("⚠️ failed frame read", flush=True)
            return None
    
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()