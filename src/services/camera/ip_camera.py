import cv2
from .base import CameraStrategy

class IPCamera(CameraStrategy):

    def __init__(self, url: str):
        self.url = url
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.url)

        if not self.cap.isOpened():
            raise Exception(f"Cannot open IP camera: {self.url}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()