from fastapi import APIRouter, UploadFile, File, Form,status
from src.controllers.recognition_controller import (
    register_face_controller,
    match_face_controller,
    remove_face_controller,
    match_face_controller
)

router = APIRouter(prefix="/faces", tags=["Face Recognition"])


@router.post("/register")
async def register(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    return await register_face_controller(name, file)


@router.post("/match")
async def match(file: UploadFile = File(...)):
    return await match_face_controller(file)

@router.post(
    "/match-v2", 
    status_code=status.HTTP_200_OK,
    summary="Match a face and log attendance",
    description="Upload an image file to match against known faces. If matched, records attendance into MongoDB."
)
async def match_face_route(
    file: UploadFile, 
    status_type: str = Form("late")
):
    """
    Route endpoint that forwards the file payload and attendance status 
    to the matching controller.
    """
    return await match_face_controller(file, status_type=status_type)
    
@router.delete("/remove")
async def remove(name: str):
    return await remove_face_controller(name)
