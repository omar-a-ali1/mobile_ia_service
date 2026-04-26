import cv2

class CameraService:
    def __init__(self, index=0):
        self.index = index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.index)

        if not self.cap.isOpened():
            raise Exception("Cannot access webcam")

    def get_frame(self):
        if not self.cap:
            raise Exception("Camera not started")

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def release(self):
        if self.cap:
            self.cap.release()