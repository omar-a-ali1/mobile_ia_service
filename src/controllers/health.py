import requests
import os
from sqlalchemy import text
from src.core.database import SessionLocal
from src.core.mongo import get_health
def check_database_connection():
    db = SessionLocal()
    try:
        # Note: In SQLAlchemy 2.0+, execute returns a result object
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print("DB ERROR:", e)
        return False
    finally:
        db.close()
        
def check_connect_with_express():
    try:
        response = requests.get("http://backend:5000/api/v1/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print("Express ERROR:", e)
        return False

def check_connect_with_mongodb():
    return get_health()
def health():
    status = {}
    
    status["database"] = "ok" if check_database_connection() else "down"
    status["express"] = "ok" if check_connect_with_express() else "down"
    status["mongoDb"] = "ok" if check_connect_with_mongodb else "down"
    
    return status