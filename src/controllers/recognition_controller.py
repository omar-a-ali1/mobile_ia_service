from fastapi import UploadFile
from src.services.face_db import register_face
from src.services.face_recognition_service import match_face
from src.utils.file_validation import validate_image_file


async def register_face_controller(name: str, file: UploadFile):
    is_valid, error = validate_image_file(file)

    if not is_valid:
        return {
            "status": "failed",
            "detail": error
        }

    result = await register_face(name, file)

    if "error" in result:
        return {
            "status": "failed",
            "detail": result["error"]
        }

    return {
        "status": "success",
        "message": result["message"]
    }


async def match_face_controller(file: UploadFile):
    is_valid, error = validate_image_file(file)

    if not is_valid:
        return {
            "status": "failed",
            "detail": error
        }

    return await match_face(file)