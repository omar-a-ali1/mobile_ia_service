import os
from .usb_camera import USBCamera
from .ip_camera import IPCamera
from .file_camera import FileCamera


def create_camera():
    camera_type = os.getenv("CAMERA_TYPE", "ip")

    if camera_type == "usb":
        return USBCamera(index=0)

    elif camera_type == "ip":
        return IPCamera(os.getenv("CAMERA_URL"))

    elif camera_type == "file":
        return FileCamera(os.getenv("CAMERA_FILE"))

    else:
        raise Exception("Invalid CAMERA_TYPE")