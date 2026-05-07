from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import os
from sqlalchemy import create_engine, text
from jwt import ExpiredSignatureError, InvalidTokenError

router = APIRouter()


def verify_token(token: str):
    secret_key = os.getenv('JWT_SECRET', 'my_secret_key')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


def get_tables_query(db_type: str):
    if db_type.startswith('mysql'):
        return 'SHOW TABLES'
    if db_type.startswith('postgresql'):
        return "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
    return None


@router.post('/tables')
async def show_tables(request: Request):
    try:
        data = await request.json()
    except:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Invalid JSON"}
        )

    token = data.get('TOKEN')
    if not token:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Missing TOKEN"}
        )

    try:
        payload = verify_token(token)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"CONECCION": "Error", "DETAIL": exc.detail}
        )

    db_type = payload.get('dbType', 'mysql+pymysql')
    db_host = payload.get('dbHost')
    db_user = payload.get('dbUser')
    db_pass = payload.get('dbPass')
    db_name = payload.get('dbName')

    if not all([db_host, db_user, db_pass, db_name]):
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Invalid token payload"}
        )

    query = get_tables_query(db_type)
    if query is None:
        return JSONResponse(
            status_code=400,
            content={"CONECCION": "Error", "DETAIL": "Unsupported dbType"}
        )

    try:
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}/{db_name}')
        with engine.connect() as conn:
            result = conn.execute(text(query))
            tables = [row[0] for row in result]

        return {"CONECCION": "Exitosa", "TABLES": tables}
    except Exception as e:
        return {"CONECCION": "Error", "DETAIL": str(e)}
