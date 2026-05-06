from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

app = FastAPI()

@app.post("/api/verify")
async def verify_connection(request: Request):
    try:
        data = await request.json()
    except:
        return JSONResponse(status_code=400, content={"CONECCION": "Error"})

    db_type = data.get('dbType', 'mysql+pymysql')
    db_host = data.get('dbHost')
    db_user = data.get('dbUser')
    db_pass = data.get('dbPass')
    db_name = data.get('dbName')

    if not all([db_host, db_user, db_pass, db_name]):
        return JSONResponse(status_code=400, content={"CONECCION": "Error"})

    try:
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}')
        
        # Verificar conexión con una query simple
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Generar token JWT con los datos de conexión
        secret_key = os.getenv('JWT_SECRET', 'my_secret_key')
        payload = {
            'dbType': db_type,
            'dbHost': db_host,
            'dbUser': db_user,
            'dbPass': db_pass,
            'dbName': db_name,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return {"CONECCION": "Exitosa", "TOKEN": token}
    except Exception as e:
        return {"CONECCION": "Error"}