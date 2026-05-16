from fastapi import UploadFile
from fastapi import UploadFile, Form, HTTPException, status
import pymongo
from src.services.face_db import register_face
from src.services.face_recognition_service import match_face, remove_face_from_database
from src.utils.file_validation import validate_image_file
from src.services.rec_service import match_face_v2

async def register_face_controller(name: str, file: UploadFile):
    """
    Registers a new face in the database by name and image file.
    """
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
    """
    Matches a face in the given image file against the known encodings.
    """
    is_valid, error = validate_image_file(file)

    if not is_valid:
        return {
            "status": "failed",
            "detail": error
        }

    return await match_face(file)
    
async def remove_face_controller(name :str):
    """
    Removes a face from the database by name.
    """
    result = await remove_face_from_database(name)

    if not result:
        return {
            "status": "failed",
            "detail": "Face not found"
        }

    return {
        "status": "success",
        "message": f"{name} removed successfully"
    }

async def match_face_controller(file: UploadFile, status_type: str = Form("late")):
    """
    Validates the uploaded file and passes it along to the face matching service.
    Note: I changed the variable name to 'status_type' to avoid overriding Python's 
    built-in 'status' module imported from fastapi.
    """
    
    # 1. Execute your existing file validation logic
    is_valid, error = validate_image_file(file)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File validation failed: {error}"
        )

    # 2. Call the service logic from rec_service.py
    result = await match_face_v2(file, status=status_type)

    # 3. If the service returned an internal logic failure, catch it here
    if result.get("status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.get("detail", "Face processing failed")
        )

    # 4. Return the successful response back to the client router
    return result