import cv2
from .base import CameraStrategy

class FileCamera(CameraStrategy):

    def __init__(self, path: str):
        self.path = path
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.path)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()