from fastapi import APIRouter, UploadFile, File, Form
from src.controllers.recognition_controller import (
    register_face_controller,
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