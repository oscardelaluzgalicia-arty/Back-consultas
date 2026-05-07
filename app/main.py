from fastapi import FastAPI
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from fastapi.responses import JSONResponse

app = FastAPI()

class VerifyRequest(BaseModel):
    dbType: str = "mysql+pymysql"
    dbHost: str
    dbUser: str
    dbPass: str
    dbName: str

@app.get("/")
def root():
    return {"status": "online"}

@app.post("/verify")
async def verify_connection(data: VerifyRequest):
    try:
        engine = create_engine(f"{data.dbType}://{data.dbUser}:{data.dbPass}@{data.dbHost}/{data.dbName}")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        secret_key = os.getenv('JWT_SECRET', 'my_secret_key')
        payload = {
            'dbType': data.dbType,
            'dbHost': data.dbHost,
            'dbUser': data.dbUser,
            'dbPass': data.dbPass,
            'dbName': data.dbName,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return {"CONECCION": "Exitosa", "TOKEN": token}
    except Exception:
        return JSONResponse(status_code=200, content={"CONECCION": "Error"})