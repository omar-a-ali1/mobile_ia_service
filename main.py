import os
from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.base import router
from dotenv import load_dotenv
import uvicorn

load_dotenv()

    
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")

if __name__ =="__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("APP_PORT", 8000)),
        log_level="info",
        reload=True,
    )
    