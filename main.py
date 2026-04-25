import os
from fastapi import  FastAPI

from src.routes.base import router

from dotenv import load_dotenv
import uvicorn

load_dotenv()


app = FastAPI()


app.include_router(router)
if __name__ =="__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("APP_PORT", 8000)),
        log_level="info",
        reload=True,
    )
    